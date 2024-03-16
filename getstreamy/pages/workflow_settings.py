"""
Information
---------------------------------------------------------------------
Name        : workflow_settings.py
Location    : ~/pages
Author      : Tom Eleff
Published   : 2024-03-12
Revised on  : .

Description
---------------------------------------------------------------------
Contains the `Class` for the session-settings-page.
"""

import copy
import streamlit as st
from getstreamy import setup
from getstreamy.components import _key_value, _core


class Content():

    def __init__(
        self,
        header: str = 'Workflow',
        tagline: str = 'Configure the parameters essential to the workflow.',
        content_info: str = (
            'Navigate to the **%s** page to load a session.' % (
                ''.join([
                    setup.SESSIONS_DB_NAME[0].upper(),
                    setup.SESSIONS_DB_NAME[1:].lower()
                ])
            )
        ),
        headerless: bool = False,
        clear_on_submit: bool = False,
        table_name: str = 'workflow',
        settings: list = [
            {
                "sort": 0,
                "type": "text-input",
                "dtype": "str",
                "parameter": "Y",
                "name": "Response metric name",
                "value": "",
                "kwargs": False,
                "description": """
                    Input the name of the Response metric to model.
                """
            },
            {
                "sort": 1,
                "type": "toggle",
                "dtype": "bool",
                "parameter": "tune_this_time",
                "name": "Estimate tuning hyper-parameters",
                "value": True,
                "kwargs": False,
                "description": """
                    If ```False```,
                    the saved hyper-parameters will be used.
                """
            },
            {
                "sort": 2,
                "type": "text-input",
                "dtype": "str",
                "parameter": "saved_hypers_filename",
                "name": "Saved hyper-parameters filename",
                "value": "",
                "kwargs": False,
                "description": """
                    Input the name of the hyper-parameters source file
                    when _Estimate tuning hyper-parameters_ = ```False```
                """
            },
            {
                "sort": 3,
                "type": "toggle",
                "dtype": "bool",
                "parameter": "search_seasonality",
                "name": "Select optimal seasonality controls",
                "value": True,
                "kwargs": False,
                "description": """
                    If ```True```,
                    the optimal seasonal controls are automatically selected.
                """
            },
            {
                "sort": 4,
                "type": "slider",
                "dtype": "int",
                "parameter": "fft_terms",
                "name": "Number of fourier terms for seasonality",
                "value": 2,
                "kwargs": {
                    "min_value": 0,
                    "max_value": 5,
                    "step": 1
                },
                "description": """
                    Select the number of fourier terms.
                    ```2``` is roughly semi-annual & trimesters,
                    ```3``` is semi-annual, trimesters and quarters.
                """
            },
            {
                "sort": 5,
                "type": "text-input",
                "dtype": "str",
                "parameter": "interaction_fft",
                "name": "Seasonality interaction dimensions",
                "value": "",
                "kwargs": None,
                "description": """
                    Input the dimension names to evaluate
                    as seasonality interactions.
                """
            },
            {
                "sort": 6,
                "type": "toggle",
                "dtype": "bool",
                "parameter": "search_randoms",
                "name": "Evaluate multiple random effects",
                "value": False,
                "kwargs": False,
                "description": """
                    If ```True```, multiple random effects will be evaluated.
                """
            },
            {
                "sort": 7,
                "type": "text-input",
                "dtype": "str",
                "parameter": "list_rand_ints",
                "name": "List random effects intercepts",
                "value": "",
                "kwargs": None,
                "description": """
                    Input the dimension names that should have random effects.
                """
            },
            {
                "sort": 8,
                "type": "text-input",
                "dtype": "str",
                "parameter": "list_rand_slopes",
                "name": "List factors for random slopes",
                "value": "",
                "kwargs": None,
                "description": """
                    Input the factor names that should have random slopes.
                """
            }
        ],
    ):
        """ Initializes the content of the workflow-settings `Class`.

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
        table_name : 'str'
            Name of the table within `db_name` to store the setting(s) parameters & values
        settings : `list`
            List of dictionary objects containing the setting(s) parameters & values
        """

        # Assign content class variables
        self.header = header
        self.tagline = tagline
        self.content_info = content_info
        self.headerless = headerless
        self.clear_on_submit = clear_on_submit

        # Assign database class variables
        self.db_name = setup.SESSIONS_DB_NAME
        self.table_name = table_name
        self.query_index = setup.SESSIONS_DB_QUERY_INDEX

        # Assign default session state class variables
        self.settings = copy.deepcopy(settings)

        # Initialize session state defaults
        _core.initialize_session_state_defaults()

        # Assign key-value pair defaults
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
            # for index, (key, value) in enumerate(
            #     setup.SESSIONS_DEFAULTS.items()
            # ):
            #     st.session_state[setup.NAME][self.db_name][key] = copy.deepcopy(value)

        # Initialize session state status defaults
        _core.initialize_session_state_status_defaults(
            db_name=self.db_name
        )

        # Initialize key-value pair defaults
        if setup.SESSIONS_DB_NAME not in st.session_state[setup.NAME]:
            st.session_state[setup.NAME][setup.SESSIONS_DB_NAME] = copy.deepcopy(
                setup.SESSIONS_DEFAULTS
            )

    def serve(
        self
    ):
        """ Serves the workflow-settings-page content.
        """

        # Manage authentication
        if st.session_state[setup.NAME][setup.AUTH_NAME][setup.AUTH_QUERY_INDEX]:

            # Display web-page header
            _core.display_page_header(
                header=self.header,
                tagline=self.tagline,
                headerless=self.headerless
            )

            # Manage the active session
            if st.session_state[setup.NAME][setup.SESSIONS_DB_NAME][setup.SESSIONS_DB_QUERY_INDEX]:

                # Parse the form response
                response = _key_value.parse_form_response(
                    db_name=self.db_name,
                    table_name=self.table_name
                )

                # Update the workflow-settings database
                if response:
                    _key_value.update_settings(
                        db_name=self.db_name,
                        table_name=self.table_name,
                        query_index=self.query_index,
                        response=response
                    )

                # Initialize the workflow-key-value-pair-settings database table
                _key_value.initialize_key_value_pair_table(
                    db_name=self.db_name,
                    table_name=self.table_name,
                    query_index=self.query_index,
                    settings=copy.deepcopy(self.settings)
                )

                # Display the workflow-key-value-pair-settings configuration form
                _key_value.display_key_value_pair_settings_form(
                    db_name=self.db_name,
                    table_name=self.table_name,
                    query_index=self.query_index,
                    apply_db_values=True,
                    clear_on_submit=self.clear_on_submit
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
