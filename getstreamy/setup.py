"""
Information
---------------------------------------------------------------------
Name        : setup.py
Location    : ~/
Author      : Tom Eleff
Published   : 2024-02-21
Revised on  : .

Description
---------------------------------------------------------------------
Contains the generic static variables and methods for a getstreamy app.
"""

import os
import urllib.parse as up

# Developer mode
DEV = os.environ['DEV']

# Web-app configuration settings
NAME = os.environ['NAME']
HOME_PAGE_NAME = os.environ['HOME_PAGE_NAME']
GITHUB_REPOSITORY_URL = os.environ['GITHUB_REPOSITORY_URL']
GITHUB_BRANCH_NAME = os.environ['GITHUB_BRANCH_NAME']
GITHUB_CONTENT_URL = 'https://raw.githubusercontent.com/%s/%s' % (
    up.urlparse(GITHUB_REPOSITORY_URL).path.lstrip('/'),
    GITHUB_BRANCH_NAME.lstrip('/')
)

# Database configuration settings
ROOT_DIR = os.path.abspath(
    os.environ['DIR']
)
DB_DIR = os.path.abspath(
    os.path.join(
        os.environ['DIR'],
        'db'
    )
)

# Web-page configuration settings
LAYOUT = 'wide'
INITIAL_SIDEBAR_STATE = 'expanded'
HEADER_COLUMNS = [.05, .6375, .15, .15, .0125]
CONTENT_COLUMNS = [.075, .7625, .1625]

# Authentication settings
AUTH_NAME = 'auth'
AUTH_QUERY_INDEX = 'authenticated'
AUTH_DEFAULTS = {
    AUTH_QUERY_INDEX: False,
    'sign-up': False,
    'login-error': False,
    'sign-up-error': False
}

# Users db settings
USERS_DB_NAME = os.environ['USERS_DB_NAME']
USERS_DB_QUERY_INDEX = os.environ['USERS_DB_QUERY_INDEX']
USERS_DEFAULTS = {
    'name': None,
    USERS_DB_QUERY_INDEX: None
}

# Sessions db settings
SESSIONS_DB_NAME = os.environ['SESSIONS_DB_NAME']
SESSIONS_DB_QUERY_INDEX = os.environ['SESSIONS_DB_QUERY_INDEX']
SESSIONS_DEFAULTS = {
    'name': None,
    SESSIONS_DB_QUERY_INDEX: None
}

# Data db settings
DATA_DB_NAME = os.environ['DATA_DB_NAME']
DATA_DB_QUERY_INDEX = os.environ['DATA_DB_QUERY_INDEX']
DATA_DEFAULTS = {
    'name': None,
    DATA_DB_QUERY_INDEX: None
}

# Session state defaults
SESSION_STATE_DEFAULTS = {
    AUTH_NAME: AUTH_DEFAULTS,
    USERS_DB_NAME: USERS_DEFAULTS,
    SESSIONS_DB_NAME: SESSIONS_DEFAULTS,
    DATA_DB_NAME: DATA_DEFAULTS,
    'dir': ROOT_DIR,
    'pages': {
        'home': '%s.py' % (HOME_PAGE_NAME)
    }
}

# Db dependencies
USERS_DEPENDENTS = {}
SESSIONS_DEPENDENTS = {}
