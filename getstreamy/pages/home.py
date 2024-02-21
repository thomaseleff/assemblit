"""
Information
---------------------------------------------------------------------
Name        : home.py
Location    : ~/
Author      : Tom Eleff
Published   : 2024-02-13
Revised on  : .

Description
---------------------------------------------------------------------
Contains the `Class` for the home-page.
"""

import streamlit as st
from getstreamy import setup, vault, web
from getstreamy.components import _core


class Content():

    def __init__(
        self,
        header: str = 'Welcome',
        tagline: str = 'A ```gitstreamy``` web-application for Github projects.',
        content_url: str = None,
        content_info: str = 'For more information, visit the Github repository.'
    ):
        """ Initializes an instance of the home-page `Class`.

        Parameters
        ----------
        header : `str`
            String to display as the web-page header
        tagline : `str`
            String to display as the web-page tagline
        content_url : `str`
            URL of the README.md document to display as the web-page content
        content_info : `str`
            String to display as `streamlit.info()` when `content_url = None`
        """

        # Assign content class variables
        self.header = header
        self.tagline = tagline
        self.content_url = content_url
        self.content_info = content_info

        # Initialize database class variables
        self.db_name = setup.USERS_DB_NAME
        self.query_index = setup.USERS_DB_QUERY_INDEX

        # Initialize session state defaults
        _core.initialize_session_state_defaults()

    def serve(
        self
    ):
        """ Serves the home-page content.
        """

        # Manage authentication
        if st.session_state[setup.NAME][setup.AUTH_NAME][setup.AUTH_QUERY_INDEX]:

            # Display the home-page header
            _core.display_page_header(
                header=self.header,
                tagline=self.tagline
            )

            # Display content
            if self.content_url:

                # Layout columns
                col1, col2, col3 = st.columns(setup.CONTENT_COLUMNS)

                # Display readme
                Github = web.Handler(url=self.content_url)
                col2.markdown(Github.get_readme(name='README.md'))

            else:

                # Display content information
                _core.display_page_content_info(
                    content_info=self.content_info
                )

        else:

            # Display the authentication-page
            self.display_user_authentication(
                header=self.header,
                tagline=self.tagline
            )

    # Define generic service function(s)
    def display_user_authentication(
        self,
        header: str = 'Welcome',
        tagline: str = 'Please login or sign-up.'
    ):
        """ Displays the standard authentication-page.

        Parameters
        ----------
        header : `str`
            String to display as the web-page header
        tagline : `str`
            String to display as the web-page tagline
        """

        # Configure
        st.set_page_config(
            layout='centered',
            initial_sidebar_state='collapsed'
        )
        st.markdown(
            """
            <style>
                [data-testid="collapsedControl"] {
                    display: none
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Display login content
        if not st.session_state[setup.NAME][setup.AUTH_NAME]['sign-up']:

            # Display header & tagline
            st.header(header)
            st.write(tagline)
            st.write('')
            st.write('')

            # Display login form
            with st.form('Login', clear_on_submit=False):
                st.subheader('Login')
                st.text_input(
                    label='Username',
                    key='username',
                    placeholder='Enter your email address'
                )
                st.text_input(
                    label='Password',
                    key='password',
                    type='password',
                    placeholder='Enter your password'
                )

                # Layout columns
                col1, col2, col3 = st.columns([1, 1, 1])

                # Display buttons
                col2.form_submit_button(
                    label='Login',
                    type='primary',
                    on_click=vault.login,
                    use_container_width=True
                )
                col3.form_submit_button(
                    label='Sign-up',
                    type='secondary',
                    on_click=self.display_sign_up_form,
                    kwargs={
                        'value': True
                    },
                    use_container_width=True
                )

            # Check login form-submission errors
            if st.session_state[setup.NAME][setup.AUTH_NAME]['login-error']:
                st.error(
                    body=st.session_state[setup.NAME][setup.AUTH_NAME]['login-error'],
                    icon='⛔'
                )

            # Reset login form-submission errors
            st.session_state[setup.NAME][setup.AUTH_NAME]['login-error'] = False

        # Display sign-up content
        else:

            # Display header & tagline
            st.header(header)
            st.write(tagline)
            st.write('')
            st.write('')

            # Display sign-up form
            with st.form('Sign-up', clear_on_submit=False):
                st.subheader('Sign-up')
                st.text_input(
                    label='First Name',
                    key='name',
                    placeholder='Enter your first name'
                )
                st.text_input(
                    label='Username',
                    key='username',
                    placeholder='Enter your email address'
                )
                st.text_input(
                    label='Password',
                    key='password0',
                    type='password',
                    placeholder='Enter your password'
                )
                st.text_input(
                    label='Re-enter password',
                    key='password1',
                    type='password',
                    placeholder='Enter your password again'
                )

                # Layout columns
                col1, col2, col3 = st.columns([1, 1, 1])

                # Display buttons
                col2.form_submit_button(
                    label='Sign-up',
                    type='primary',
                    on_click=vault.sign_up,
                    use_container_width=True
                )
                col3.form_submit_button(
                    label='Return to login',
                    type='secondary',
                    on_click=self.display_sign_up_form,
                    kwargs={
                        'value': False
                    },
                    use_container_width=True
                )

            # Check sign-up form-submission errors
            if st.session_state[setup.NAME][setup.AUTH_NAME]['sign-up-error']:
                st.warning(
                    body=st.session_state[setup.NAME][setup.AUTH_NAME]['sign-up-error'],
                    icon='⚠️'
                )

            # Reset sign-up form-submission errors
            st.session_state[setup.NAME][setup.AUTH_NAME]['sign-up-error'] = False

    def display_sign_up_form(
        self,
        value
    ):
        """ Displays the sign-up form.

        Parameters
        ----------
        value : `bool`
            Boolean value to that determines when to display the
                sign-up form.
        """

        # Switch form
        st.session_state[setup.NAME][setup.AUTH_NAME]['sign-up'] = value

        # Reset callback session state variables
        for key in [
            i for i in st.session_state[setup.NAME][setup.AUTH_NAME] if i not in (
                setup.AUTH_QUERY_INDEX,
                'sign-up'
            )
        ]:
            # Reset authentication status
            st.session_state[setup.NAME][setup.AUTH_NAME][key] = False

        # Reset log-in session state variables
        if value:
            del st.session_state['username']
            del st.session_state['password']

        # Reset sign-up session state variables
        else:
            del st.session_state['name']
            del st.session_state['username']
            del st.session_state['password0']
            del st.session_state['password1']
