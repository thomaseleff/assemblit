""" Assemblit web-application exceptions """

_DOCS_URL = 'https://www.assemblit.org/api/assemblit'


class MissingConfiguration(FileNotFoundError):
    """ Raises a missing configuration error."""

    def __init__(self, *args, **kwargs):
        default_message = ''.join([
            "Missing configuration.",
            " `assemblit` requires web-application configuration to be provided within '/.assemblit/config.yaml'.",
            " See %s." % (_DOCS_URL)
        ])

        if not args:
            args = (default_message,)

        super().__init__(*args, **kwargs)


class InvalidConfiguration(KeyError):
    """ Raises an invalid configuration error."""

    def __init__(self, *args, **kwargs):
        default_message = ''.join([
            "Invalid configuration.",
            " `assemblit` requires environment variables to be provided within '/.assemblit/config.yaml'.",
            " See %s." % (_DOCS_URL)
        ])

        if not args:
            args = (default_message,)

        super().__init__(*args, **kwargs)


class MissingEnvironmentVariables(KeyError):
    """ Raises a missing environment variables error."""

    def __init__(self, *args, **kwargs):
        default_message = ''.join([
            "Missing environment variables.",
            " `assemblit` requires environment variables to be provided within '/.assemblit/config.yaml'.",
            " See %s." % (_DOCS_URL)
        ])

        if not args:
            args = (default_message,)

        super().__init__(*args, **kwargs)


class CompatibilityError(ValueError):

    def __init__(
        self,
        app_type: str,
        page_name: str,
        compatible_app_types: list[str],
        *args,
        **kwargs
    ):
        """ Raises a web-page compatibility error.

        Parameters
        ----------
        app_type : `str`
            The type of web-application.
        page_name : `str`
            The name of the web-page.
        compatible_app_types : `list[str]`
            The list of compatible web-application types.
        """
        default_message = ''.join([
            "Incompatible app-type {%s} with {%s}." % (app_type, page_name),
            " {%s} is only compatible with app-type(s) [%s]." % (page_name, ', '.join(compatible_app_types))
        ])

        if not args:
            args = (default_message,)

        super().__init__(*args, **kwargs)