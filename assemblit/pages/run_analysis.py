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
        clear_on_submit : `bool`
            `True` or `False`, determines whether to clear the form-submission responses
                after submission
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

        # Initialize session state defaults
        _core.initialize_session_state_defaults()

        # Assign default session state class variables
        self.parameters = [
            {
                'db_name': setup.DATA_DB_NAME,
                'table_name': 'datasets',
                'query_index': setup.DATA_DB_QUERY_INDEX,
                'scope_db_name': setup.SESSIONS_DB_NAME,
                'scope_query_index': setup.SESSIONS_DB_QUERY_INDEX
            }
        ]

        # Assign key-value pair defaults
        if self.db_name not in st.session_state[setup.NAME]:
            st.session_state[setup.NAME][self.db_name] = {
                self.table_name: {
                    'parameters': copy.deepcopy(self.parameters),
                    'form-submission': False
                },
            }
        else:
            if self.table_name not in st.session_state[setup.NAME][self.db_name]:
                st.session_state[setup.NAME][self.db_name][self.table_name] = {
                    'parameters': copy.deepcopy(self.parameters),
                    'form-submission': False
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

                # Update the workflow-settings database
                if response:
                    _run_analysis.run_workflow(
                        db_name=self.db_name,
                        table_name=self.table_name,
                        query_index=self.query_index,
                        # scope_db_name=self.scope_db_name,
                        # scope_query_index=self.scope_query_index,
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
                            'created',
                            'inputs',
                            'outputs',
                            'run_request',
                            'state',
                            'run_information'
                        ]
                    )
                )

                # Submit run
                # _run_analysis.submit_run(
                #     db_name=self.db_name,
                #     table_name=self.table_name,
                #     query_index=self.query_index,
                #     response=_key_value.parse_form_response(
                #         db_name=self.db_name,
                #         table_name=self.table_name
                #     )
                # )

                # Display the run-analysis context
                # _run_analysis.display_run_analysis_context(
                #     header='Context',
                #     tagline='Parameter information about the session.'
                # )

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
