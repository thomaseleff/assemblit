""" Configuration utility """

import os
import copy
import yaml
from typing import Union
from pytensils import utils
from assemblit.toolkit import _exceptions


def load_configuration(
    path: Union[str, os.PathLike]
) -> dict:
    """ Loads the `assemblit` configuration from '/.assemblit/config.yaml`.

    Parameters
    ----------
    path : `str` | `os.PathLike`
        The absolute path to the work-directory.
    """

    # Infer the location of `config.yaml`
    config_path = os.path.join(
        path,
        '.assemblit',
        'config.yaml'
    )

    # Check for `config.yaml`
    if not os.path.isfile(config_path):
        raise _exceptions.MissingConfiguration

    # Read `config.yaml`
    with open(config_path) as file:
        try:
            config: dict = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise e

    # Check for environment variables
    try:
        if 'assemblit' not in [str(key).strip().lower() for key in dict(config).keys()]:
            raise _exceptions.InvalidConfiguration
    except ValueError:
        raise _exceptions.InvalidConfiguration

    return config


def unload_configuration(
    path: Union[str, os.PathLike],
    config: dict
) -> dict:
    """ Unloads the `assemblit` configuration to '/.assemblit/config.yaml`.

    Parameters
    ----------
    path : `str` | `os.PathLike`
        The absolute path to the work-directory.
    config : `dict`
        The `assemblit` configuration.
    """

    # Infer the location of `config.yaml`
    config_path = os.path.join(
        path,
        '.assemblit',
        'config.yaml'
    )

    # Create output folder
    if not os.path.isdir(os.path.dirname(config_path)):
        utils.generate_output_directory(
            path=os.path.abspath(path),
            root='.assemblit'
        )

    # Unload (and replace) `config.yaml`
    with open(config_path, 'w') as file:
        try:
            yaml.dump(config, file, sort_keys=False, default_flow_style=False)
        except yaml.YAMLError as e:
            raise e


def load_environment(
    config: dict,
    env: str
) -> dict:
    """ Validates the orchestrator environment variables and returns the
    environment variables as a `dict`.

    Parameters
    ----------
    config : `dict`
        The `assemblit` configuration.
    env : `str`
        The environment in the configuration to load.
    """

    # Check for the server environment variables
    try:
        if 'env' not in [str(key).strip().lower() for key in dict(config['assemblit'][env]).keys()]:
            raise _exceptions.MissingEnvironmentVariables
    except (KeyError, ValueError):
        raise _exceptions.MissingEnvironmentVariables

    # Parse config into dictionary object for keyword arguments
    env: dict = copy.deepcopy(config['assemblit'][env]['env'])
    return {
        str(key).strip().upper(): value for key, value
        in env.items()
        if 'assemblit' in str(key).strip().lower()
    }


def load_type(
    config: dict,
    env: str,
    supported_types: list[str]
) -> str:
    """ Validates the web-application type and returns the web-application type as a `str`.

    Parameters
    ----------
    config : `dict`
        The web-application configuration.
    env : `str`
        The environment in the configuration to load.
    supported_types : `list[str]`
        The list of support types.
    """

    # Check for the web-application types
    try:
        if 'type' not in [str(key).strip().lower() for key in dict(config['assemblit'][env]).keys()]:
            raise _exceptions.MissingEnvironmentVariables
    except (KeyError, ValueError):
        raise _exceptions.MissingEnvironmentVariables

    # Load the web-application type
    type_: str = config['assemblit'][env]['type']

    # Ensure that the web-application type is a valid supported type
    return validate_type(env=env, type_=type_, supported_types=supported_types)


def create_environment(
    dict_object: dict
):
    """ Creates environment variables and values.

    Parameters
    ----------
    dict_object : `dict`
        Dictionary object containing environment variables and values.
    """
    for key, value in dict_object.items():
        os.environ[key] = str(value)


# Define validation function(s)
def validate_type(
    env: str,
    type_: str,
    supported_types: list[str]
) -> str:
    """ Validates the type and returns the type as a `str` if a valid type is provided,
    otherwise raises an `assemblit.app.exceptions.InvalidConfiguration` error.

    Parameters
    ----------
    env : `str`
        The configuration environment.
    type_ : `str`
        The type to validate
    supported_types : `list[str]`
        The list of support types.
    """

    # Ensure that the web-application type is a valid supported type
    if type_.strip().lower() not in [i.strip().lower() for i in supported_types]:
        raise _exceptions.InvalidConfiguration(
            ''.join([
                'Invalid %s type value {%s}.' % (env, type_),
                ' Currently, `assemblit` supports the following types, [%s].' % (
                    ', '.join(["'%s'" % (i.strip().lower()) for i in supported_types])
                )
            ])
        )

    return type_.strip().lower()


def validate_port(
    env: str,
    port: str
) -> str:
    """ Validates a registered port address. Returns the port as a `str` if a valid
    port is provided, otherwise raises an `assemblit.exceptions.InvalidConfiguration`
    when the port is invalid or the port is not an integer as a string.

    Parameters
    ----------
    env : `str`
        The configuration environment.
    port : `str`
        The registered port address to validate.
    """

    # Ensure the web-application-port is an integer as a string
    try:
        port_int = utils.as_type(value=port, return_dtype='int')
    except TypeError:
        raise _exceptions.InvalidConfiguration(
            ''.join([
                'Invalid %s port value {%s}.' % (
                    env,
                    port
                ),
                ' The port value must be an integer as a string.'
            ])
        )

    # Ensure the web-application-port is a valid port address number
    if (
        (port_int < 0)
        or (port_int > 65535)
    ):
        raise _exceptions.InvalidConfiguration(
            ''.join([
                'Invalid %s port value {%s}.' % (env, port_int),
                ' The port value must be between 0 and 65535.'
            ])
        )

    return str(port_int).strip().lower()
