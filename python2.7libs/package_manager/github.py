import json
import os
import shutil
import tempfile
import zipfile
import time

import hou
import requests

from .package import isPackage, NotPackageError, Package
from .houdini_license import fullHoudiniLicenseName, HOUDINI_COMMERCIAL_LICENSE
from .choose_version_dialog import ChooseVersionDialog
from .version import Version


class RepoNotFound(Exception):
    pass


class CacheItem:
    __slots__ = 'data', 'last_modified'

    def __init__(self, data, last_modified=None):
        self.data = data
        self.last_modified = last_modified

    def toJson(self):
        return {
            'data': self.data,
            'last_modified': self.last_modified
        }

    @classmethod
    def fromJson(cls, data):
        return cls(data['data'], data['last_modified'])


class GitHubAPICache:
    cache_data = {}

    @staticmethod
    def get(url, headers=None, timeout=5):
        headers_data = {
            'User-Agent': 'Houdini-Package-Manager',
            'Accept': 'application / vnd.github.v3 + json'
        }
        if headers:
            headers_data.update(headers)

        GitHubAPICache.loadFromFile()

        if url in GitHubAPICache.cache_data:
            cached_item = GitHubAPICache.cache_data[url]
            headers_data['If-Modified-Since'] = cached_item.last_modified
        r = requests.get(url, headers=headers_data, timeout=timeout)
        if r.status_code == 200:
            data = json.loads(r.text)
            try:
                last_modified = r.headers['Last-Modified']
                GitHubAPICache.cache_data[url] = CacheItem(data, last_modified)
                GitHubAPICache.saveToFile()
            except KeyError:
                pass
            return data
        elif r.status_code == 304:
            return GitHubAPICache.cache_data[url].data
        elif r.status_code == 404:
            raise RepoNotFound  # Todo: explainable message

    @staticmethod
    def post(query):
        """Tests only, don't use in production"""
        headers = {'Authorization': 'Bearer 008d86db69e83cef0e1df1d2d3691b6efcc28be6'}
        r = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
        print(r.text)

    @staticmethod
    def toJson():
        return {url: item.toJson() for url, item in GitHubAPICache.cache_data.items()}

    @staticmethod
    def fromJson(data):
        for url, item_data in data.items():
            GitHubAPICache.cache_data[url] = CacheItem.fromJson(item_data)

    @staticmethod
    def saveToFile():
        file_path = hou.expandString('$HOUDINI_USER_PREF_DIR/package_manager.github_api_cache')
        with open(file_path, 'w') as file:
            json.dump(GitHubAPICache.toJson(), file)

    @staticmethod
    def loadFromFile():
        try:
            file_path = hou.expandString('$HOUDINI_USER_PREF_DIR/package_manager.github_api_cache')
            with open(file_path) as file:
                GitHubAPICache.fromJson(json.load(file))
        except IOError:
            pass

    @staticmethod
    def clear():
        GitHubAPICache.cache_data = {}
        GitHubAPICache.saveToFile()

    @staticmethod
    def cacheSize():
        raise NotImplementedError


class Release:
    def __init__(self, release_data):
        self.__data = release_data

    @property
    def version(self):
        return self.__data.get('tag_name')

    @property
    def name(self):
        return self.__data.get('name')

    @property
    def changes(self):
        return self.__data.get('body')

    @property
    def is_stable(self):
        return not self.__data.get('prerelease')

    @property
    def zip_archive_url(self):
        return self.__data.get('zipball_url')


def ownerAndRepoName(source):
    return source.strip('/').split('/')[-2:]


def repoURL(owner, repo_name):
    return 'https://github.com/{}/{}'.format(owner, repo_name)


def isPackageRepo(source):
    repo_owner, repo_name = ownerAndRepoName(source)
    api_repo_url = 'https://api.github.com/repos/{}/{}/contents/'.format(repo_owner, repo_name)
    repo_content = GitHubAPICache.get(api_repo_url)
    items = tuple(file_data['name'] for file_data in repo_content)
    return isPackage(items)


