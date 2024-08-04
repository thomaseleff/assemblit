""" Essential web-application settings """

import os
from typing import Union, List
from assemblit.app import layer


# Web-application configuration settings
if 'ASSEMBLIT_APP_TYPE' not in os.environ:
    raise layer.MissingEnvironmentVariables(
        ''.join([
            "Missing environment variables.",
            " `assemblit` requires environment variables to be provided within '/.assemblit/config.yaml'.",
            " In order to load the environment variables, run `assemblit run {app}.py`."
            " See https://www.assemblit.org/api/assemblit/setup."
        ])
    )

(
    # [required]

    # Developer configuration settings
    ENV,
    VERSION,
    DEBUG,

    # Web-app configuration settings
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
    SERVER_JOB_NAME,
    SERVER_JOB_ENTRYPOINT,
    SERVER_DEPLOYMENT_NAME,

    # Add'l Port configuration settings
    SERVER_PORT,

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
    job_name=os.environ.get('ASSEMBLIT_SERVER_JOB_NAME', None),
    job_entrypoint=os.environ.get('ASSEMBLIT_SERVER_JOB_ENTRYPOINT', None),
    deployment_name=os.environ.get('ASSEMBLIT_SERVER_DEPLOYMENT_NAME', None),
    server_port=os.environ.get('ASSEMBLIT_SERVER_PORT', None),
    users_db_name=os.environ.get('ASSEMBLIT_USERS_DB_NAME', None),
    users_db_query_index=os.environ.get('ASSEMBLIT_USERS_DB_QUERY_INDEX', None),
    sessions_db_name=os.environ.get('ASSEMBLIT_SESSIONS_DB_NAME', None),
    sessions_db_query_index=os.environ.get('ASSEMBLIT_SESSIONS_DB_QUERY_INDEX', None),
    data_db_name=os.environ.get('ASSEMBLIT_DATA_DB_NAME', None),
    data_db_query_index=os.environ.get('ASSEMBLIT_DATA_DB_QUERY_INDEX', None),
    analysis_db_name=os.environ.get('ASSEMBLIT_ANALYSIS_DB_NAME', None),
    analysis_db_query_index=os.environ.get('ASSEMBLIT_ANALYSIS_DB_QUERY_INDEX', None)
)

# # Developer configuration settings
# ENV: str = os.environ['ASSEMBLIT_ENV']
# VERSION: str = os.environ['ASSEMBLIT_VERSION']
# DEBUG: bool = utils.as_type(
#     os.environ['ASSEMBLIT_DEBUG'],
#     return_dtype='bool'
# )

# # Web-app configuration settings
# NAME: str = os.environ['ASSEMBLIT_NAME']
# HOME_PAGE_NAME: str = os.environ['ASSEMBLIT_HOME_PAGE_NAME']
# GITHUB_REPOSITORY_URL: str = os.environ['ASSEMBLIT_GITHUB_REPOSITORY_URL']
# GITHUB_BRANCH_NAME: str = os.environ['ASSEMBLIT_GITHUB_BRANCH_NAME']
# GITHUB_CONTENT_URL: str = 'https://raw.githubusercontent.com/%s/%s/' % (
#     up.urlparse(GITHUB_REPOSITORY_URL).path.lstrip('/'),
#     GITHUB_BRANCH_NAME.lstrip('/')
# )

# # Database configuration settings
# ROOT_DIR: Union[str, os.PathLike] = os.path.abspath(
#     os.environ['ASSEMBLIT_DIR']
# )
# DB_DIR: Union[str, os.PathLike] = os.path.abspath(
#     os.path.join(
#         os.environ['ASSEMBLIT_DIR'],
#         'db'
#     )
# )

# Layout settings
LAYOUT: str = 'wide'
INITIAL_SIDEBAR_STATE: str = 'expanded'
HEADER_COLUMNS: List[Union[int, float]] = [.05, .625, .1, .175, .05]
TAGLINE_COLUMNS: List[Union[int, float]] = [.05, .9, .05]
CONTENT_COLUMNS: List[Union[int, float]] = [.075, .875, .05]
INDENTED_CONTENT_COLUMNS: List[Union[int, float]] = [.1, .85, .05]

