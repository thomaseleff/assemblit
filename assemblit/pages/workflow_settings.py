""" Page builder """

import os
import copy
import streamlit as st
from assemblit import setup, blocks
from assemblit.toolkit import _exceptions, content
from assemblit.pages._components import _key_value, _core

_COMPATIBLE_APP_TYPES = ['aaas']


class Content():
    """ A `class` that contains the workflow settings-page content.

    Parameters
    ----------
    header : `str`
        String to display as the webpage header
    tagline : `str`
        String to display as the webpage tagline
    content_info : `str`
        String to display as `streamlit.info()` when there is no active session
    settings : `list[Setting]`
        List of `assemblit.app.structures.Setting` objects containing the setting(s) parameters & values
    headerless : `bool`
        `True` or `False`, determines whether to display the header & tagline
    clear_on_submit : `bool`
        `True` or `False`, determines whether to clear the form-submission responses
            after submission

    Examples
    --------

    ``` python

    # Constructing the workflow settings-page content

    from assemblit.pages import workflow_settings

    Workflow = workflow_settings.Content(
        header='Workflow',
        tagline='Configure the parameters essential to the workflow.'
    )

    # Serving the workflow settings-page content

    Workflow.serve()

    ```
    """

    def __init__(
        self,
        header: str = 'Workflow',
        tagline: str = 'Configure the parameters essential to the workflow.',
        content_info: str = 'Navigate to the **scope-selector** page to load a session.',
        settings: list[blocks.structures.Setting] = [
            blocks.structures.Setting(
                type='text-input',
                dtype='str',
                parameter='y',
                name='Response metric',
                description='Input the name of the Response metric to model.'
            )
        ],
        headerless: bool = False,
        clear_on_submit: bool = False,
        # table_name: str = 'workflow'
    ):
        """ Initializes an instance of the workflow settings-page content.

        Parameters
        ----------
        header : `str`
            String to display as the webpage header
        tagline : `str`
            String to display as the webpage tagline
        content_info : `str`
            String to display as `streamlit.info()` when there is no active session
        settings : `list[Setting]`
            List of `assemblit.app.structures.Setting` objects containing the setting(s) parameters & values
        headerless : `bool`
            `True` or `False`, determines whether to display the header & tagline
        clear_on_submit : `bool`
            `True` or `False`, determines whether to clear the form-submission responses
                after submission
        """

        # Validate compatibility
        if setup.TYPE not in _COMPATIBLE_APP_TYPES:
            raise _exceptions.CompatibilityError(
                app_type=setup.TYPE,
                page_name=os.path.splitext(os.path.basename(__file__))[0],
                compatible_app_types=_COMPATIBLE_APP_TYPES
            )

        # Assign content class variables
        self.header = content.clean_text(header)
        self.tagline = content.clean_text(tagline)
        self.content_info = content.clean_text(content_info)
        self.headerless = headerless
        self.clear_on_submit = clear_on_submit

        # Assign database class variables
        self.db_name = setup.SESSIONS_DB_NAME
        self.table_name = 'workflow'
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

        # Initialize session state status defaults
        _core.initialize_session_state_status_defaults(
            db_name=self.db_name
        )

    def serve(
        self
    ):
        """ Serves the workflow settings-page content.
        """

        # Manage authentication
        if st.session_state[setup.NAME][setup.AUTH_NAME][setup.AUTH_QUERY_INDEX]:

            # Manage the active session
            if st.session_state[setup.NAME][setup.SESSIONS_DB_NAME][setup.SESSIONS_DB_QUERY_INDEX]:

                # Configure and display the header
                if not self.headerless:
                    _core.set_page_config(
                        header=self.header,
                        icon=None,
                        layout=setup.LAYOUT,
                        initial_sidebar_state=setup.INITIAL_SIDEBAR_STATE
                    )
                    _core.display_page_header(
                        header=self.header,
                        tagline=self.tagline,
                        context=copy.deepcopy(
                            st.session_state[setup.NAME][setup.SESSIONS_DB_NAME][setup.SESSIONS_DB_NAME]['settings']
                        )
                    )

                # Parse the form response
                response = _key_value.parse_form_response(
                    db_name=self.db_name,
                    table_name=self.table_name
                )

                # Update the workflow settings database
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

                # Configure and display the header
                if not self.headerless:
                    _core.set_page_config(
                        header=self.header,
                        icon=None,
                        layout=setup.LAYOUT,
                        initial_sidebar_state=setup.INITIAL_SIDEBAR_STATE
                    )
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
