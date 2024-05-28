"""
Information
---------------------------------------------------------------------
Name        : run_analysis.py
Location    : ~/pages
Author      : Tom Eleff
Published   : 2024-03-28
Revised on  : .

Description
---------------------------------------------------------------------
Contains the `Class` for the run-analysis-page.
"""

import copy
import streamlit as st
from assemblit import setup, db
from assemblit.pages._components import _core, _run_analysis


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
        """ Initializes the content of the run-analysis `Class`.

        Parameters
        ----------
        header : `str`
            String to display as the web-page header
        tagline : `str`
            String to display as the web-page tagline
        content_info : `str`
            String to display as `streamlit.info()` when there is no active session
        headerless : `bool`
            `True` or `False`, determines whether to display the header & tagline
        """

        # Assign content class variables
        self.header = header
        self.tagline = tagline
        self.content_info = content_info
        self.headerless = headerless

        # Assign database class variables to set the scope for data-ingestion
        self.scope_db_name = setup.SESSIONS_DB_NAME
        self.scope_query_index = setup.SESSIONS_DB_QUERY_INDEX

        # Assign database class variables
        self.db_name = setup.ANALYSIS_DB_NAME
        self.table_name = 'listing'
        self.query_index = setup.ANALYSIS_DB_QUERY_INDEX

        # Assign default session state class variables
        self.settings = [
            {
                "sort": 0,
                "type": "multiselect",
                "dtype": "str",
                "parameter": "dataset",
                "name": "Dataset",
                "value": "",
                "kwargs": False,
                "description": """
                    Select a dataset for the model analysis.
                """
            },
            {
                "sort": 1,
                "type": "text-input",
                "dtype": "str",
                "parameter": "run_information",
                "name": "Run information",
                "value": "",
                "kwargs": False,
                "description": """
                    Enter context about the model analysis run.
                """
            }
        ]
        self.selector = {
            "sort": 0,
            "type": "selectbox",
            "dtype": "str",
            "parameter": "file_name",
            "name": "Datafile name",
            "value": "",
            "kwargs": None,
            "description": "Select a datafile to review."
        }

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
                'datasets': {
                    'selector': copy.deepcopy(self.selector),
                    'set-up': False
                }
            }
        else:
            if 'datasets' not in st.session_state[setup.NAME][self.db_name]:
                st.session_state[setup.NAME][setup.DATA_DB_NAME]['datasets'] = {
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

                # Update the run-analysis-settings database
                if response:
                    _run_analysis.run_workflow(
                        db_name=self.db_name,
                        table_name=self.table_name,
                        query_index=self.query_index,
                        scope_db_name=self.scope_db_name,
                        scope_query_index=self.scope_query_index,
                        response=response
                    )

                # Initialize the scope-database table
                _ = db.initialize_table(
                    db_name=self.scope_db_name,
                    table_name=self.table_name,
                    cols=(
                        [self.scope_query_index] + [self.query_index]
                    )
                )

                # Initialize the analysis-database table
                _ = db.initialize_table(
                    db_name=self.db_name,
                    table_name=self.table_name,
                    cols=(
                        [
                            self.query_index,
                            'server_type',
                            'server_id',
                            'submitted_by',
                            'created_on',
                            'state',
                            'start_time',
                            'end_time',
                            'run_time',
                            'inputs',
                            'outputs',
                            'run_information',
                            'parameters',
                            'tags',
                            'url'
                        ]
                    )
                )

                # Display the run-analysis submission form
                _run_analysis.display_run_analysis_form(
                    db_name=self.db_name,
                    table_name=self.table_name,
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
