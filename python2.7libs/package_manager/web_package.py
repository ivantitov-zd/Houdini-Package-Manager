from __future__ import print_function

from .package import Package


class WebPackage(Package):
    def __init__(self, name=None, description=None, author=None, source=None, source_type=None,
                 hversion=None, hlicense=None, status=None, setup_schema=None):
        self.name = name
        self.description = description
        self.author = author

        self.source = source
        self.source_type = source_type

        self.hversion = hversion
        self.hlicense = hlicense

        self.status = status

        self.setup_schema = setup_schema