def extractRepoZip(file_path, repo_data, dst_location='$HOUDINI_USER_PREF_DIR'):
    package_name = repo_data.get('full_name', os.path.splitext(os.path.basename(file_path))[0])
    package_name = package_name.replace('/', '_')
    dst_location = os.path.join(hou.expandString(dst_location), package_name)
    if os.path.exists(dst_location):
        shutil.rmtree(dst_location)
    with zipfile.ZipFile(file_path) as file:
        repo_root_path = file.namelist()[0]
        for zip_data in file.infolist():
            if zip_data.filename[-1] == '/':
                continue
            zip_data.filename = zip_data.filename.replace(repo_root_path, '')
            file.extract(zip_data, dst_location)
    return dst_location


def ownerName(login):
    return GitHubAPICache.get('https://api.github.com/users/' + login).get('name', login)


def updatePackageDataFile(repo_data, web_package, package_location, version, version_type):
    data_file_path = os.path.join(package_location, 'package.setup')
    try:
        with open(data_file_path) as file:
            data = json.load(file)
    except (IOError, ValueError):
        data = {}
    if not data.get('name'):
        data['name'] = web_package.name or repo_data['name']
    if not data.get('description'):
        data['description'] = web_package.description or repo_data['description']
    if not data.get('author'):
        data['author'] = web_package.author or repo_data['owner']['login']
    if not data.get('source'):
        data['source'] = web_package.source or repo_data['full_name']
    if not data.get('source_type'):
        data['source_type'] = web_package.source_type or 'github'
    if not data.get('version'):
        data['version'] = version
        data['version_type'] = version_type
    if not data.get('hversion'):
        data['hversion'] = web_package.hversion or '*'
    if not data.get('hlicense'):
        data['hlicense'] = web_package.hlicense or fullHoudiniLicenseName(HOUDINI_COMMERCIAL_LICENSE)
    if not data.get('status'):
        data['status'] = web_package.status or 'Stable'
    with open(data_file_path, 'w') as file:
        json.dump(data, file, indent=4, encoding='utf-8')


def downloadRepoZipArchive(repo_data, version=None, dst_location='$TEMP'):
    repo_owner = repo_data['owner']['login']
    repo_name = repo_data['name']
    branch = repo_data.get('default_branch', 'master')
    zip_url = 'https://github.com/{}/{}/zipball/{}'.format(repo_owner, repo_name, version or branch)
    zip_file_path = os.path.join(hou.expandString(dst_location), repo_name + '.zip')
    with open(zip_file_path, 'wb') as file:
        r = requests.get(zip_url, timeout=5)
        file.write(r.content)  # Todo: sequentially
    return zip_file_path


def installFromGitHubRepo(web_package, dst_location='$HOUDINI_USER_PREF_DIR'):
    repo_owner, repo_name = ownerAndRepoName(web_package.source)
    api_repo_url = 'https://api.github.com/repos/{}/{}'.format(repo_owner, repo_name)
    repo_data = GitHubAPICache.get(api_repo_url)
    version = None
    api_releases_url = api_repo_url + '/releases'
    versions = []
    for release_data in GitHubAPICache.get(api_releases_url):
        if not release_data['prerelease']:
            versions.append(Version(release_data['tag_name']))
    if versions:
        version_type = 'version'
    else:
        version_type = 'time_github'
    if len(versions) == 1:
        version = versions[0].raw
    elif len(versions) > 1:
        version = ChooseVersionDialog.getVersion(hou.qt.mainWindow(), versions).raw
    zip_file = downloadRepoZipArchive(repo_data, version)
    package_location = extractRepoZip(zip_file, repo_data, dst_location)
    os.remove(zip_file)  # Todo: optional
    if len(versions) == 0:
        version = repo_data['pushed_at']
    updatePackageDataFile(repo_data, web_package, package_location, version, version_type)
    Package.install(package_location)


def checkUpdates():
    from .package import findInstalledPackages
    for package in findInstalledPackages():
        if package.source:
            pass
