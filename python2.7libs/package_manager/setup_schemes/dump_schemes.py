import os
import json

ROOT = os.path.dirname(__file__)

schemas = {
    'qLib': {
        '': ''
    },
    'Redshift': {
        '': ''
    }
}

for name, schema in schemas:
    file_path = os.path.join(ROOT, name + '.schema')
    with open(file_path, 'w') as file:
        json.dump(schemas[name], file)
