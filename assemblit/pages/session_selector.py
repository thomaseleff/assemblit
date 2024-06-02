"""
Information
---------------------------------------------------------------------
Name        : session_selector.py
Location    : ~/pages
Author      : Tom Eleff
Published   : 2024-03-16
Revised on  : .

Description
---------------------------------------------------------------------
Contains the `Class` for the session-selector-page.
"""

import copy
import streamlit as st
from assemblit import setup, db
from assemblit.pages._components import _core, _key_value, _selector


class Content():

    def __init__(
        self,
        header: str = 'Sessions',
        tagline: str = 'Select a session.',
        selector: dict = {
            "sort": 0,
            "type": "selectbox",
            "dtype": "str",
            "parameter": "session_name",
            "name": "Session Name",
            "value": "",
            "kwargs": None,
            "description": "Select a session."
        },
        settings: list = [
            {
                "sort": 0,
                "type": "text-input",
                "dtype": "str",
                "parameter": "session_name",
                "name": "Session Name",
                "value": "",
                "kwargs": None,
                "description": "Input the name of a new session."
            }
        ],
        headerless: bool = False,
        clear_on_submit: bool = True
    ):
        """ Initializes an instance of the session-selector `Class`.

        Parameters
        ----------
        header : `str`
            String to display as the web-page header
        tagline : `str`
            String to display as the web-page tagline
        selector : `dict`
            Dictionary object containing the setting parameter & value to populate the
                drop-down selection options
        settings : `list`
            List of dictionary objects containing the setting(s) parameters & values
        headerless : `bool`
            `True` or `False`, determines whether to display the header & tagline
        clear_on_submit : `bool`
            `True` or `False`, determines whether to clear the form-submission responses
                after submission
        """

        # Assign content class variables
        self.header = header
        self.tagline = tagline
        self.headerless = headerless
        self.clear_on_submit = clear_on_submit

        # Assign database class variables to set the scope for the sessions-selector
        self.scope_db_name = setup.USERS_DB_NAME
        self.scope_query_index = setup.USERS_DB_QUERY_INDEX

        # Assign database class variables
        self.db_name = setup.SESSIONS_DB_NAME
        self.table_name = setup.SESSIONS_DB_NAME
        self.query_index = setup.SESSIONS_DB_QUERY_INDEX

        # Assign default session state class variables
        self.selector = copy.deepcopy(selector)
        self.settings = copy.deepcopy(settings)

        # Initialize session state defaults
        _core.initialize_session_state_defaults()

        # Assign session-selector defaults
        if self.db_name not in st.session_state[setup.NAME]:
            st.session_state[setup.NAME][self.db_name] = {
                self.table_name: {
                    'selector': copy.deepcopy(selector),
                    'settings': copy.deepcopy(self.settings),
                    'form-submission': False,
                    'set-up': False
                },
            }
        else:
            if self.table_name not in st.session_state[setup.NAME][self.db_name]:
                st.session_state[setup.NAME][self.db_name][self.table_name] = {
                    'selector': copy.deepcopy(selector),
                    'settings': copy.deepcopy(self.settings),
                    'form-submission': False,
                    'set-up': False
                }

        # Initialize session state status defaults
        _core.initialize_session_state_status_defaults(
            db_name=self.db_name
        )

    def serve(self):
        """ Serves the session-selector-page content.
        """

        # Manage authentication
        if st.session_state[setup.NAME][setup.AUTH_NAME][setup.AUTH_QUERY_INDEX]:

            # Display web-page header
            _core.display_page_header(
                header=self.header,
                tagline=self.tagline,
                headerless=self.headerless
            )

            # Parse the form response
            response = _key_value.parse_form_response(
                db_name=self.db_name,
                table_name=self.table_name
            )

            # Update the sessions-settings database
            if response:

                # Create a new session
                if st.session_state[setup.NAME][self.db_name][self.table_name]['set-up']:
                    _selector.create_session(
                        db_name=self.db_name,
                        table_name=self.table_name,
                        query_index=self.query_index,
                        scope_db_name=self.scope_db_name,
                        scope_query_index=self.scope_query_index,
                        response=response
                    )

                    # Reset set-up form
                    if not st.session_state[setup.NAME][self.db_name]['errors']:
                        _selector.display_session_setup_form(
                            db_name=self.db_name,
                            table_name=self.table_name,
                            value=False
                        )

                # Update an existing session
                else:
                    _selector.update_session(
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

            # Manage the sessions-key-value-pair-settings database table
            _key_value.initialize_key_value_pair_table(
                db_name=self.db_name,
                table_name=self.table_name,
                query_index=self.query_index,
                settings=copy.deepcopy(self.settings)
            )

            # Retrieve sessions-key-value-pair drop-down selection options
            options = _selector.select_selector_dropdown_options(
                db_name=self.db_name,
                table_name=self.table_name,
                query_index=self.query_index,
                scope_db_name=self.scope_db_name,
                scope_query_index=self.scope_query_index
            )

            # Set sessions-key-value-pair drop-down default query index
            index = _selector.select_selector_default_value(
                db_name=self.db_name,
                table_name=self.table_name,
                query_index=self.query_index,
                scope_db_name=self.scope_db_name,
                scope_query_index=self.scope_query_index,
                options=options
            )

            # Set default sessions-key-value-pair settings configuration form attributes
            if not options:
                st.session_state[setup.NAME][self.db_name][self.table_name]['set-up'] = True
            else:
                st.session_state[setup.NAME][self.db_name][self.table_name]['set-up'] = False

            # Display the session-selector drop-down
            self.display_session_selector(
                options=options,
                index=index
            )

            # Display the sessions-key-value-pair-settings configuration form for an existing session
            if (
                (st.session_state[setup.NAME][setup.SESSIONS_DB_NAME][setup.SESSIONS_DB_QUERY_INDEX])
                and (not st.session_state[setup.NAME][self.db_name][self.table_name]['set-up'])
            ):
                _key_value.display_key_value_pair_settings_form(
                    header='Parameters',
                    tagline='Edit the form then click `Save` to modify the currently selected entry.',
                    db_name=self.db_name,
                    table_name=self.table_name,
                    query_index=self.query_index,
                    apply_db_values=True,
                    clear_on_submit=self.clear_on_submit
                )

            # Display the sessions-key-value-pair-settings configuration form for a new session
            else:

                # Reset session-selector settings defaults
                st.session_state[setup.NAME][self.db_name][self.table_name]['settings'] = copy.deepcopy(self.settings)

                # Display
                _key_value.display_key_value_pair_settings_form(
                    header='Setup',
                    tagline='Populate each field in the form then click `Save` to create a new entry.',
                    db_name=self.db_name,
                    table_name=self.table_name,
                    query_index=self.query_index,
                    apply_db_values=False,
                    clear_on_submit=self.clear_on_submit
                )

            # Display page status
            _core.display_page_status(
                db_name=self.db_name
            )

        else:

            # Return to home-page
            st.switch_page(st.session_state[setup.NAME]['pages']['home'])

    # Define generic sessions-selector service function(s)
    def display_session_selector(
        self,
        options: list,
        index: int
    ):
        """ Displays the database table drop-down options and default value as a selector.

        Parameters
        ----------
        options: `list`
            The list containing the the drop-down options.
        index : `int`
            The index position of the value to be displayed as the default selection.
        """

        # Layout columns
        col1, col2, col3 = st.columns(setup.CONTENT_COLUMNS)

        # Display the session-selector drop-down
        with col2:

            # Layout session-selector columns
            col1, col2, col3 = st.columns([.6, .2, .2])

            # Display the session-selector
            if not st.session_state[setup.NAME][self.db_name][self.table_name]['set-up']:
                with col1:
                    _selector.display_selector(
                        db_name=self.db_name,
                        table_name=self.table_name,
                        query_index=self.query_index,
                        scope_db_name=self.scope_db_name,
                        scope_query_index=self.scope_query_index,
                        options=options,
                        index=index,
                        disabled=False
                    )
                with col2:
                    self.display_session_delete_button(
                        disabled=False
                    )
                with col3:
                    self.display_session_new_button(
                        disabled=False
                    )
            else:
                with col1:
                    _selector.display_selector(
                        db_name=self.db_name,
                        table_name=self.table_name,
                        query_index=self.query_index,
                        scope_db_name=self.scope_db_name,
                        scope_query_index=self.scope_query_index,
                        options=options,
                        index=index,
                        disabled=True
                    )
                with col2:
                    self.display_session_delete_button(
                        disabled=True
                    )

                with col3:
                    if options:
                        self.display_session_edit_button(
                            disabled=False
                        )
                    else:
                        self.display_session_edit_button(
                            disabled=True
                        )

    def display_session_delete_button(
        self,
        disabled: bool
    ):
        """ Displays the button to delete the selected session.

        Parameters
        ----------
        disabled : `int`
            `True` or `False`, whether the button is displayed disabled or not.
        """

        # Display the 'Delete' button
        st.button(
            label='Delete',
            key='Button:%s' % _selector.generate_selector_key(
                db_name=self.db_name,
                table_name=self.table_name,
                parameter='Delete'
            ),
            type='secondary',
            disabled=disabled,
            on_click=_selector.delete_session,
            kwargs={
                'session_id': st.session_state[setup.NAME][self.db_name][self.query_index]
            },
            use_container_width=True
        )

    def display_session_edit_button(
        self,
        disabled: bool
    ):
        """ Displays the button to edit the settings of the selected session.

        Parameters
        ----------
        disabled : `int`
            `True` or `False`, whether the button is displayed disabled or not.
        """

        # Display the 'Edit' button
        st.button(
            label='Edit',
            key='Button:%s' % _selector.generate_selector_key(
                db_name=self.db_name,
                table_name=self.table_name,
                parameter='Edit'
            ),
            type='primary',
            disabled=disabled,
            on_click=_selector.display_session_setup_form,
            kwargs={
                'db_name': self.db_name,
                'table_name': self.table_name,
                'value': False
            },
            use_container_width=True
        )

    def display_session_new_button(
        self,
        disabled: bool
    ):
        """ Displays the button to create a new session.

        Parameters
        ----------
        disabled : `int`
            `True` or `False`, whether the button is displayed disabled or not.
        """

        # Display the 'New' button
        st.button(
            label='New',
            key='Button:%s-New' % _selector.generate_selector_key(
                db_name=self.db_name,
                table_name=self.table_name,
                parameter='New'
            ),
            type='primary',
            disabled=disabled,
            on_click=_selector.display_session_setup_form,
            kwargs={
                'db_name': self.db_name,
                'table_name': self.table_name,
                'value': True
            },
            use_container_width=True
        )