# # Session state defaults
# SESSION_STATE_DEFAULTS: dict = {
#     'dir': ROOT_DIR,
#     'pages': {
#         'home': '%s.py' % (HOME_PAGE_NAME)
#     }
# }

# # Authentication settings
# AUTH_NAME: str = 'auth'
# AUTH_QUERY_INDEX: str = 'authenticated'
# REQUIRE_AUTHENTICATION: bool = utils.as_type(
#     os.environ.get('ASSEMBLIT_REQUIRE_AUTHENTICATION', 'False'),
#     return_dtype='bool'
# )
# if REQUIRE_AUTHENTICATION:
#     AUTH_QUERY_INDEX_STATE: bool = False
# else:
#     AUTH_QUERY_INDEX_STATE: bool = True
# AUTH_DEFAULTS: dict = {
#     AUTH_QUERY_INDEX: AUTH_QUERY_INDEX_STATE,
#     'sign-up': False,
#     'login-error': False,
#     'sign-up-error': False
# }
# SESSION_STATE_DEFAULTS[AUTH_NAME] = copy.deepcopy(AUTH_DEFAULTS)

# # Users db settings
# USERS_DB_NAME: str = os.environ.get('ASSEMBLIT_USERS_DB_NAME', 'users')
# USERS_DB_QUERY_INDEX: str = os.environ.get('ASSEMBLIT_USERS_DB_QUERY_INDEX', 'user_id')
# if REQUIRE_AUTHENTICATION:
#     USERS_DB_QUERY_INDEX_VALUE: Union[str, None] = None
# else:
#     USERS_DB_QUERY_INDEX_VALUE: Union[str, None] = 'default'
# if USERS_DB_NAME:
#     USERS_DEFAULTS: dict = {
#         'name': None,
#         USERS_DB_QUERY_INDEX: USERS_DB_QUERY_INDEX_VALUE
#     }
#     SESSION_STATE_DEFAULTS[USERS_DB_NAME] = copy.deepcopy(USERS_DEFAULTS)

# # Sessions db settings
# SESSIONS_DB_NAME: str = os.environ.get('ASSEMBLIT_SESSIONS_DB_NAME', 'sessions')
# SESSIONS_DB_QUERY_INDEX: str = os.environ.get('ASSEMBLIT_SESSIONS_DB_QUERY_INDEX', 'session_id')
# if SESSIONS_DB_NAME:
#     SESSIONS_DEFAULTS: dict = {
#         'name': None,
#         SESSIONS_DB_QUERY_INDEX: None
#     }
#     SESSION_STATE_DEFAULTS[SESSIONS_DB_NAME] = copy.deepcopy(SESSIONS_DEFAULTS)

# # Data db settings
# DATA_DB_NAME: str = os.environ.get('ASSEMBLIT_DATA_DB_NAME', 'data')
# DATA_DB_QUERY_INDEX: str = os.environ.get('ASSEMBLIT_DATA_DB_QUERY_INDEX', 'dataset_id')
# if DATA_DB_NAME:
#     DATA_DEFAULTS: dict = {
#         'name': None,
#         DATA_DB_QUERY_INDEX: None
#     }
#     SESSION_STATE_DEFAULTS[DATA_DB_NAME] = copy.deepcopy(DATA_DEFAULTS)

# # Analysis db settings
# ANALYSIS_DB_NAME: str = os.environ.get('ASSEMBLIT_ANALYSIS_DB_NAME', 'analysis')
# ANALYSIS_DB_QUERY_INDEX: str = os.environ.get('ASSEMBLIT_ANALYSIS_DB_QUERY_INDEX', 'run_id')
# if ANALYSIS_DB_NAME:
#     ANALYSIS_DEFAULTS: dict = {
#         'name': None,
#         ANALYSIS_DB_QUERY_INDEX: None
#     }
#     SESSION_STATE_DEFAULTS[ANALYSIS_DB_NAME] = copy.deepcopy(ANALYSIS_DEFAULTS)
