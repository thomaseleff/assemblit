""" Assemblit web-application """

import os
import subprocess
import copy
from typing import Union
from assemblit import app
from assemblit.orchestrator import layer
from pytensils import utils
from assemblit.toolkit import _config


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

    - `ENV`
    - `VERSION`
    - `DEBUG`
    - `NAME`
    - `HOME_PAGE_NAME`
    - `GITHUB_REPOSITORY_URL`
    - `GITHUB_BRANCH_NAME`
    - `ROOT_DIR`
    - `CLIENT_PORT`
    - `REQUIRE_AUTHENTICATION`
    - `DB_DIR`
    - `USERS_DB_NAME`
    - `USERS_DB_QUERY_INDEX`
    - `SESSIONS_DB_NAME`
    - `SESSIONS_DB_QUERY_INDEX`
    - `DATA_DB_NAME`
    - `DATA_DB_QUERY_INDEX`
    - `ANALYSIS_DB_NAME`
    - `ANALYSIS_DB_QUERY_INDEX`
    - `SESSION_STATE_DEFAULTS`
    - `AUTH_DEFAULTS`
    - `USERS_DEFAULTS`
    - `SESSIONS_DEFAULTS`
    - `DATA_DEFAULTS`
    - `ANALYSIS_DEFAULTS`
    """

    # Validate the web-application type
    app_type = _config.validate_type(env='app', type_=app_type, supported_types=app.__all__)

    if app_type == 'aaas':

        # Initialize the analytics-as-a-service (AaaS) web-application
        application = app.aaas.env(
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
        application.ASSEMBLIT_CLIENT_PORT = _config.validate_port(
            env='app',
            port=application.ASSEMBLIT_CLIENT_PORT
        )

        # Construct session-state defaults
        session_state_defaults = _construct_session_state_defaults(
            root_dir=application.ASSEMBLIT_DIR,
            home_page_name=application.ASSEMBLIT_HOME_PAGE_NAME
        )

        # Construct authentication settings
        session_state_defaults, auth_name, auth_query_index, auth_defaults = _construct_authentication_defaults(
            session_state_defaults=session_state_defaults,
            require_authentication=application.ASSEMBLIT_REQUIRE_AUTHENTICATION
        )

        # Construct user database settings
        if application.ASSEMBLIT_REQUIRE_AUTHENTICATION:
            users_db_query_index_value: Union[str, None] = None
        else:
            users_db_query_index_value: Union[str, None] = 'default'
        users_defaults: dict = {
            'name': None,
            application.ASSEMBLIT_USERS_DB_QUERY_INDEX: users_db_query_index_value
        }
        session_state_defaults[application.ASSEMBLIT_USERS_DB_NAME] = copy.deepcopy(users_defaults)

        # Construct sessions database settings
        sessions_defaults: dict = {
            'name': None,
            application.ASSEMBLIT_SESSIONS_DB_QUERY_INDEX: None
        }
        session_state_defaults[application.ASSEMBLIT_SESSIONS_DB_NAME] = copy.deepcopy(sessions_defaults)

        # Construct data database settings
        data_defaults: dict = {
            'name': None,
            application.ASSEMBLIT_DATA_DB_QUERY_INDEX: None
        }
        session_state_defaults[application.ASSEMBLIT_DATA_DB_NAME] = copy.deepcopy(data_defaults)

        # Construct analysis database settings
        analysis_defaults: dict = {
            'name': None,
            application.ASSEMBLIT_ANALYSIS_DB_QUERY_INDEX: None
        }
        session_state_defaults[application.ASSEMBLIT_ANALYSIS_DB_NAME] = copy.deepcopy(analysis_defaults)

        return (
            application.ASSEMBLIT_ENV,
            application.ASSEMBLIT_VERSION,
            application.ASSEMBLIT_DEBUG,
            application.ASSEMBLIT_NAME,
            application.ASSEMBLIT_HOME_PAGE_NAME,
            application.ASSEMBLIT_GITHUB_REPOSITORY_URL,
            application.ASSEMBLIT_GITHUB_BRANCH_NAME,
            application.ASSEMBLIT_DIR,
            application.ASSEMBLIT_CLIENT_PORT,
            auth_name,
            auth_query_index,
            application.ASSEMBLIT_REQUIRE_AUTHENTICATION,
            os.path.abspath(os.path.join(application.ASSEMBLIT_DIR, 'db')),
            application.ASSEMBLIT_USERS_DB_NAME,
            application.ASSEMBLIT_USERS_DB_QUERY_INDEX,
            application.ASSEMBLIT_SESSIONS_DB_NAME,
            application.ASSEMBLIT_SESSIONS_DB_QUERY_INDEX,
            application.ASSEMBLIT_DATA_DB_NAME,
            application.ASSEMBLIT_DATA_DB_QUERY_INDEX,
            application.ASSEMBLIT_ANALYSIS_DB_NAME,
            application.ASSEMBLIT_ANALYSIS_DB_QUERY_INDEX,
            session_state_defaults,
            auth_defaults,
            users_defaults,
            sessions_defaults,
            data_defaults,
            analysis_defaults,
        )

    if app_type == 'wiki':

        # Initialize the Python package documentation wiki-application
        application = app.wiki.env(
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
        application.ASSEMBLIT_CLIENT_PORT = _config.validate_port(
            env='app',
            port=application.ASSEMBLIT_CLIENT_PORT
        )

        # Construct session-state defaults
        session_state_defaults = _construct_session_state_defaults(
            root_dir=application.ASSEMBLIT_DIR,
            home_page_name=application.ASSEMBLIT_HOME_PAGE_NAME
        )

        # Construct authentication settings
        session_state_defaults, auth_name, auth_query_index, auth_defaults = _construct_authentication_defaults(
            session_state_defaults=session_state_defaults
        )

        return (
            application.ASSEMBLIT_ENV,
            application.ASSEMBLIT_VERSION,
            application.ASSEMBLIT_DEBUG,
            application.ASSEMBLIT_NAME,
            application.ASSEMBLIT_HOME_PAGE_NAME,
            application.ASSEMBLIT_GITHUB_REPOSITORY_URL,
            application.ASSEMBLIT_GITHUB_BRANCH_NAME,
            application.ASSEMBLIT_DIR,
            application.ASSEMBLIT_CLIENT_PORT,
            auth_name,
            auth_query_index,
            False,  # Require authentication
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


def create_app(
    config: dict
):
    """ Creates the web-application environment.

    Parameters
    ----------
    config : `dict`
        The `assemblit` configuration.
    """

    # Load the web-application type
    app_type = _config.load_type(config=config, env='app', supported_types=app.__all__)

    # Load the web-application environment variables
    app_environment_dict_object = _config.load_environment(config=config, env='app')

    if app_type == 'aaas':

        # Initialize the analytics-as-a-service (AaaS) web-application
        application = app.aaas.env(**app_environment_dict_object)

        # Validate the port-configuration settings
        application.ASSEMBLIT_CLIENT_PORT = _config.validate_port(
            env='app',
            port=application.ASSEMBLIT_CLIENT_PORT
        )

        # Create the orchestration server environment
        _ = layer.create_orchestrator(config=config)

    if app_type == 'wiki':

        # Initialize the Python package documentation wiki-application
        application = app.wiki.env(**app_environment_dict_object)

        # Validate the port-configuration settings
        application.ASSEMBLIT_CLIENT_PORT = _config.validate_port(
            env='app',
            port=application.ASSEMBLIT_CLIENT_PORT
        )

    # Load the environment parameters
    _config.create_environment(dict_object={'ASSEMBLIT_APP_TYPE': app_type, **application.to_dict()})

    return application


def run(
    script: Union[str, os.PathLike]
):
    """ Runs a Python script.

    Parameters
    ----------
    script : `str | os.PathLike`
        The relative or absolute path to a local Python script.
    """

    # Load the web-application configuration
    config = _config.load_configuration(path=os.path.dirname(os.path.abspath(script)))

    # Create the web-application environment
    application = create_app(config=config)

    # Run the web-application
    subprocess.Popen(
        'streamlit run %s --server.port %s' % (
            os.path.abspath(script),
            application.ASSEMBLIT_CLIENT_PORT
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
