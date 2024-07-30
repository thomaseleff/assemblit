""" Essential web-application settings """

import os
import copy
from typing import Union, List
import urllib.parse as up
from pytensils import utils


# Developer configuration settings
ENV: str = os.environ['ENV']
VERSION: str = os.environ['VERSION']
DEBUG: bool = utils.as_type(
    os.environ['DEBUG'],
    return_dtype='bool'
)

# Web-app configuration settings
NAME: str = os.environ['NAME']
HOME_PAGE_NAME: str = os.environ['HOME_PAGE_NAME']
GITHUB_REPOSITORY_URL: str = os.environ['GITHUB_REPOSITORY_URL']
GITHUB_BRANCH_NAME: str = os.environ['GITHUB_BRANCH_NAME']
GITHUB_CONTENT_URL: str = 'https://raw.githubusercontent.com/%s/%s/' % (
    up.urlparse(GITHUB_REPOSITORY_URL).path.lstrip('/'),
    GITHUB_BRANCH_NAME.lstrip('/')
)

# Database configuration settings
ROOT_DIR: Union[str, os.PathLike] = os.path.abspath(
    os.environ['DIR']
)
DB_DIR: Union[str, os.PathLike] = os.path.abspath(
    os.path.join(
        os.environ['DIR'],
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

# Authentication settings
AUTH_NAME: str = 'auth'
AUTH_QUERY_INDEX: str = 'authenticated'
REQUIRE_AUTHENTICATION: bool = utils.as_type(
    os.environ['REQUIRE_AUTHENTICATION'],
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

# Users db settings
USERS_DB_NAME: str = os.environ['USERS_DB_NAME']
USERS_DB_QUERY_INDEX: str = os.environ['USERS_DB_QUERY_INDEX']
if REQUIRE_AUTHENTICATION:
    USERS_DB_QUERY_INDEX_VALUE: Union[str, None] = None
else:
    USERS_DB_QUERY_INDEX_VALUE: Union[str, None] = 'default-no-auth-required'
USERS_DEFAULTS: dict = {
    'name': None,
    USERS_DB_QUERY_INDEX: USERS_DB_QUERY_INDEX_VALUE
}

# Sessions db settings
SESSIONS_DB_NAME: str = os.environ['SESSIONS_DB_NAME']
SESSIONS_DB_QUERY_INDEX: str = os.environ['SESSIONS_DB_QUERY_INDEX']
SESSIONS_DEFAULTS: dict = {
    'name': None,
    SESSIONS_DB_QUERY_INDEX: None
}

# Data db settings
DATA_DB_NAME: str = os.environ['DATA_DB_NAME']
DATA_DB_QUERY_INDEX: str = os.environ['DATA_DB_QUERY_INDEX']
DATA_DEFAULTS: dict = {
    'name': None,
    DATA_DB_QUERY_INDEX: None
}

# Analysis db settings
ANALYSIS_DB_NAME: str = os.environ['ANALYSIS_DB_NAME']
ANALYSIS_DB_QUERY_INDEX: str = os.environ['ANALYSIS_DB_QUERY_INDEX']
ANALYSIS_DEFAULTS: dict = {
    'name': None,
    ANALYSIS_DB_QUERY_INDEX: None
}

# Session state defaults
SESSION_STATE_DEFAULTS: dict = {
    AUTH_NAME: copy.deepcopy(AUTH_DEFAULTS),
    USERS_DB_NAME: copy.deepcopy(USERS_DEFAULTS),
    SESSIONS_DB_NAME: copy.deepcopy(SESSIONS_DEFAULTS),
    DATA_DB_NAME: copy.deepcopy(DATA_DEFAULTS),
    ANALYSIS_DB_NAME: copy.deepcopy(ANALYSIS_DEFAULTS),
    'dir': ROOT_DIR,
    'pages': {
        'home': '%s.py' % (HOME_PAGE_NAME)
    }
}
