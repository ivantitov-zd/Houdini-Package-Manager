class WebPackage:
    __slots__ = ('name', 'description', 'author', 'source', 'source_type',
                 'hversion', 'hlicense', 'status', 'setup_scheme')

    def __init__(self, name, description, author, source, source_type='github',
                 hversion='*', hlicense='commercial', status='stable', setup_scheme=None):
        self.name = name
        self.description = description
        self.author = author

        self.source = source
        self.source_type = source_type

        self.hversion = hversion
        self.hlicense = hlicense

        self.status = status

        self.setup_scheme = setup_scheme
