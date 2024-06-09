from .package import Package


class WebPackage(Package):
    def __init__(
            self,
            name: str | None = None,
            description: str | None = None,
            author: str | None = None,
            source: str | None = None,
            source_type: str | None = None,
            hversion: str | None = None,
            hlicense: str | None = None,
            status: str | None = None,
            setup_schema: str | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.author = author

        self.source = source
        self.source_type = source_type

        self.hversion = hversion
        self.hlicense = hlicense

        self.status = status

        self.setup_schema = setup_schema
