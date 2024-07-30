""" Essential web-application settings """

import os
import copy
from typing import Union, List
import urllib.parse as up
from pytensils import utils


# Developer configuration settings
ENV: str = os.environ['ASSEMBLIT_ENV']
VERSION: str = os.environ['ASSEMBLIT_VERSION']
DEBUG: bool = utils.as_type(
    os.environ['ASSEMBLIT_DEBUG'],
    return_dtype='bool'
)

# Web-app configuration settings
NAME: str = os.environ['ASSEMBLIT_NAME']
HOME_PAGE_NAME: str = os.environ['ASSEMBLIT_HOME_PAGE_NAME']
GITHUB_REPOSITORY_URL: str = os.environ['ASSEMBLIT_GITHUB_REPOSITORY_URL']
GITHUB_BRANCH_NAME: str = os.environ['ASSEMBLIT_GITHUB_BRANCH_NAME']
GITHUB_CONTENT_URL: str = 'https://raw.githubusercontent.com/%s/%s/' % (
    up.urlparse(GITHUB_REPOSITORY_URL).path.lstrip('/'),
    GITHUB_BRANCH_NAME.lstrip('/')
)

# Database configuration settings
ROOT_DIR: Union[str, os.PathLike] = os.path.abspath(
    os.environ['ASSEMBLIT_DIR']
)
DB_DIR: Union[str, os.PathLike] = os.path.abspath(
    os.path.join(
        os.environ['ASSEMBLIT_DIR'],
        'db'
    )
)

# Web-page configuration settings
LAYOUT: str = 'wide'
INITIAL_SIDEBAR_STATE: str = 'expanded'
HEADER_COLUMNS: List[Union[int, float]] = [.05, .625, .1, .175, .05]
TAGLINE_COLUMNS: List[Union[int, float]] = [.05, .9, .05]
CONTENT_COLUMNS: List[Union[int, float]] = [.075, .875, .05]
METHODS_COLUMNS: List[Union[int, float]] = [.1, .85, .05]

# Session state defaults
SESSION_STATE_DEFAULTS: dict = {
    'dir': ROOT_DIR,
    'pages': {
        'home': '%s.py' % (HOME_PAGE_NAME)
    }
}

# Authentication settings
AUTH_NAME: str = 'auth'
AUTH_QUERY_INDEX: str = 'authenticated'
REQUIRE_AUTHENTICATION: bool = utils.as_type(
    os.environ.get('ASSEMBLIT_REQUIRE_AUTHENTICATION', 'False'),
    return_dtype='bool'
)
if REQUIRE_AUTHENTICATION:
    AUTH_QUERY_INDEX_STATE: bool = False
else:
    AUTH_QUERY_INDEX_STATE: bool = True
AUTH_DEFAULTS: dict = {
    AUTH_QUERY_INDEX: AUTH_QUERY_INDEX_STATE,
    'sign-up': False,
    'login-error': False,
    'sign-up-error': False
}
SESSION_STATE_DEFAULTS[AUTH_NAME] = copy.deepcopy(AUTH_DEFAULTS)

# Users db settings
USERS_DB_NAME: str = os.environ.get('ASSEMBLIT_USERS_DB_NAME', 'users')
USERS_DB_QUERY_INDEX: str = os.environ.get('ASSEMBLIT_USERS_DB_QUERY_INDEX', 'user_id')
if REQUIRE_AUTHENTICATION:
    USERS_DB_QUERY_INDEX_VALUE: Union[str, None] = None
else:
    USERS_DB_QUERY_INDEX_VALUE: Union[str, None] = 'default'
if USERS_DB_NAME:
    USERS_DEFAULTS: dict = {
        'name': None,
        USERS_DB_QUERY_INDEX: USERS_DB_QUERY_INDEX_VALUE
    }
    SESSION_STATE_DEFAULTS[USERS_DB_NAME] = copy.deepcopy(USERS_DEFAULTS)

# Sessions db settings
SESSIONS_DB_NAME: str = os.environ.get('ASSEMBLIT_SESSIONS_DB_NAME', 'sessions')
SESSIONS_DB_QUERY_INDEX: str = os.environ.get('ASSEMBLIT_SESSIONS_DB_QUERY_INDEX', 'session_id')
if SESSIONS_DB_NAME:
    SESSIONS_DEFAULTS: dict = {
        'name': None,
        SESSIONS_DB_QUERY_INDEX: None
    }
    SESSION_STATE_DEFAULTS[SESSIONS_DB_NAME] = copy.deepcopy(SESSIONS_DEFAULTS)

# Data db settings
DATA_DB_NAME: str = os.environ.get('ASSEMBLIT_DATA_DB_NAME', 'data')
DATA_DB_QUERY_INDEX: str = os.environ.get('ASSEMBLIT_DATA_DB_QUERY_INDEX', 'dataset_id')
if DATA_DB_NAME:
    DATA_DEFAULTS: dict = {
        'name': None,
        DATA_DB_QUERY_INDEX: None
    }
    SESSION_STATE_DEFAULTS[DATA_DB_NAME] = copy.deepcopy(DATA_DEFAULTS)

# Analysis db settings
ANALYSIS_DB_NAME: str = os.environ.get('ASSEMBLIT_ANALYSIS_DB_NAME', 'analysis')
ANALYSIS_DB_QUERY_INDEX: str = os.environ.get('ASSEMBLIT_ANALYSIS_DB_QUERY_INDEX', 'run_id')
if ANALYSIS_DB_NAME:
    ANALYSIS_DEFAULTS: dict = {
        'name': None,
        ANALYSIS_DB_QUERY_INDEX: None
    }
    SESSION_STATE_DEFAULTS[ANALYSIS_DB_NAME] = copy.deepcopy(ANALYSIS_DEFAULTS)
