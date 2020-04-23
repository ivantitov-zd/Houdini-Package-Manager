from __future__ import print_function

import json
import os
import shutil
import tempfile
import zipfile
import time
import datetime

import hou
import requests

from .local_package import isPackage, NotPackageError, LocalPackage
from .houdini_license import fullHoudiniLicenseName, HOUDINI_COMMERCIAL_LICENSE
from .version_dialog import VersionDialog
from .version import Version
from .web_package import WebPackage
from .package import Package


class RepoNotFound(Exception):
    pass


class ReachedAPILimit(Exception):
    pass


class CacheItem:
    __slots__ = 'data', 'etag', 'last_modified'

    def __init__(self, data, etag=None, last_modified=None):
        self.data = data
        self.etag = etag
        self.last_modified = last_modified

    def toJson(self):
        return {
            'data': self.data,
            'etag': self.etag,
            'last_modified': self.last_modified
        }

    @classmethod
    def fromJson(cls, data):
        return cls(data['data'], data.get('etag'), data.get('last_modified'))


class GitHubAPICache:
    cache_data = {}

    @staticmethod
    def get(url, headers=None, timeout=5):
        headers_data = {
            'User-Agent': 'Houdini-Package-Manager',
            'Accept': 'application / vnd.github.v3 + json',
            'Authorization': ('token ' +
                              '55993b807df3eb5541c6' +
                              'bcd439d69aa335fcda89')
        }
        if headers:
            headers_data.update(headers)

        try:
            GitHubAPICache.loadFromFile()
        except IOError:
            pass

        if url in GitHubAPICache.cache_data:
            cached_item = GitHubAPICache.cache_data[url]
            if cached_item.etag:
                headers_data['If-None-Match'] = cached_item.etag
            elif cached_item.last_modified:
                headers_data['If-Modified-Since'] = cached_item.last_modified

        r = requests.get(url, stream=True, headers=headers_data, timeout=timeout)

        if r.status_code == 200:
            data = json.loads(r.text)
            etag = r.headers.get('ETag')
            last_modified = r.headers.get('Last-Modified')
            GitHubAPICache.cache_data[url] = CacheItem(data, etag, last_modified)
            GitHubAPICache.saveToFile()
            return data
        elif r.status_code == 304:
            return GitHubAPICache.cache_data[url].data
        elif r.status_code == 403:
            raise ReachedAPILimit
        elif r.status_code == 404:
            raise RepoNotFound  # Todo: explainable message

    # @staticmethod
    # def post(query):
    #     """Test only, don't use in production"""
    #     headers = {'Authorization': 'Bearer 008d86db69e83cef0e1df1d2d3691b6efcc28be6'}
    #     r = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    #     print(r.text)

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
        file_path = hou.expandString('$HOUDINI_USER_PREF_DIR/package_manager.github_api_cache')
        with open(file_path) as file:
            GitHubAPICache.fromJson(json.load(file))

    @staticmethod
    def clear():
        GitHubAPICache.cache_data = {}
        GitHubAPICache.saveToFile()

    @staticmethod
    def cacheSize():
        raise NotImplementedError


# class Release:
#     def __init__(self, release_data):
#         self.__data = release_data
#
#     @property
#     def version(self):
#         return self.__data.get('tag_name')
#
#     @property
#     def name(self):
#         return self.__data.get('name')
#
#     @property
#     def changes(self):
#         return self.__data.get('body')
#
#     @property
#     def is_stable(self):
#         return not self.__data.get('prerelease')
#
#     @property
#     def zip_archive_url(self):
#         return self.__data.get('zipball_url')


def ownerAndRepoName(source):
    return source.strip('/').split('/')[-2:]


def repoURL(owner, repo_name):
    return 'https://github.com/{0}/{1}'.format(owner, repo_name)


def isPackageRepo(source):
    repo_owner, repo_name = ownerAndRepoName(source)
    api_repo_url = 'https://api.github.com/repos/{0}/{1}/contents'.format(repo_owner, repo_name)
    repo_content = GitHubAPICache.get(api_repo_url)
    items = tuple(file_data['name'] for file_data in repo_content)
    return isPackage(items)


def extractRepoZip(file_path, repo_data, dst_location='$HOUDINI_USER_PREF_DIR', dst_name=None):
    if not dst_name:
        _, extension = os.path.splitext(os.path.basename(file_path))
        dst_name = repo_data.get('full_name', extension)
        dst_name = dst_name.replace('/', '_')
    dst_location = os.path.join(hou.expandString(dst_location), dst_name)
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


def repoDescription(package_or_link):
    if isinstance(package_or_link, Package):
        repo_owner, repo_name = ownerAndRepoName(package_or_link.source)
    else:  # package_or_link is link
        repo_owner, repo_name = ownerAndRepoName(package_or_link)
    return GitHubAPICache.get('https://api.github.com/repos/{0}/{1}'.format(repo_owner, repo_name)).get('description')


