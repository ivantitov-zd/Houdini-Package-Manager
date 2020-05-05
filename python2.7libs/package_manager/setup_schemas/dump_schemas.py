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
                'value': '<package_root>'
            },
            {
                'name': 'QOTL',
                'value': '$QLIB/otls'
            }
        ],
        'hda_roots': [
            {
                'name': 'Base',
                'path': '$QOTL/base'
            },
            {
                'name': 'Future',
                'path': '$QOTL/future'
            },
            {
                'name': 'Experimental',
                'path': '$QOTL/experimental'
            },
            {
                'name': 'Graveyard',
                'path': '$QOTL/graveyard'
            }
        ]
    },
    'MOPS': {
        'name': 'MOPS',
        'author': 'Henry Foster',
        'env': [
            {
                'name': 'MOPS',
                'value': '<package_root>'
            }
        ]
    },
    'Redshift': {
        'name': 'Redshift',
        'root': '<package_root>/../$HOUDINI_VERSION',
        'env': [
            {
                'name': 'PATH',
                'value': '<package_root>/../../../bin'  # append
            }
        ]
    },
    'SideFX Labs': {
        'name': 'SideFX Labs',
        'author': 'SideFX',
        'env': [
            {
                'name': 'sidefxlabs_current_version',
                'value': 'MANUAL'
            },
            {
                'name': 'PATH',
                'value': '<package_root>/bin'
            }
        ]
    }
}

for name, schema in schemas.items():
    file_path = os.path.join(ROOT, name.replace(' ', '_') + '.schema')
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(schemas[name], file, indent=4)

'''
{
    "recommends": "houdini_version >= '17.5.321'",  # todo
}
'''
