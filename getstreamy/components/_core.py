"""
Information
---------------------------------------------------------------------
Name        : _core.py
Location    : ~/
Author      : Tom Eleff
Published   : 2024-02-13
Revised on  : .

Description
---------------------------------------------------------------------
Contains the generic methods for a gitstreamy web-application.
"""

import json
import copy
import streamlit as st
from getstreamy import setup, vault


# Define generic initialization function(s)
def initialize_session_state_defaults():
    """
    Initializes the session state with the default setup parameter(s).
    """
    if setup.NAME not in st.session_state:
        st.session_state[setup.NAME] = {}
        for index, (key, value) in enumerate(
            setup.SESSION_STATE_DEFAULTS.items()
        ):
            st.session_state[setup.NAME][key] = copy.deepcopy(value)


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
    headerless: bool = False
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

        with st.container():

            # Create class element for the header container
            st.markdown(
                """
                    <div class='fixed-header'/>
                    <style>
                        div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
                            position: sticky;
                            top: 2.875rem;
                            background-color: white;
                            z-index: 999;
                        }
                    </style>
                """,
                unsafe_allow_html=True
            )

            # Layout columns
            col1, col2, col3, col4, col5 = st.columns(setup.HEADER_COLUMNS)

            # Display the header
            col2.header(header)
            col2.write(tagline)
            col2.write('')
            col2.write('')

            # Display user name
            if st.session_state[setup.NAME][setup.USERS_DB_NAME][setup.USERS_DB_QUERY_INDEX]:
                col3.write('')
                col3.markdown(
                    "<p style='padding: 6px; text-align: right;'>%s %s</p>" % (
                        '👋',
                        st.session_state[setup.NAME][setup.USERS_DB_NAME]['name']
                    ),
                    unsafe_allow_html=True
                )

            # Display 'Logout' button
            col4.write('')
            col4.button(
                label='Logout',
                on_click=vault.logout,
                type='secondary',
                use_container_width=False
            )
            col4.write('')

    # Debug
    if setup.DEV:
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
    col1, col2, col3 = st.columns(setup.CONTENT_COLUMNS)

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
    col1, col2, col3 = st.columns(setup.CONTENT_COLUMNS)

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
