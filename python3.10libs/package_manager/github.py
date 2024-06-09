import datetime
import json
import os
import shutil
import zipfile
from collections.abc import Iterable
from typing import Any

import hou
import requests
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from package_manager.package import is_package

from .houdini_license import HOUDINI_COMMERCIAL_LICENSE
from .houdini_license import full_houdini_license_name
from .local_package import LocalPackage
from .package import Package
from .version import Version
from .web_package import WebPackage


class RepoNotFoundError(IOError):
    pass


class ReachedAPILimitError(Exception):
    pass


class CacheItem:
    __slots__ = 'data', 'etag', 'last_modified'

    def __init__(self, data: Any, etag: str | None = None, last_modified: float | None = None):
        self.data = data
        self.etag = etag
        self.last_modified = last_modified

    def to_json(self) -> dict:
        return {
            'data': self.data,
            'etag': self.etag,
            'last_modified': self.last_modified,
        }

    @classmethod
    def from_json(cls, data: dict) -> 'CacheItem':
        return cls(data['data'], data.get('etag'), data.get('last_modified'))


class API:
    cache_data: dict[str, CacheItem] = {}

    @staticmethod
    def get(url: str, headers: dict | None = None, timeout: int | float = 5) -> dict:
        headers_data = {
            'User-Agent': 'Houdini-Package-Manager',
            'Accept': 'application / vnd.github.v3 + json',
            'Authorization': ('token '
                              '55993b807df3eb5541c6'
                              'bcd439d69aa335fcda89'),
        }
        if headers:
            headers_data.update(headers)

        try:
            API.load_from_file()
        except OSError:
            pass

        if url in API.cache_data:
            cached_item = API.cache_data[url]
            if cached_item.etag:
                headers_data['If-None-Match'] = cached_item.etag
            elif cached_item.last_modified:
                headers_data['If-Modified-Since'] = cached_item.last_modified

        response = requests.get(url, stream=True, headers=headers_data, timeout=timeout)

        if os.getenv('username') == 'MarkWilson':  # Debug only
            print(response.headers.get('X-RateLimit-Remaining'))

        if response.status_code == 200:
            data = json.loads(response.text)
            etag = response.headers.get('ETag')
            last_modified = response.headers.get('Last-Modified')
            API.cache_data[url] = CacheItem(data, etag, last_modified)
            API.save_to_file()
            return data
        elif response.status_code == 304:
            return API.cache_data[url].data
        elif response.status_code == 403:
            raise ReachedAPILimitError
        elif response.status_code == 404:
            raise RepoNotFoundError(url)  # TODO: explainable message

    @staticmethod
    def to_json() -> dict:
        return {url: item.to_json() for url, item in API.cache_data.items()}

    @staticmethod
    def from_json(data: dict) -> None:
        for url, item_data in data.items():
            API.cache_data[url] = CacheItem.from_json(item_data)

    @staticmethod
    def save_to_file() -> None:
        file_path = hou.expandString('$HOUDINI_USER_PREF_DIR/package_manager.github_api_cache')
        with open(file_path, 'w') as file:
            json.dump(API.to_json(), file)

    @staticmethod
    def load_from_file() -> None:
        file_path = hou.expandString('$HOUDINI_USER_PREF_DIR/package_manager.github_api_cache')
        with open(file_path) as file:
            API.from_json(json.load(file))

    @staticmethod
    def clear() -> None:
        API.cache_data = {}
        API.save_to_file()

    @staticmethod
    def cache_size() -> None:
        raise NotImplementedError


def owner_and_repo_name(source: str) -> list[str]:
    return source.strip('/').split('/')[-2:]


def repo_url(owner: str, repo_name: str) -> str:
    return f'https://github.com/{owner}/{repo_name}'


def is_package_repo(source: str) -> bool:
    repo_owner, repo_name = owner_and_repo_name(source)
    api_repo_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents'
    repo_content = API.get(api_repo_url)
    items = tuple(file_data['name'] for file_data in repo_content)
    return is_package(items)


def extract_repo_zip(
        file_path: str,
        repo_data: dict,
        dst_location: str = '$HOUDINI_USER_PREF_DIR',
        dst_name: str | None = None,
) -> str:
    if not dst_name:
        _, extension = os.path.splitext(os.path.basename(file_path))
        dst_name = repo_data.get('full_name', extension)
        dst_name = dst_name.replace('/', '__')
    dst_location = str(os.path.join(hou.expandString(dst_location),
                                    hou.expandString(dst_name)))
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


