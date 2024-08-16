""" Page builder """

import os
import copy
import streamlit as st
from assemblit import setup, blocks, _database
from assemblit.toolkit import _exceptions
from assemblit._auth import vault
from assemblit._database import users
from assemblit.pages._components import _key_value, _core

_COMPATIBLE_APP_TYPES = ['aaas']


class Content():
    """ A `class` that contains the account settings-page content.

    Parameters
    ----------
    headerless : `bool`
        `True` or `False`, determines whether to display the header & tagline
    personalize : `bool`
        `True` or `False`, determines whether to personalize the header,
            concatenating the user's name, e.g., "Welcome, Jonathan"

    Notes
    -----
    The account settings-page can only be created when the ENV variable `ASSEMBLIT_REQUIRE_AUTHENTICATION` = 'True'.

    Examples
    --------

    ``` python

    # Constructing the account settings-page content

    from assemblit.pages import account_settings

    Settings = account_settings.Content()

    # Serving the account settings-page content

    Settings.serve()

    ```
    """

    def __init__(
        self,
        headerless: bool = False,
        personalize: bool = True
    ):
        """ Initializes an instance of the account settings-page content.

        Parameters
        ----------
        headerless : `bool`
            `True` or `False`, determines whether to display the header & tagline
        personalize : `bool`
            `True` or `False`, determines whether to personalize the header,
                concatenating the user's name, e.g., "Welcome, Jonathan"
        """

        # Validate compatibility
        if setup.TYPE not in _COMPATIBLE_APP_TYPES:
            raise _exceptions.CompatibilityError(
                app_type=setup.TYPE,
                page_name=os.path.splitext(os.path.basename(__file__))[0],
                compatible_app_types=_COMPATIBLE_APP_TYPES
            )

        # Assign content class variables
        self.header = 'Welcome'
        self.tagline = 'Manage your personal information, privacy and data.'
        self.headerless = headerless
        self.personalize = personalize
        self.clear_on_submit = True

        # Assign database class variables
        self.db_name = setup.USERS_DB_NAME
        self.table_name = 'accounts'  # Used only to organize the settings in the session state
        self.query_index = setup.USERS_DB_QUERY_INDEX

        # Assign default session state class variables
        self.settings = [
            blocks.structures.Setting(
                type='text-input',
                dtype='str',
                parameter='first_name',
                name='Name',
                kwargs={'disabled': True}
            ),
            blocks.structures.Setting(
                type='text-input',
                dtype='str',
                parameter='username',
                name='Username',
                kwargs={'disabled': True}
            ),
            blocks.structures.Setting(
                type='text-input',
                dtype='str',
                parameter='change_username',
                name='Change username',
                description='Enter your new email address.'
            ),
            blocks.structures.Setting(
                type='text-input',
                dtype='str',
                parameter='change_password0',
                name='Change password',
                kwargs={'type': 'password'},
                description='Enter your new password.'
            ),
            blocks.structures.Setting(
                type='text-input',
                dtype='str',
                parameter='change_password1',
                name='Re-enter password',
                kwargs={'type': 'password'},
                description='Re-enter your new password'
            ),
            blocks.structures.Setting(
                type='toggle',
                dtype='bool',
                parameter='delete_account',
                name='Delete account',
                value=False,
                description='Deleting your account will remove all your data.'
            )
        ]

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
        """ Serves the account settings-page content.
        """

        # Manage authentication
        if setup.REQUIRE_AUTHENTICATION:
            if st.session_state[setup.NAME][setup.AUTH_NAME][setup.AUTH_QUERY_INDEX]:

                # Personalize the header content
                if self.personalize:
                    self.header = '%s, %s' % (
                        self.header,
                        st.session_state[setup.NAME][self.db_name]['name']
                    )

                # Configure
                _core.set_page_config(
                    header=self.header,
                    icon=None,
                    layout=setup.LAYOUT,
                    initial_sidebar_state=setup.INITIAL_SIDEBAR_STATE
                )

                # Display webpage header
                if not self.headerless:
                    _core.display_page_header(
                        header=self.header,
                        tagline=self.tagline,
                        context=None
                    )

                # Parse the form response & update credentials
                vault.update_credentials(
                    response=_key_value.parse_form_response(
                        db_name=self.db_name,
                        table_name=self.table_name
                    )
                )

                # Initialize the connection to the users database
                Users = users.Connection()

                # Apply credential settings into the account parameters
                st.session_state[setup.NAME][self.db_name][self.table_name]['settings'][0].value = (
                    Users.select_table_column_value(
                        table_name=users.Schemas.credentials.name,
                        col='first_name',
                        filtr=_database._structures.Filter(
                            col=self.query_index,
                            val=st.session_state[setup.NAME][self.db_name][self.query_index]
                        ),
                        return_dtype='str'
                    )
                )
                st.session_state[setup.NAME][self.db_name][self.table_name]['settings'][1].value = (
                    Users.select_table_column_value(
                        table_name=users.Schemas.credentials.name,
                        col='username',
                        filtr=_database._structures.Filter(
                            col=self.query_index,
                            val=st.session_state[setup.NAME][self.db_name][self.query_index]
                        ),
                        return_dtype='str'
                    )
                )

                # Display the account-key-value-pair-settings configuration form
                _key_value.display_key_value_pair_settings_form(
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

        else:
            raise vault.AuthenticationNotRequired(
                ' '.join([
                    'Account settings are unavailable when REQUIRE_AUTHENTICATION = False.',
                    'To enable account settings, set REQUIRE_AUTHENTICATION = True within `/.assemblit/config.yaml`.',
                    'When authentication is required, visitors will be required to sign-up or login and will',
                    'be able to manage their information, privacy and data via the `Account Settings` page.'
                ])
            )
