""" Contains the core components for an `assemblit` web-application """

from typing import Any, Literal, List, Union
import json
import copy
import streamlit as st
from assemblit import setup
from assemblit._auth import vault
from assemblit.blocks.structures import Setting


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


def set_page_config(
    header: str = 'Welcome',
    icon: Any = None,
    layout: Literal['centered', 'wide'] = setup.LAYOUT,
    initial_sidebar_state: Literal['auto', 'expanded', 'collapsed'] = setup.INITIAL_SIDEBAR_STATE
):
    """ Configures the web-page.

    Parameters
    ----------
    header : `str`
        String to display as the web-page header
    icon : `str`
        The page favicon. If `icon` is `None` (default), the favicon will be a monochrome Streamlit logo.
    layout : `Literal['centered', 'wide']`
        The page layout, either `centered` or `wide`.
    initial_sidebar_state: `Literal['auto', 'expanded', 'collapsed']`
        The initial state of the sidebar navigation, either `auto`, `expanded` or `collapsed`.
    """

    # Configure
    st.set_page_config(
        page_title='%s ― %s' % (header, setup.NAME),
        page_icon=icon,
        layout=layout,
        initial_sidebar_state=initial_sidebar_state,
    )

    # Force custom styling
    if not setup.DEBUG:
        st.html(
            """
                <style>

                    header[data-testid="stHeader"] {
                        display: none;
                    }

                    .main {
                        overflow-y: scroll;
                    }

                    div[data-testid="stAppViewBlockContainer"] {
                        padding: 3rem 1rem 10rem 1rem;
                    }

                    div[data-testid="stHorizontalBlock"] {
                        gap: 0.5rem;
                    }

                </style>
            """
        )
    else:
        st.html(
            """
                <style>

                    .main {
                        overflow-y: scroll;
                    }

                    div[data-testid="stAppViewBlockContainer"] {
                        padding: 3rem 1rem 10rem 1rem;
                    }

                    div[data-testid="stHorizontalBlock"] {
                        gap: 0.5rem;
                    }

                </style>
            """
        )

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


# Define generic content function(s)
def display_page_header(
    header: str = 'Welcome',
    tagline: str = 'Please login or sign-up.',
    context: Union[List[Setting], None] = None
):
    """ Displays the standard header.

    Parameters
    ----------
    header : `str`
        String to display as the web-page header
    tagline : `str`
        String to display as the web-page tagline
    context : `Union[List[Setting], None]`
        List of `assemblit.blocks.structures.Setting` objects to display as context.
    """

    # Layout columns
    _, col2, col3, col4 = st.columns([.01, .64, .175, .175])

    # Display the header
    col2.markdown('# %s' % header)
    col2.markdown(tagline, unsafe_allow_html=True)

    # Display the 'Logout' button
    if setup.REQUIRE_AUTHENTICATION:
        col4.button(
            label='Logout',
            on_click=vault.logout,
            type='secondary',
            use_container_width=True
        )

    # Display context
    if context:
        with col3.popover(label='🔍', use_container_width=True):
            st.write('##### %s context' % (setup.SESSIONS_DB_NAME.title()))

            # Display pop-over content
            for setting in context:
                setting: Setting

                # Layout columns
                col1, col2 = st.columns([.5, .5])

                # Display context-parameters
                col1.write('_%s_' % (setting.name))
                col2.write('`%s`' % (setting.value))


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
    _, col2 = st.columns(setup.CONTENT_COLUMNS)

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
    _, col2 = st.columns(setup.CONTENT_COLUMNS)

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
