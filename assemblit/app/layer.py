""" Assemblit web-application """

import os
import subprocess
import yaml
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
    app_type: str
) -> str:
    """ Validates the web-application type. Returns the web-application type as a `str`
    if a valid web-application type is provided, otherwise raises a `NotImplementedError`.

    Parameters
    ----------
    app_type : `str`
        The type of web-application.
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


def parse_app_port(
    client_port: str,
    server_port: str
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
        os.environ['.'.join(['ASSEMBLIT', key])] = value


def run(
    app_type: Literal['aaas', 'wiki'],
    file_path: Union[str, os.PathLike]
):
    """ Runs a Python script.

    Parameters
    ----------
    app_type : `Literal['aaas', 'wiki']
        The type of `assemblit` web-application, either
        - `aaas` for a analytics-as-a-service web-application
        - 'wiki' for a python documentation web-application
    file_path : `str | os.PathLike`
        The relative or absolute path to a local Python script.
    """

    # Parse
    app_type = parse_app_type(app_type=app_type)

    # Load the web-application configuration
    config = load_app_configuration(file_path=file_path)

    if app_type == 'aaas':

        # Initialize the analytics-as-a-service (AaaS) web-application
        app = apps.AAAS(**config)

        # Validate the port-configuration settings
        app.CLIENT_PORT = parse_app_port(client_port=app.CLIENT_PORT, server_port=app.SERVER_PORT)

    else:
        raise NotImplementedError(
            ''.join([
                'Invalid web-application type argument value {%s}.' % app_type,
                ' Currently, `assemblit` supports the following web-application types, [%s].' % (
                    ', '.join(["'%s'" % (i.strip().lower()) for i in _APP_TYPES])
                )
            ])
        )

    # Load the environment parameters
    load_app_environment(dict_object=app.to_dict())

    # Run the web-application
    subprocess.Popen(
        'streamlit run %s.py --server.port %s' % (
            app.HOME_PAGE_NAME,
            app.CLIENT_PORT
        ),
        shell=True
    )


# Define yaml-configuration function(s)
def load_app_configuration(
    file_path: Union[str, os.PathLike]
) -> dict:
    """ Loads the web-application configuration from '/.assemblit/config.yaml`.

    Parameters
    ----------
    file_path : `str | os.PathLike`
        The relative or absolute path to a local Python script.
    """

    # Infer the location of `config.yaml`
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(file_path)),
        '.assemblit',
        'config.yaml'
    )

    # Check for `config.yaml`
    if os.path.isfile(config_path):

        # Read `config.yaml`
        with open(config_path) as file:
            try:
                config = {
                    str(key).split('.')[1]: value
                    for key, value in dict(yaml.safe_load(file)).items()
                    if 'ASSEMBLIT' in key
                }
            except yaml.YAMLError as e:
                raise e

        return config

    else:
        raise KeyError(
            ''.join([
                "Missing environment variables.",
                " `assemblit` requires environment variables to be provided within '/.assemblit/config.yaml'.",
                " See https://www.assemblit.org/api/assemblit/setup."
            ])
        )