def owner_name(login: str) -> str:
    return API.get('https://api.github.com/users/' + login).get('name', login)


def repo_description(package_or_link: str | Package) -> str:
    if isinstance(package_or_link, Package):
        repo_owner, repo_name = owner_and_repo_name(package_or_link.source)
    else:  # package_or_link is link
        repo_owner, repo_name = owner_and_repo_name(package_or_link)
    return API.get(f'https://api.github.com/repos/{repo_owner}/{repo_name}').get('description')


def update_package_data_file(
        repo_data: str,
        package: WebPackage | None,
        package_location: str,
        version: str,
        version_type: str,
        update: bool = False,
) -> None:
    data_file_path = os.path.join(package_location, 'package.setup')
    try:
        with open(data_file_path) as file:
            data = json.load(file)
    except (OSError, ValueError):
        data = {}
    package = package or WebPackage()
    if not data.get('name') or update:
        data['name'] = package.name or repo_data['name'] or data.get('name')
    if not data.get('description') or update:
        data['description'] = package.description or repo_data['description'] or data.get('description')
    if not data.get('author') or update:
        data['author'] = package.author or repo_data['owner']['login'] or data.get('author')
    if not data.get('source') or update:
        data['source'] = package.source or repo_data['full_name'] or data.get('source')
    if not data.get('source_type'):
        data['source_type'] = package.source_type or 'github'
    # TODO: or Version(data['version']) < version  # consider type
    if update or not data.get('version') or not data.get('version_type'):
        data['version'] = version
        data['version_type'] = version_type
    if not data.get('hversion') or update:
        data['hversion'] = package.hversion or data.get('hversion') or '*'
    if not data.get('hlicense'):
        data['hlicense'] = package.hlicense or \
                           data.get('hlicense') or \
                           full_houdini_license_name(HOUDINI_COMMERCIAL_LICENSE)
    if not data.get('status') or update:
        data['status'] = package.status or data.get('status') or 'Stable'
    if not data.get('setup_schema') or update:
        data['setup_schema'] = package.setup_schema or data.get('setup_schema')
    with open(data_file_path, 'w') as file:
        json.dump(data, file, indent=4)


def download_file(url: str, dst_location: str = '$TEMP') -> str:
    zip_file_path = os.path.join(hou.expandString(dst_location), os.path.basename(url) + '.zip')
    with open(zip_file_path, 'wb') as file:
        response = requests.get(url, timeout=5)
        file.write(response.content)  # TODO: sequentially
    return zip_file_path


class PickReleaseDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super(PickReleaseDialog, self).__init__(parent)

        self.setWindowTitle('Choose release')

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        form_layout = QFormLayout()
        main_layout.addLayout(form_layout)
        # form_layout.setContentsMargins(4, 4, 4, 4)
        # form_layout.setSpacing(4)

        self.release_combo = QComboBox()
        form_layout.addRow('Release', self.release_combo)

        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout)

        ok_button = QPushButton('OK')
        ok_button.clicked.connect(self._on_ok)
        buttons_layout.addWidget(ok_button)

        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        self.current_release = None

    def _on_ok(self) -> None:
        self.current_release = self.release_combo.currentData(Qt.UserRole)
        self.accept()

    def _set_release_list(self, releases: Iterable[dict]) -> None:
        self.release_combo.clear()
        for release_data in releases:
            self.release_combo.addItem(release_data['tag_name'], release_data)

    @classmethod
    def get_release(cls, releases, parent=None):
        window = cls(parent)
        window._set_release_list(releases)
        window.exec_()
        return window.current_release


class PickAssetDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super(PickAssetDialog, self).__init__(parent)

        self.setWindowTitle('Choose asset')

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        form_layout = QFormLayout()
        main_layout.addLayout(form_layout)
        # form_layout.setContentsMargins(4, 4, 4, 4)
        # form_layout.setSpacing(4)

        self.asset_combo = QComboBox()
        form_layout.addRow('Asset', self.asset_combo)

        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout)

        ok_button = QPushButton('OK')
        ok_button.clicked.connect(self._on_ok)
        buttons_layout.addWidget(ok_button)

        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        self.current_asset = None

    def _on_ok(self) -> None:
        self.current_asset = self.asset_combo.currentData(Qt.UserRole)
        self.accept()

    def _set_asset_list(self, assets) -> None:
        self.asset_combo.clear()
        for asset_data in assets:
            self.asset_combo.addItem(asset_data['name'], asset_data)
        self.asset_combo.addItem('Repo Archive', 'repo_archive')

    @classmethod
    def get_asset(cls, release_data, parent=None):
        window = cls(parent)
        window._set_asset_list(release_data['assets'])
        window.exec_()
        return window.current_asset


