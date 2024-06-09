import json
import os


ROOT = os.path.dirname(__file__)

schemas = {
    'qLib': {
        'name': 'qLib',
        'author': 'qLab',
        'env': [
            {
                'name': 'QLIB',
                'value': '<package_root>',
            },
            {
                'name': 'QOTL',
                'value': '$QLIB/otls',
            },
        ],
        'hda_roots': [
            {
                'name': 'Base',
                'path': '$QOTL/base',
            },
            {
                'name': 'Future',
                'path': '$QOTL/future',
                'optional': True,
            },
            {
                'name': 'Experimental',
                'path': '$QOTL/experimental',
                'optional': True,
            },
            {
                'name': 'Graveyard',
                'path': '$QOTL/graveyard',
                'optional': True,
                'enabled': False,
            },
        ],
    },
    'MOPS': {
        'name': 'MOPS',
        'author': 'Henry Foster',
        'env': [
            {
                'name': 'MOPS',
                'value': '<package_root>',
            },
        ],
    },
    'Redshift': {
        'name': 'Redshift',
        'root': {
            'path': '<package_root>/../$HOUDINI_VERSION',
            'method': 'append',
        },
        'env': [
            {
                'name': 'PATH',
                'value': '<package_root>/../../../bin',
                'method': 'append',
            },
        ],
    },
    'SideFX Labs': {
        'name': 'SideFX Labs',
        'author': 'SideFX',
        'env': [
            {
                'name': 'sidefxlabs_current_version',
                'value': 'MANUAL',
            },
            {
                'name': 'PATH',
                'value': '<package_root>/bin',
            },
        ],
    },
}

for name, schema in schemas.items():
    file_path = os.path.join(ROOT, name.replace(' ', '_') + '.schema')
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(schema, file, indent=4)

'''
{
    "recommends": "houdini_version >= '17.5.321'",  # todo
}
'''
