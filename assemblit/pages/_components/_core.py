"""
Information
---------------------------------------------------------------------
Name        : _core.py
Location    : ~/pages/_components

Description
---------------------------------------------------------------------
Contains the core components for an assemblit web-application.
"""

import json
import copy
import streamlit as st
from assemblit import setup
from assemblit.auth import vault
from assemblit.app.structures import Setting


# Define generic initialization function(s)
def initialize_session_state_defaults():
    """
    Initializes the session state with the default setup parameter(s).
    """
    if setup.NAME not in st.session_state:
        st.session_state[setup.NAME] = {}
    for _, (key, value) in enumerate(
        setup.SESSION_STATE_DEFAULTS.items()
    ):
        if key not in st.session_state[setup.NAME]:
            st.session_state[setup.NAME][key] = copy.deepcopy(value)


def initialize_session_state_database_defaults(
    db_name: str,
    defaults: dict
):
    """
    Reset the session state with the default setup parameter(s) for a single database.

    Parameters
    ----------
    db_name : 'str'
        Name of the database.
    defaults : 'dict'
        Dictionary containing the database table default parameters.
    """
    if db_name in st.session_state[setup.NAME]:
        st.session_state[setup.NAME][db_name] = copy.deepcopy(defaults)


def initialize_session_state_status_defaults(
    db_name: str
):
    """
    Initializes the session state with the default setup parameter(s).

    Parameters
    ----------
    db_name : 'str'
        Name of the database.
    """
    if 'errors' not in st.session_state[setup.NAME][db_name]:
        st.session_state[setup.NAME][db_name]['errors'] = []
    if 'warnings' not in st.session_state[setup.NAME][db_name]:
        st.session_state[setup.NAME][db_name]['warnings'] = []
    if 'successes' not in st.session_state[setup.NAME][db_name]:
        st.session_state[setup.NAME][db_name]['successes'] = []


# Define generic content function(s)
def display_page_header(
    header: str = 'Welcome',
    tagline: str = 'Please login or sign-up.',
    headerless: bool = False,
    show_context: bool = False
):
    """ Displays the standard home-page header.

    Parameters
    ----------
    header : `str`
        String to display as the web-page header
    tagline : `str`
        String to display as the web-page tagline
    headerless : 'bool'
        'True' or 'False', determines whether to display the
            header content
    show_context : `bool`
        `True` or `False`, determines whether to display the
            session context information as an `st.popover` object.
    """

    # Configure
    st.set_page_config(
        layout=setup.LAYOUT,
        initial_sidebar_state=setup.INITIAL_SIDEBAR_STATE
    )

    # Force vertical scroll to avoid inconsistent auto-resizing
    #   when pages do not require vertical scroll
    st.markdown(
        """
            <style>
                .main {
                    overflow-y: scroll;
                }
            </style>
        """,
        unsafe_allow_html=True
    )

    # Display header & tagline
    if not headerless:

        # Layout columns
        _, col2, col3, col4, _ = st.columns(setup.HEADER_COLUMNS)

        # Display the header
        col2.markdown('# %s' % header)

        # Display context pop-over
        if show_context and st.session_state[setup.NAME][setup.SESSIONS_DB_NAME]['name']:
            col3.subheader('')
            with col3.popover(label='🔍', use_container_width=True):

                # Display subheader
                st.write('##### %s context' % (
                    ''.join([
                        setup.SESSIONS_DB_NAME[0].upper(),
                        setup.SESSIONS_DB_NAME[1:]
                    ])
                ))

                # Display pop-over content
                for setting in st.session_state[setup.NAME][setup.SESSIONS_DB_NAME][setup.SESSIONS_DB_NAME]['settings']:
                    setting: Setting

                    # Layout columns
                    col1, col2 = st.columns([.5, .5])

                    # Display context-parameters
                    col1.write('_%s_' % (setting.name))
                    col2.write('`%s`' % (setting.value))

        # # Display user pop-over
        # if st.session_state[setup.NAME][setup.USERS_DB_NAME]['name']:
        #     col4.subheader('')
        #     with col4.popover(label='👋'):

        #         # Display account information
        #         st.write(
        #             '##### Hello, %s' % (
        #                 st.session_state[setup.NAME][setup.USERS_DB_NAME]['name']
        #             )
        #         )

        #         # Layout columns
        #         col1, col2 = st.columns([.5, .5])

        # Display 'Logout' button
        if setup.REQUIRE_AUTHENTICATION:
            col4.subheader('')
            col4.button(
                label='Logout',
                on_click=vault.logout,
                type='secondary',
                use_container_width=True
            )

        # Layout columns
        _, col2, _ = st.columns(setup.TAGLINE_COLUMNS)

        # Display the tagline
        col2.markdown('%s' % tagline)

    # Debug
    if setup.DEBUG:
        print(
            json.dumps(
                st.session_state.to_dict(),
                indent=2,
                default=(
                    lambda o: f"Non-Serializable: <{type(o).__qualname__}>"
                )
            )
        )


def display_page_content_info(
    content_info: str
):
    """
    Displays the web-page content information.

    Parameters
    ----------
    content_info : `str`
        String to display as `streamlit.info()`.
    """

    # Layout columns
    _, col2, _ = st.columns(setup.CONTENT_COLUMNS)

    # Display info
    col2.info(content_info, icon='ℹ️')


def display_page_status(
    db_name: str
):
    """
    Displays the web-page status(es).

    Parameters
    ----------
    db_name : 'str'
        Name of the database.
    """

    # Layout columns
    _, col2, _ = st.columns(setup.CONTENT_COLUMNS)

    # Errors
    if st.session_state[setup.NAME][db_name]['errors']:
        for error in st.session_state[setup.NAME][db_name]['errors']:
            col2.error(
                body=error,
                icon='⛔'
            )

    # Reset session state
    st.session_state[setup.NAME][db_name]['errors'] = []

    # Warnings
    if st.session_state[setup.NAME][db_name]['warnings']:
        for warning in st.session_state[setup.NAME][db_name]['warnings']:
            col2.warning(
                body=warning,
                icon='⚠️'
            )

    # Reset session state
    st.session_state[setup.NAME][db_name]['warnings'] = []

    # Successes
    if st.session_state[setup.NAME][db_name]['successes']:
        for success in st.session_state[setup.NAME][db_name]['successes']:
            col2.success(
                body=success,
                icon='✅'
            )

    # Reset session state
    st.session_state[setup.NAME][db_name]['successes'] = []
