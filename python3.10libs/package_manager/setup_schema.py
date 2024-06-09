import os
from operator import itemgetter

from .package import package_score


def dir_package_score(path: str) -> int:
    return package_score(os.listdir(path))


def find_package_root_path(path: str) -> str:
    paths = []
    scores = []
    for root, folders, files in os.walk(path):
        score = dir_package_score(root)
        if score > 0:
            paths.append(root)
            scores.append(score)
    if not paths:
        raise FileNotFoundError('No package found')
    return sorted(zip(paths, scores), key=itemgetter(1))[-1][0]


def find_digital_assets_roots(package_root_path: str) -> tuple[str, ...]:
    paths = []
    for root, folders, files in os.walk(package_root_path):
        if root.lower() == os.path.join(package_root_path, 'otls').lower():
            continue

        if os.path.basename(root) == 'backup':
            continue

        for file in files:
            if file.endswith(('.otl', '.otlnc', '.otllc',
                              '.hda', '.hdanc', '.hdalc')):
                paths.append(root)
                break
    return tuple(paths)


def make_setup_schema(path: str) -> dict:
    try:
        package_root_path = find_package_root_path(path)
    except FileNotFoundError:
        return
    package_root = package_root_path.replace(path, '').strip('\\/').replace('\\', '/')
    hda_roots = map(lambda p: p.replace(package_root_path, '').strip('\\/').replace('\\', '/'),
                    find_digital_assets_roots(package_root_path))
    schema = {
        'root': package_root,
        'hda_roots': tuple(hda_roots)
    }
    return schema
