""" Essential web-application settings """

import os
from typing import Union, List
from assemblit.app import layer, exceptions


# Layout settings
LAYOUT: str = 'wide'
INITIAL_SIDEBAR_STATE: str = 'expanded'
HEADER_COLUMNS: List[Union[int, float]] = [.05, .625, .1, .175, .05]
TAGLINE_COLUMNS: List[Union[int, float]] = [.05, .9, .05]
CONTENT_COLUMNS: List[Union[int, float]] = [.075, .875, .05]
INDENTED_CONTENT_COLUMNS: List[Union[int, float]] = [.1, .85, .05]

# Validate web-application type
if 'ASSEMBLIT_APP_TYPE' not in os.environ:
    raise exceptions.MissingEnvironmentVariables(
        ''.join([
            "Missing environment variables.",
            " `assemblit` requires environment variables to be provided within '/.assemblit/config.yaml'.",
            " In order to load the environment variables, run `assemblit run {script}`."
            " See https://www.assemblit.org/api/assemblit/setup."
        ])
    )

# Web-application configuration settings
(
    # [required]

    # Developer configuration settings
    ENV,
    VERSION,
    DEBUG,

    # Web-app configuration settings
    TYPE,
    NAME,
    HOME_PAGE_NAME,
    GITHUB_REPOSITORY_URL,
    GITHUB_BRANCH_NAME,
    ROOT_DIR,
    CLIENT_PORT,

    # [optional]

    # Authentication settings
    AUTH_NAME,
    AUTH_QUERY_INDEX,
    REQUIRE_AUTHENTICATION,

    # Orchestration server configuration settings
    # SERVER_JOB_NAME,
    # SERVER_JOB_ENTRYPOINT,
    # SERVER_DEPLOYMENT_NAME,

    # Add'l Port configuration settings
    # SERVER_PORT,

    # Db settings
    DB_DIR,

    # Users db settings
    USERS_DB_NAME,
    USERS_DB_QUERY_INDEX,

    # Sessions db settings
    SESSIONS_DB_NAME,
    SESSIONS_DB_QUERY_INDEX,

    # Data db settings
    DATA_DB_NAME,
    DATA_DB_QUERY_INDEX,

    # Analysis db settings
    ANALYSIS_DB_NAME,
    ANALYSIS_DB_QUERY_INDEX,

    # Defaults
    SESSION_STATE_DEFAULTS,
    AUTH_DEFAULTS,
    USERS_DEFAULTS,
    SESSIONS_DEFAULTS,
    DATA_DEFAULTS,
    ANALYSIS_DEFAULTS
) = layer.load_app_environment(

    # [required]
    app_type=os.environ['ASSEMBLIT_APP_TYPE'],
    env=os.environ['ASSEMBLIT_ENV'],
    version=os.environ['ASSEMBLIT_VERSION'],
    debug=os.environ['ASSEMBLIT_DEBUG'],
    name=os.environ['ASSEMBLIT_NAME'],
    home_page_name=os.environ['ASSEMBLIT_HOME_PAGE_NAME'],
    github_repository_url=os.environ['ASSEMBLIT_GITHUB_REPOSITORY_URL'],
    github_branch_name=os.environ['ASSEMBLIT_GITHUB_BRANCH_NAME'],
    root_dir=os.path.abspath(os.environ['ASSEMBLIT_DIR']),
    client_port=os.environ['ASSEMBLIT_CLIENT_PORT'],

    # [optional]
    require_authentication=os.environ.get('ASSEMBLIT_REQUIRE_AUTHENTICATION', None),
    # job_name=os.environ.get('ASSEMBLIT_SERVER_JOB_NAME', None),
    # job_entrypoint=os.environ.get('ASSEMBLIT_SERVER_JOB_ENTRYPOINT', None),
    # deployment_name=os.environ.get('ASSEMBLIT_SERVER_DEPLOYMENT_NAME', None),
    # server_port=os.environ.get('ASSEMBLIT_SERVER_PORT', None),
    users_db_name=os.environ.get('ASSEMBLIT_USERS_DB_NAME', None),
    users_db_query_index=os.environ.get('ASSEMBLIT_USERS_DB_QUERY_INDEX', None),
    sessions_db_name=os.environ.get('ASSEMBLIT_SESSIONS_DB_NAME', None),
    sessions_db_query_index=os.environ.get('ASSEMBLIT_SESSIONS_DB_QUERY_INDEX', None),
    data_db_name=os.environ.get('ASSEMBLIT_DATA_DB_NAME', None),
    data_db_query_index=os.environ.get('ASSEMBLIT_DATA_DB_QUERY_INDEX', None),
    analysis_db_name=os.environ.get('ASSEMBLIT_ANALYSIS_DB_NAME', None),
    analysis_db_query_index=os.environ.get('ASSEMBLIT_ANALYSIS_DB_QUERY_INDEX', None)
)
