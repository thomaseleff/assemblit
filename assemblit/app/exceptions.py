""" Assemblit web-application exceptions """


class MissingConfiguration(FileNotFoundError):

    def __init__(self, *args, **kwargs):
        default_message = ''.join([
            "Missing configuration.",
            " `assemblit` requires web-application configuration to be provided within '/.assemblit/config.yaml'.",
            " See https://www.assemblit.org/api/assemblit/setup."
        ])

        if not args:
            args = (default_message,)

        super().__init__(*args, **kwargs)


class InvalidConfiguration(KeyError):

    def __init__(self, *args, **kwargs):
        default_message = ''.join([
            "Invalid configuration.",
            " `assemblit` requires environment variables to be provided within '/.assemblit/config.yaml'.",
            " See https://www.assemblit.org/api/assemblit/setup."
        ])

        if not args:
            args = (default_message,)

        super().__init__(*args, **kwargs)


class MissingEnvironmentVariables(KeyError):

    def __init__(self, *args, **kwargs):
        default_message = ''.join([
            "Missing environment variables.",
            " `assemblit` requires environment variables to be provided within '/.assemblit/config.yaml'.",
            " See https://www.assemblit.org/api/assemblit/setup."
        ])

        if not args:
            args = (default_message,)

        super().__init__(*args, **kwargs)
