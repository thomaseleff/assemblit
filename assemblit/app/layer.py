""" Assemblit web-application """

import os
import subprocess
import yaml
import copy
from typing import Literal, Union
from assemblit import app
from pytensils import utils


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
            raise MissingEnvironmentVariables
    except ValueError:
        raise MissingEnvironmentVariables

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
    if app_type.strip().lower() in [i.strip().lower() for i in app.__all__]:
        return app_type.strip().lower()
    else:
        raise NotImplementedError(
            ''.join([
                'Invalid web-application type argument value {%s}.' % app_type,
                ' Currently, `assemblit` supports the following web-application types, [%s].' % (
                    ', '.join(["'%s'" % (i.strip().lower()) for i in app.__all__])
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
            raise MissingEnvironmentVariables
    except ValueError:
        raise MissingEnvironmentVariables

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
    app_type: str,
    env: str,
    version: str,
    debug: bool,
    name: str,
    home_page_name: str,
    github_repository_url: str,
    github_branch_name: str,
    root_dir: Union[str, os.PathLike],
    client_port: Union[str] = '8501',
    require_authentication: Union[str, None] = 'False',
    # server_type: Union[str, None] = 'prefect',
    job_name: Union[str, None] = None,
    job_entrypoint: Union[str, None] = None,
    deployment_name: Union[str, None] = None,
    server_port: Union[str, None] = '4200',
    users_db_name: Union[str, None] = 'users',
    users_db_query_index: Union[str, None] = 'user_id',
    sessions_db_name: Union[str, None] = 'sessions',
    sessions_db_query_index: Union[str, None] = 'session_id',
    data_db_name: Union[str, None] = 'data',
    data_db_query_index: Union[str, None] = 'dataset_id',
    analysis_db_name: Union[str, None] = 'analysis',
    analysis_db_query_index: Union[str, None] = 'run_id'
) -> tuple[
        str,
        str,
        bool,
        str,
        str,
        str,
        str,
        str | os.PathLike,
        int,
        bool | None,
        str | None,
        str | None,
        str | None,
        int | None,
        str | os.PathLike | None,
        str | None,
        str | None,
        str | None,
        str | None,
        str | None,
        str | None,
        str | None,
        str | None,
        dict | None,
        dict | None,
        dict | None,
        dict | None,
        dict | None,
        dict | None
]:
    """ Loads and validates the orchestration server environment variables and returns the values in the following order,
    - ENV,
    - VERSION,
    - DEBUG,
    - NAME,
    - HOME_PAGE_NAME,
    - GITHUB_REPOSITORY_URL,
    - GITHUB_BRANCH_NAME,
    - ROOT_DIR,
    - CLIENT_PORT,
    - REQUIRE_AUTHENTICATION,
    - SERVER_JOB_NAME,
    - SERVER_JOB_ENTRYPOINT,
    - SERVER_DEPLOYMENT_NAME,
    - SERVER_PORT,
    - DB_DIR,
    - USERS_DB_NAME,
    - USERS_DB_QUERY_INDEX,
    - SESSIONS_DB_NAME,
    - SESSIONS_DB_QUERY_INDEX,
    - DATA_DB_NAME,
    - DATA_DB_QUERY_INDEX,
    - ANALYSIS_DB_NAME,
    - ANALYSIS_DB_QUERY_INDEX,
    - SESSION_STATE_DEFAULTS,
    - AUTH_DEFAULTS,
    - USERS_DEFAULTS,
    - SESSIONS_DEFAULTS,
    - DATA_DEFAULTS,
    - ANALYSIS_DEFAULTS
    """

    # Validate the web-application environment variables
    app_type = validate_app_type(app_type=app_type)

    if app_type == 'aaas':

        # Initialize the analytics-as-a-service (AaaS) web-application
        environment = app.aaas.env(
            ASSEMBLIT_ENV=env,
            ASSEMBLIT_VERSION=version,
            ASSEMBLIT_DEBUG=utils.as_type(debug, return_dtype='bool'),
            ASSEMBLIT_NAME=name,
            ASSEMBLIT_HOME_PAGE_NAME=home_page_name,
            ASSEMBLIT_GITHUB_REPOSITORY_URL=github_repository_url,
            ASSEMBLIT_GITHUB_BRANCH_NAME=github_branch_name,
            ASSEMBLIT_DIR=root_dir,
            ASSEMBLIT_CLIENT_PORT=utils.as_type(client_port, return_dtype='int'),
            ASSEMBLIT_REQUIRE_AUTHENTICATION=utils.as_type(require_authentication, return_dtype='bool'),
            ASSEMBLIT_SERVER_JOB_NAME=job_name,
            ASSEMBLIT_SERVER_JOB_ENTRYPOINT=job_entrypoint,
            ASSEMBLIT_SERVER_DEPLOYMENT_NAME=deployment_name,
            ASSEMBLIT_SERVER_PORT=utils.as_type(server_port, return_dtype='int'),
            ASSEMBLIT_USERS_DB_NAME=users_db_name,
            ASSEMBLIT_USERS_DB_QUERY_INDEX=users_db_query_index,
            ASSEMBLIT_SESSIONS_DB_NAME=sessions_db_name,
            ASSEMBLIT_SESSIONS_DB_QUERY_INDEX=sessions_db_query_index,
            ASSEMBLIT_DATA_DB_NAME=data_db_name,
            ASSEMBLIT_DATA_DB_QUERY_INDEX=data_db_query_index,
            ASSEMBLIT_ANALYSIS_DB_NAME=analysis_db_name,
            ASSEMBLIT_ANALYSIS_DB_QUERY_INDEX=analysis_db_query_index
        )

        # Validate the port-configuration settings
        environment.ASSEMBLIT_CLIENT_PORT = parse_app_port(
            client_port=environment.ASSEMBLIT_CLIENT_PORT,
            server_port=environment.ASSEMBLIT_SERVER_PORT
        )

        # Construct session-state defaults
        session_state_defaults = _construct_session_state_defaults(
            root_dir=environment.ASSEMBLIT_DIR,
            home_page_name=environment.ASSEMBLIT_HOME_PAGE_NAME
        )

        # Construct authentication settings
        session_state_defaults, auth_name, auth_query_index, auth_defaults = _construct_authentication_defaults(
            session_state_defaults=session_state_defaults,
            require_authentication=environment.ASSEMBLIT_REQUIRE_AUTHENTICATION
        )

        # Construct user database settings
        if environment.ASSEMBLIT_REQUIRE_AUTHENTICATION:
            users_db_query_index_value: Union[str, None] = None
        else:
            users_db_query_index_value: Union[str, None] = 'default'
        users_defaults: dict = {
            'name': None,
            environment.ASSEMBLIT_USERS_DB_QUERY_INDEX: users_db_query_index_value
        }
        session_state_defaults[environment.ASSEMBLIT_USERS_DB_NAME] = copy.deepcopy(users_defaults)

        # Construct sessions database settings
        sessions_defaults: dict = {
            'name': None,
            environment.ASSEMBLIT_SESSIONS_DB_QUERY_INDEX: None
        }
        session_state_defaults[environment.ASSEMBLIT_SESSIONS_DB_NAME] = copy.deepcopy(sessions_defaults)

        # Construct data database settings
        data_defaults: dict = {
            'name': None,
            environment.ASSEMBLIT_DATA_DB_QUERY_INDEX: None
        }
        session_state_defaults[environment.ASSEMBLIT_DATA_DB_NAME] = copy.deepcopy(data_defaults)

        # Construct analysis database settings
        analysis_defaults: dict = {
            'name': None,
            environment.ASSEMBLIT_ANALYSIS_DB_QUERY_INDEX: None
        }
        session_state_defaults[environment.ASSEMBLIT_ANALYSIS_DB_NAME] = copy.deepcopy(analysis_defaults)

        return (
            environment.ASSEMBLIT_ENV,
            environment.ASSEMBLIT_VERSION,
            environment.ASSEMBLIT_DEBUG,
            environment.ASSEMBLIT_NAME,
            environment.ASSEMBLIT_HOME_PAGE_NAME,
            environment.ASSEMBLIT_GITHUB_REPOSITORY_URL,
            environment.ASSEMBLIT_GITHUB_BRANCH_NAME,
            environment.ASSEMBLIT_DIR,
            environment.ASSEMBLIT_CLIENT_PORT,
            auth_name,
            auth_query_index,
            environment.ASSEMBLIT_REQUIRE_AUTHENTICATION,
            environment.ASSEMBLIT_SERVER_JOB_NAME,
            environment.ASSEMBLIT_SERVER_JOB_ENTRYPOINT,
            environment.ASSEMBLIT_SERVER_DEPLOYMENT_NAME,
            environment.ASSEMBLIT_SERVER_PORT,
            os.path.abspath(os.path.join(environment.ASSEMBLIT_DIR, 'db')),
            environment.ASSEMBLIT_USERS_DB_NAME,
            environment.ASSEMBLIT_USERS_DB_QUERY_INDEX,
            environment.ASSEMBLIT_SESSIONS_DB_NAME,
            environment.ASSEMBLIT_SESSIONS_DB_QUERY_INDEX,
            environment.ASSEMBLIT_DATA_DB_NAME,
            environment.ASSEMBLIT_DATA_DB_QUERY_INDEX,
            environment.ASSEMBLIT_ANALYSIS_DB_NAME,
            environment.ASSEMBLIT_ANALYSIS_DB_QUERY_INDEX,
            session_state_defaults,
            auth_defaults,
            users_defaults,
            sessions_defaults,
            data_defaults,
            analysis_defaults,
        )

    if app_type == 'wiki':

        # Initialize the Python package documentation wiki-application
        environment = app.wiki.env(
            ASSEMBLIT_ENV=env,
            ASSEMBLIT_VERSION=version,
            ASSEMBLIT_DEBUG=utils.as_type(debug, return_dtype='bool'),
            ASSEMBLIT_NAME=name,
            ASSEMBLIT_HOME_PAGE_NAME=home_page_name,
            ASSEMBLIT_GITHUB_REPOSITORY_URL=github_repository_url,
            ASSEMBLIT_GITHUB_BRANCH_NAME=github_branch_name,
            ASSEMBLIT_DIR=root_dir,
            ASSEMBLIT_CLIENT_PORT=utils.as_type(client_port, return_dtype='int'),
        )

        # Validate the port-configuration settings
        environment.ASSEMBLIT_CLIENT_PORT = parse_app_port(
            client_port=environment.ASSEMBLIT_CLIENT_PORT
        )

        # Construct session-state defaults
        session_state_defaults = _construct_session_state_defaults(
            root_dir=environment.ASSEMBLIT_DIR,
            home_page_name=environment.ASSEMBLIT_HOME_PAGE_NAME
        )

        # Construct authentication settings
        session_state_defaults, auth_name, auth_query_index, auth_defaults = _construct_authentication_defaults(
            session_state_defaults=session_state_defaults
        )

        return (
            environment.ASSEMBLIT_ENV,
            environment.ASSEMBLIT_VERSION,
            environment.ASSEMBLIT_DEBUG,
            environment.ASSEMBLIT_NAME,
            environment.ASSEMBLIT_HOME_PAGE_NAME,
            environment.ASSEMBLIT_GITHUB_REPOSITORY_URL,
            environment.ASSEMBLIT_GITHUB_BRANCH_NAME,
            environment.ASSEMBLIT_DIR,
            environment.ASSEMBLIT_CLIENT_PORT,
            auth_name,
            auth_query_index,
            False,  # Require authentication
            None,  # Server job name
            None,  # Server job entrypoint
            None,  # Server job deployment name
            None,  # Server port
            None,  # Database directory
            None,  # Users db name
            None,  # Users db query-index
            None,  # Sessions db name
            None,  # Users db query-index
            None,  # Data db name
            None,  # Data db query-index
            None,  # Analysis db name
            None,  # Analysis db query-index
            session_state_defaults,
            auth_defaults,
            None,  # Users db defaults
            None,  # Sessions db defaults
            None,  # Data db defaults
            None,  # Analysis db defaults
        )


def make_app_environment(
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
    environment_dict_object = parse_app_environment(config=config)

    if app_type == 'aaas':

        # Initialize the analytics-as-a-service (AaaS) web-application
        environment = app.aaas.env(**environment_dict_object)

        # Validate the port-configuration settings
        environment.ASSEMBLIT_CLIENT_PORT = parse_app_port(
            client_port=environment.ASSEMBLIT_CLIENT_PORT,
            server_port=environment.ASSEMBLIT_SERVER_PORT
        )

    if app_type == 'wiki':

        # Initialize the Python package documentation wiki-application
        environment = app.wiki.env(**environment_dict_object)

        # Validate the port-configuration settings
        environment.ASSEMBLIT_CLIENT_PORT = parse_app_port(
            client_port=environment.ASSEMBLIT_CLIENT_PORT
        )

    # Load the environment parameters
    make_app_environment(dict_object={'ASSEMBLIT_APP_TYPE': app_type, **environment.to_dict()})

    # Run the web-application
    subprocess.Popen(
        'streamlit run %s.py --server.port %s' % (
            environment.ASSEMBLIT_HOME_PAGE_NAME,
            environment.ASSEMBLIT_CLIENT_PORT
        ),
        shell=True
    ).wait()


# Define environment variable constructing functions
def _construct_session_state_defaults(
    root_dir: str,
    home_page_name: str
) -> dict:
    """ Constructs the session-state defaults from the environment variables. """
    return {
        'dir': root_dir,
        'pages': {
            'home': '%s.py' % (home_page_name)
        }
    }


def _construct_authentication_defaults(
    session_state_defaults: dict,
    require_authentication: bool = False
) -> tuple:
    """ Constructs the session-state defaults from the environment variables. """
    auth_name: str = 'auth'
    auth_query_index: str = 'authenticated'

    if require_authentication:
        auth_query_index_state: bool = False
    else:
        auth_query_index_state: bool = True
    auth_defaults: dict = {
        auth_query_index: auth_query_index_state,
        'sign-up': False,
        'login-error': False,
        'sign-up-error': False
    }
    session_state_defaults[auth_name] = copy.deepcopy(auth_defaults)

    return (session_state_defaults, auth_name, auth_query_index, auth_defaults)


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
        raise MissingConfiguration

    # Read `config.yaml`
    with open(config_path) as file:
        try:
            config: dict = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise e

    # Check for environment variables
    try:
        if 'assemblit' not in [str(key).strip().lower() for key in dict(config).keys()]:
            raise InvalidConfiguration
    except ValueError:
        raise InvalidConfiguration

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
