""" Assemblit web-application """

import os
import subprocess
import yaml
import copy
from typing import List, Literal, Union
from assemblit.app import apps
from pytensils import utils


# Assign private variable(s)
_APP_TYPES: List[str] = [
    'aaas',
    'wiki'
]


# Define parsing function(s)
def parse_app_type(
    config: dict
) -> str:
    """ Validates the web-application type and returns the web-application type as a `str`.

    Parameters
    ----------
    config : `dict`
        The web-application configuration.
    """

    # Check for the web-application types
    try:
        if 'type' not in [str(key).strip().lower() for key in dict(config['assemblit']).keys()]:
            raise MissingEnvironmentVariables()
    except ValueError:
        raise MissingEnvironmentVariables()

    # Parse the web-application type
    app_type: str = config['assemblit']['type']

    # Ensure that the web-application type is a valid supported type
    return validate_app_type(app_type=app_type)


def validate_app_type(
    app_type: str
) -> str:
    """ Validates the web-application type and returns the web-application type as a `str`.

    Parameters
    ----------
    app_type : `str`
        The web-application type.
    """

    # Ensure that the web-application type is a valid supported type
    if app_type.strip().lower() in [i.strip().lower() for i in _APP_TYPES]:
        return app_type.strip().lower()
    else:
        raise NotImplementedError(
            ''.join([
                'Invalid web-application type argument value {%s}.' % app_type,
                ' Currently, `assemblit` supports the following web-application types, [%s].' % (
                    ', '.join(["'%s'" % (i.strip().lower()) for i in _APP_TYPES])
                )
            ])
        )


def parse_app_environment(
    config: dict
) -> dict:
    """ Validates the web-application environment variables and returns the web-application
    environment variables as a `dict`.

    Parameters
    ----------
    config : `dict`
        The web-application configuration.
    """

    # Check for the web-application environment variables
    try:
        if 'env' not in [str(key).strip().lower() for key in dict(config['assemblit']).keys()]:
            raise MissingEnvironmentVariables()
    except ValueError:
        raise MissingEnvironmentVariables()

    # Parse config into dictionary object for keyword arguments
    env: dict = copy.deepcopy(config['assemblit']['env'])
    return {
        str(key).strip().upper(): value for key, value
        in env.items()
        if 'assemblit' in str(key).strip().lower()
    }


def parse_app_port(
    client_port: str,
    server_port: str | None = None
) -> str:
    """ Validates the web-application port. Returns the web-application port as a `str`
    if a valid web-application port is provided, otherwise raises a `ValueError` when the
    same port has been configured as both the `streamlit` client-port as well as the
    server-port and raises a `TypeError` when the port is not an
    integer as a string.

    Parameters
    ----------
    client_port : `str`
        The registered port address of the web-application.
    server_port : `str`
        The registered port address of the orchestration server.
    """

    # Ensure the web-application-port is an integer as a string
    try:
        client_port_int = utils.as_type(value=client_port, return_dtype='int')
    except TypeError:
        raise TypeError(
            ''.join([
                'Invalid web-application port argument value {%s}.',
                ' The web-application port value must be an integer as a string.' % (
                    client_port
                )
            ])
        )

    # Ensure the web-application-port is a valid port address number
    if (
        (client_port_int < 0)
        or (client_port_int > 65535)
    ):
        raise ValueError(
            ''.join([
                'Invalid web-application port argument value {%s}.' % (client_port),
                ' The web-application port value must be between 0 and 65535.'
            ])
        )

    # Ensure the web-application-port is unique and does not conflict with the server port
    if server_port:
        if client_port_int == utils.as_type(value=str(server_port), return_dtype='int'):
            raise ValueError(
                ''.join([
                    'Invalid web-application port argument value {%s}.' % (client_port),
                    ' The web-application port value cannot be the same as the `streamlit` web-application port.'
                ])
            )

    return str(client_port_int).strip().lower()


# Define abstracted web-application function(s)
def load_app_environment(
    dict_object: dict
):
    """ Sets environment variables and values.

    Parameters
    ----------
    dict_object : `dict`
        Dictionary object containing environment configuration parameters and values.
    """
    for key, value in dict_object.items():
        os.environ[key] = str(value)


def run(
    app_type: Literal['aaas', 'wiki'] | None,
    script: Union[str, os.PathLike]
):
    """ Runs a Python script.

    Parameters
    ----------
    app_type : `Literal['aaas', 'wiki']
        The type of `assemblit` web-application, either
        - `aaas` for a analytics-as-a-service web-application
        - 'wiki' for a python documentation web-application
    script : `str | os.PathLike`
        The relative or absolute path to a local Python script.
    """

    # Load the web-application configuration
    config = load_app_configuration(script=script)

    # Parse the web-application type
    if not app_type:
        app_type = parse_app_type(config=config)
    else:
        app_type = validate_app_type(app_type=app_type)

    # Parse the web-application environment variables
    app_environment = parse_app_environment(config=config)

    if app_type == 'aaas':

        # Initialize the analytics-as-a-service (AaaS) web-application
        app = apps.AaaS(**app_environment)

        # Validate the port-configuration settings
        app.ASSEMBLIT_CLIENT_PORT = parse_app_port(
            client_port=app.ASSEMBLIT_CLIENT_PORT,
            server_port=app.ASSEMBLIT_SERVER_PORT
        )

    if app_type == 'wiki':

        # Initialize the Python package documentation wiki-application
        app = apps.Wiki(**app_environment)

        # Validate the port-configuration settings
        app.ASSEMBLIT_CLIENT_PORT = parse_app_port(
            client_port=app.ASSEMBLIT_CLIENT_PORT
        )

    # Load the environment parameters
    load_app_environment(dict_object=app.to_dict())

    # Run the web-application
    subprocess.Popen(
        'streamlit run %s.py --server.port %s' % (
            app.ASSEMBLIT_HOME_PAGE_NAME,
            app.ASSEMBLIT_CLIENT_PORT
        ),
        shell=True
    ).wait()


# Define yaml-configuration function(s)
def load_app_configuration(
    script: Union[str, os.PathLike]
) -> dict:
    """ Loads the web-application configuration from '/.assemblit/config.yaml`.

    Parameters
    ----------
    script : `str | os.PathLike`
        The relative or absolute path to a local Python script.
    """

    # Infer the location of `config.yaml`
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(script)),
        '.assemblit',
        'config.yaml'
    )

    # Check for `config.yaml`
    if not os.path.isfile(config_path):
        raise MissingConfiguration()

    # Read `config.yaml`
    with open(config_path) as file:
        try:
            config: dict = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise e

    # Check for environment variables
    try:
        if 'assemblit' not in [str(key).strip().lower() for key in dict(config).keys()]:
            raise InvalidConfiguration()
    except ValueError:
        raise InvalidConfiguration()

    return config


# Define exceptions
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
