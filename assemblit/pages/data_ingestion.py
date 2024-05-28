"""
Information
---------------------------------------------------------------------
Name        : data_ingestion.py
Location    : ~/pages
Author      : Tom Eleff
Published   : 2024-03-16
Revised on  : .

Description
---------------------------------------------------------------------
Contains the `Class` for the data-ingestion-page.
"""

import copy
import streamlit as st
import pandas as pd
from assemblit import setup, db
from assemblit.pages._components import _core, _data_uploader, _data_review


class Content():

    def __init__(
        self,
        header: str = 'Data',
        tagline: str = 'Upload, review and finalize the model input data for the session.',
        content_info: str = (
            'Navigate to the **%s** page to load a session.' % (
                ''.join([
                    setup.SESSIONS_DB_NAME[0].upper(),
                    setup.SESSIONS_DB_NAME[1:].lower()
                ])
            )
        ),
        headerless: bool = False,
        data_dictionary: pd.DataFrame = pd.DataFrame(),
        data_example: pd.DataFrame = pd.DataFrame()
    ):
        """ Initializes an instance of the data-ingestion-page Class().

        Parameters
        ----------
        header : `str`
            String to display as the web-page header.
        tagline : `str`
            String to display as the web-page tagline.
        content_info : `str`
            String to display as `streamlit.info()` when there is no selected session.
        data_dictionary : `pd.DataFrame`
            An optional data dictionary that describes the structure and format of the
                expected datafile.
        data_example : `pd.DataFrame`
            An optional dataframe that provides a reference for a valid datafile.
        """

        # Assign content class variables
        self.header = header
        self.tagline = tagline
        self.headerless = headerless
        self.content_info = content_info
        self.data_dictionary = data_dictionary
        self.data_example = data_example

        # Assign database class variables to set the scope for data-ingestion
        self.scope_db_name = setup.SESSIONS_DB_NAME
        self.scope_query_index = setup.SESSIONS_DB_QUERY_INDEX

        # Assign database class variables
        self.db_name = setup.DATA_DB_NAME
        self.table_name = 'datasets'
        self.query_index = setup.DATA_DB_QUERY_INDEX

        # Assign default session state class variables
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

        # Assign key-value pair defaults
        if self.db_name not in st.session_state[setup.NAME]:
            st.session_state[setup.NAME][self.db_name] = {
                self.table_name: {
                    'selector': copy.deepcopy(self.selector),
                    'set-up': False
                }
            }
        else:
            if self.table_name not in st.session_state[setup.NAME][self.db_name]:
                st.session_state[setup.NAME][self.db_name][self.table_name] = {
                    'selector': copy.deepcopy(self.selector),
                    'set-up': False
                }

        # Initialize session state status defaults
        _core.initialize_session_state_status_defaults(
            db_name=self.db_name
        )

    def serve(self):
        """ Serves the data-ingestion-page content.
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

                # Initialize the scope-database table
                _ = db.initialize_table(
                    db_name=self.scope_db_name,
                    table_name=self.table_name,
                    cols=(
                        [self.scope_query_index] + [self.query_index]
                    )
                )

                # Initialize the data-ingestion-database table
                _ = db.initialize_table(
                    db_name=self.db_name,
                    table_name=self.table_name,
                    cols=(
                        [
                            self.query_index,
                            'uploaded_by',
                            'created_on',
                            'final',
                            'version',
                            'file_name',
                            'dbms',
                            'datetime',
                            'dimensions',
                            'metrics',
                            'selected_datetime',
                            'selected_dimensions',
                            'selected_metrics',
                            'selected_aggrules',
                            'size_mb',
                            'sha256'
                        ]
                    )
                )

                # Display the data-contract expander
                _data_uploader.display_data_contract(
                    data_dictionary=self.data_dictionary,
                    data_example=self.data_example
                )

                # Display the data-uploader form
                _data_uploader.display_data_uploader(
                    db_name=self.db_name,
                    table_name=self.table_name
                )

                # Display the schema-validation result and the data-preview table
                _data_uploader.display_data_preview(
                    db_name=self.db_name,
                    table_name=self.table_name,
                    query_index=self.query_index,
                    scope_db_name=self.scope_db_name,
                    scope_query_index=self.scope_query_index
                )

                # Display the data-review summary report
                _data_review.display_data_review(
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

                # Display content information
                _core.display_page_content_info(
                    content_info=self.content_info
                )

        else:

            # Return to home-page
            st.switch_page(st.session_state[setup.NAME]['pages']['home'])
