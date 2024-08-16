""" Page builder """

import os
import copy
import streamlit as st
from assemblit import setup
from assemblit.toolkit import _exceptions
from assemblit._database import sessions, analysis
from assemblit.pages._components import _core, _run_listing

_COMPATIBLE_APP_TYPES = ['aaas']


class Content():
    """ A `class` that contains the run listing-page content.

    Parameters
    ----------
    header : `str`
        String to display as the webpage header.
    tagline : `str`
        String to display as the webpage tagline.
    content_info : `str`
        String to display as `streamlit.info()` when there is no active session.
    headerless : `bool`
        `True` or `False`, determines whether to display the header & tagline.

    Examples
    --------

    ``` python

    # Constructing the run listing-page content

    from assemblit.pages import run_listing

    Listing = run_analysis.Content(
        header='Listing',
        tagline='Browse submitted analysis runs, review status and navigate to outputs.'
    )

    # Serving the run listing-page content

    Listing.serve()

    ```
    """

    def __init__(
        self,
        header: str = 'Listing',
        tagline: str = 'Browse submitted analysis runs, review status and navigate to outputs.',
        content_info: str = 'Navigate to the **scope-selector** page to load a session.',
        headerless: bool = False
    ):
        """ Initializes an instance of the run listing-page content.

        Parameters
        ----------
        header : `str`
            String to display as the webpage header.
        tagline : `str`
            String to display as the webpage tagline.
        content_info : `str`
            String to display as `streamlit.info()` when there is no active session.
        headerless : `bool`
            `True` or `False`, determines whether to display the header & tagline.
        """

        # Validate compatibility
        if setup.TYPE not in _COMPATIBLE_APP_TYPES:
            raise _exceptions.CompatibilityError(
                app_type=setup.TYPE,
                page_name=os.path.splitext(os.path.basename(__file__))[0],
                compatible_app_types=_COMPATIBLE_APP_TYPES
            )

        # Assign content class variables
        self.header = header
        self.tagline = tagline
        self.content_info = content_info
        self.headerless = headerless

        # Assign database class variables to set the scope for run listing
        self.scope_db_name = setup.SESSIONS_DB_NAME
        self.scope_query_index = setup.SESSIONS_DB_QUERY_INDEX

        # Assign database class variables
        self.db_name = setup.ANALYSIS_DB_NAME
        self.table_name = analysis.Schemas.analysis.name
        self.query_index = setup.ANALYSIS_DB_QUERY_INDEX

        # Initialize session state defaults
        _core.initialize_session_state_defaults()

        # Initialize session state status defaults
        _core.initialize_session_state_status_defaults(
            db_name=self.db_name
        )

    def serve(
        self
    ):
        """ Serves the run listing-page content.
        """

        # Manage authentication
        if st.session_state[setup.NAME][setup.AUTH_NAME][setup.AUTH_QUERY_INDEX]:

            # Configure
            _core.set_page_config(
                header=self.header,
                icon=None,
                layout=setup.LAYOUT,
                initial_sidebar_state=setup.INITIAL_SIDEBAR_STATE
            )

            # Manage the active session
            if st.session_state[setup.NAME][setup.SESSIONS_DB_NAME][setup.SESSIONS_DB_QUERY_INDEX]:

                # Display web-page header
                if not self.headerless:
                    _core.display_page_header(
                        header=self.header,
                        tagline=self.tagline,
                        context=copy.deepcopy(
                            st.session_state[setup.NAME][setup.SESSIONS_DB_NAME][setup.SESSIONS_DB_NAME]['settings']
                        )
                    )

                # Initialize the scope-database table
                _ = sessions.Connection().create_table(
                    table_name=sessions.Schemas.analysis.name,
                    schema=sessions.Schemas.analysis
                )

                # Initialize the analysis-database table
                _ = analysis.Connection().create_table(
                    table_name=analysis.Schemas.analysis.name,
                    schema=analysis.Schemas.analysis
                )

                # Refresh the run-listing table
                _run_listing.refresh_run_listing_table(
                    db_name=self.db_name,
                    table_name=self.table_name,
                    query_index=self.query_index,
                )

                # Display the run-listing table
                _run_listing.display_run_listing_table(
                    db_name=self.db_name,
                    table_name=self.table_name,
                    query_index=self.query_index,
                    scope_db_name=self.scope_db_name,
                    scope_query_index=self.scope_query_index
                )

                # Display page status
                _core.display_page_status(
                    db_name=self.db_name
                )

            else:

                # Display web-page header
                if not self.headerless:
                    _core.display_page_header(
                        header=self.header,
                        tagline=self.tagline,
                        context=None
                    )

                # Display content information
                _core.display_page_content_info(
                    content_info=self.content_info
                )

        else:

            # Return to home-page
            st.switch_page(st.session_state[setup.NAME]['pages']['home'])