def updatePackageDataFile(repo_data, package, package_location,
                          version, version_type, update=False):
    data_file_path = os.path.join(package_location, 'package.setup')
    try:
        with open(data_file_path) as file:
            data = json.load(file)
    except (IOError, ValueError):
        data = {}
    package = package or WebPackage()
    if not data.get('name') or update:
        data['name'] = package.name or repo_data['name']
    if not data.get('description') or update:
        data['description'] = package.description or repo_data['description']
    if not data.get('author') or update:
        data['author'] = package.author or repo_data['owner']['login']
    if not data.get('source') or update:
        data['source'] = package.source or repo_data['full_name']
    if not data.get('source_type'):
        data['source_type'] = package.source_type or 'github'
    if not data.get('version') or update:
        data['version'] = version
        data['version_type'] = version_type
    elif not data.get('version_type'):
        data['version_type'] = package.version_type
    if not data.get('hversion') or update:
        data['hversion'] = package.hversion or '*'
    if not data.get('hlicense'):
        data['hlicense'] = package.hlicense or \
                           fullHoudiniLicenseName(HOUDINI_COMMERCIAL_LICENSE)
    if not data.get('status') or update:
        data['status'] = package.status or 'Stable'
    if not data.get('setup_scheme') or update:
        data['setup_scheme'] = package.setup_scheme
    with open(data_file_path, 'w') as file:
        json.dump(data, file, indent=4, encoding='utf-8')


def downloadRepoZipArchive(repo_data, version=None, dst_location='$TEMP'):
    repo_owner = repo_data['owner']['login']
    repo_name = repo_data['name']
    branch = repo_data.get('default_branch', 'master')
    zip_url = 'https://github.com/{0}/{1}/zipball/{2}'.format(repo_owner, repo_name, version or branch)
    zip_file_path = os.path.join(hou.expandString(dst_location), repo_name + '.zip')
    with open(zip_file_path, 'wb') as file:
        r = requests.get(zip_url, timeout=5)
        file.write(r.content)  # Todo: sequentially
    return zip_file_path


def installFromRepo(package_or_link, dst_location='$HOUDINI_USER_PREF_DIR', update=False, only_stable=True):
    if isinstance(package_or_link, Package):
        package = package_or_link
        repo_owner, repo_name = ownerAndRepoName(package.source)
    else:  # package_or_link is link
        repo_owner, repo_name = ownerAndRepoName(package_or_link)
        package = None

    repo_api_url = 'https://api.github.com/repos/{0}/{1}'.format(repo_owner, repo_name)
    repo_data = GitHubAPICache.get(repo_api_url)

    version = None
    releases_api_url = repo_api_url + '/releases'
    versions = []
    for release_data in GitHubAPICache.get(releases_api_url):
        if only_stable and release_data['prerelease']:
            continue
        versions.append(Version(release_data['tag_name']))
    if versions:
        version_type = 'version'
    else:
        version_type = 'time_github'
    if len(versions) >= 1:
        if update:
            version = versions[0].raw
        else:
            try:
                version = VersionDialog.getVersion(hou.qt.mainWindow(), versions).raw
            except AttributeError:
                return False  # Cancelled

    zip_file = downloadRepoZipArchive(repo_data, version)
    if update:
        dst_location, dst_name = os.path.split(package.content_path)
        package_location = extractRepoZip(zip_file, repo_data, dst_location, dst_name)
    else:
        package_location = extractRepoZip(zip_file, repo_data, dst_location)
    os.remove(zip_file)
    if len(versions) == 0:
        version = repo_data['pushed_at']
    updatePackageDataFile(repo_data, package, package_location, version, version_type, update)
    LocalPackage.install(package_location, force_overwrite=update)
    return True


def parseTimestamp(timestamp_string):
    return datetime.datetime.strptime(timestamp_string, '%Y-%m-%dT%H:%M:%SZ')


def repoHasUpdate(link, version, version_type, only_stable=True):
    repo_owner, repo_name = ownerAndRepoName(link)

    repo_api_url = 'https://api.github.com/repos/{0}/{1}'.format(repo_owner, repo_name)
    if version_type == 'time_github':
        repo_data = GitHubAPICache.get(repo_api_url)
        latest_version = parseTimestamp(repo_data['pushed_at'])
        # Todo: support only_stable
    else:
        releases_api_url = repo_api_url + '/releases'
        releases_data = GitHubAPICache.get(releases_api_url)

        if not releases_data:
            return False

        if not isinstance(releases_data, list):
            return False

        release_index = 0
        if only_stable:
            for index, release_data in enumerate(releases_data):
                if not release_data['prerelease']:
                    release_index = index
                    break

        latest_version = Version(releases_data[release_index]['tag_name'])

    return latest_version > version