# def is_release_stable(release) -> bool:
#     raise NotImplementedError


def install_from_repo(
        package_or_link: str | Package,
        dst_location: str = '$HOUDINI_USER_PREF_DIR',
        update: bool = False,
        only_stable: bool = True,
        setup_schema=None,
) -> bool:
    if isinstance(package_or_link, Package):
        package = package_or_link
        repo_owner, repo_name = owner_and_repo_name(package.source)
    else:  # package_or_link is link
        repo_owner, repo_name = owner_and_repo_name(package_or_link)
        package = WebPackage()

    repo_api_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}'
    repo_data = API.get(repo_api_url)

    releases_api_url = repo_api_url + '/releases'
    releases = []
    for i in range(1, 4):  # Latest 90 releases (30 per page)
        releases.extend(API.get(releases_api_url + '?page=' + str(i)))

    suitable_releases = []
    for release_data in releases:
        if only_stable and release_data['prerelease'] or release_data.get('draft'):
            continue  # TODO: Check release type by version
        suitable_releases.append(release_data)

    if not suitable_releases:
        latest_release_api_url = repo_api_url + '/releases/latest'
        latest_release_data = API.get(latest_release_api_url)
        if 'tag_name' in latest_release_data:
            suitable_releases = latest_release_data,

    if suitable_releases:
        if len(suitable_releases) == 1 or update:
            release_data = suitable_releases[0]
        else:
            release_data = PickReleaseDialog.get_release(suitable_releases, hou.qt.mainWindow())
            if not release_data:
                return False  # Cancelled
        version_type = 'version'
        version = release_data['tag_name']

        if release_data['assets']:
            if len(release_data['assets']) == 1:
                asset_data = release_data['assets'][0]
            else:
                asset_data = PickAssetDialog.get_asset(release_data, hou.qt.mainWindow())

            if asset_data == 'repo_archive':
                asset_url = release_data['zipball_url']
            elif not asset_data:
                return False  # Cancelled
            else:
                asset_url = asset_data['browser_download_url']
        else:
            asset_url = release_data['zipball_url']
    else:
        version_type = 'time_github'
        version = repo_data['pushed_at']
        repo_owner = repo_data['owner']['login']
        repo_name = repo_data['name']
        branch = repo_data.get('default_branch', 'master')
        asset_url = f'https://github.com/{repo_owner}/{repo_name}/zipball/{branch}'

    zip_file = download_file(asset_url)
    if update:
        dst_location, dst_name = os.path.split(package.content_path)
        package_location = extract_repo_zip(zip_file, repo_data, dst_location, dst_name)
    else:
        package_location = extract_repo_zip(zip_file, repo_data, dst_location)
    os.remove(zip_file)

    update_package_data_file(repo_data, package, package_location, version, version_type, update)

    if not update:
        LocalPackage.install(package_location, setup_schema=package.setup_schema or setup_schema)
    return True


def parse_timestamp(timestamp_string: str) -> datetime:
    return datetime.datetime.strptime(timestamp_string, '%Y-%m-%dT%H:%M:%SZ')


def repo_has_update(
        link: str,
        version: str,
        version_type: str,
        only_stable: bool = True,
) -> bool:
    repo_owner, repo_name = owner_and_repo_name(link)

    repo_api_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}'
    if version_type == 'time_github':
        repo_data = API.get(repo_api_url)
        latest_version = parse_timestamp(repo_data['pushed_at'])
        version = parse_timestamp(version)
        # TODO: support only_stable
    else:  # version_type == 'version':
        if only_stable:
            latest_release_api_url = repo_api_url + '/releases/latest'
            try:
                release_data = API.get(latest_release_api_url)
            except RepoNotFoundError:
                return False
        else:
            releases_api_url = repo_api_url + '/releases'
            releases_data = API.get(releases_api_url)

            if not releases_data:
                return False

            if not isinstance(releases_data, list):
                return False

            release_data = releases_data[0]

        latest_version = Version(release_data['tag_name'])

    return latest_version > version
