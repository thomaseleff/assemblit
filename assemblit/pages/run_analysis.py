"""
Information
---------------------------------------------------------------------
Name        : run_analysis.py
Location    : ~/pages

Description
---------------------------------------------------------------------
Contains the `class` for the run-analysis-page.
"""

import copy
import streamlit as st
from assemblit import setup
from assemblit.app.structures import Setting
from assemblit.pages._components import _core, _run_analysis
from assemblit.database import sessions, data, analysis


class Content():

    def __init__(
        self,
        header: str = 'Analysis',
        tagline: str = 'Configure and submit a model analysis.',
        content_info: str = (
            'Navigate to the **%s** page to load a session.' % (
                ''.join([
                    setup.SESSIONS_DB_NAME[0].upper(),
                    setup.SESSIONS_DB_NAME[1:].lower()
                ])
            )
        ),
        headerless: bool = False
    ):
        """ Initializes the content of the run-analysis `class`.

        Parameters
        ----------
        header : `str`
            String to display as the web-page header.
        tagline : `str`
            String to display as the web-page tagline.
        content_info : `str`
            String to display as `streamlit.info()` when there is no active session.
        headerless : `bool`
            `True` or `False`, determines whether to display the header & tagline.
        """

        # Assign content class variables
        self.header = header
        self.tagline = tagline
        self.content_info = content_info
        self.headerless = headerless

        # Assign database class variables to set the scope for run-analysis
        self.scope_db_name = setup.SESSIONS_DB_NAME
        self.scope_query_index = setup.SESSIONS_DB_QUERY_INDEX

        # Assign database class variables
        self.db_name = setup.ANALYSIS_DB_NAME
        self.table_name = analysis.Schemas.analysis.name
        self.query_index = setup.ANALYSIS_DB_QUERY_INDEX

        # Assign default session state class variables
        self.settings = [
            Setting(
                type='multiselect',
                dtype='str',
                parameter='dataset',
                name='Dataset',
                description='Select a dataset for the model analysis.'
            ),
            Setting(
                type='text-input',
                dtype='str',
                parameter='run_information',
                name='Run information',
                description='Enter context about the model analysis run.'
            )
        ]
        self.selector = Setting(
            type='selectbox',
            dtype='str',
            parameter='file_name',
            name='Datafile name',
            description='Select a datafile to review.'
        )

        # Initialize session state defaults
        _core.initialize_session_state_defaults()

        # Assign key-value pair defaults for the analysis
        if self.db_name not in st.session_state[setup.NAME]:
            st.session_state[setup.NAME][self.db_name] = {
                self.table_name: {
                    'settings': copy.deepcopy(self.settings),
                    'form-submission': False
                },
            }
        else:
            if self.table_name not in st.session_state[setup.NAME][self.db_name]:
                st.session_state[setup.NAME][self.db_name][self.table_name] = {
                    'settings': copy.deepcopy(self.settings),
                    'form-submission': False
                }

        # Assign key-value pair defaults for the selector
        if self.db_name not in st.session_state[setup.NAME]:
            st.session_state[setup.NAME][setup.DATA_DB_NAME] = {
                data.Schemas.data.name: {
                    'selector': copy.deepcopy(self.selector),
                    'set-up': False
                }
            }
        else:
            if data.Schemas.data.name not in st.session_state[setup.NAME][self.db_name]:
                st.session_state[setup.NAME][setup.DATA_DB_NAME][data.Schemas.data.name] = {
                    'selector': copy.deepcopy(self.selector),
                    'set-up': False
                }

        # Initialize session state status defaults
        _core.initialize_session_state_status_defaults(
            db_name=self.db_name
        )

    def serve(
        self
    ):
        """ Serves the run-analysis-page content.
        """

        # Manage authentication
        if st.session_state[setup.NAME][setup.AUTH_NAME][setup.AUTH_QUERY_INDEX]:

            # Display web-page header
            _core.display_page_header(
                header=self.header,
                tagline=self.tagline,
                headerless=self.headerless,
                show_context=True
            )

            # Manage the active session
            if st.session_state[setup.NAME][setup.SESSIONS_DB_NAME][setup.SESSIONS_DB_QUERY_INDEX]:

                # Parse the form response
                response = _run_analysis.parse_form_response(
                    db_name=self.db_name,
                    table_name=self.table_name
                )

                # Run an analysis and update the run-analysis-settings database
                if response:
                    _run_analysis.run_job(
                        db_name=self.db_name,
                        table_name=self.table_name,
                        query_index=self.query_index,
                        scope_db_name=self.scope_db_name,
                        scope_query_index=self.scope_query_index,
                        response=response
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

                # Display the run-analysis submission form
                _run_analysis.display_run_analysis_form(
                    db_name=self.db_name,
                    table_name=self.table_name,
                    scope_db_name=self.scope_db_name,
                    scope_query_index=self.scope_query_index,
                    header='Run',
                    tagline='Populate each field in the form then click `Run` to submit the analysis.'
                )

                # Display page status
                _core.display_page_status(
                    db_name=self.db_name
                )

            else:

                # Display content information
                _core.display_page_content_info(
                    content_info=self.content_info
                )

        else:

            # Return to home-page
            st.switch_page(st.session_state[setup.NAME]['pages']['home'])
