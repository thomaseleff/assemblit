"""
Information
---------------------------------------------------------------------
Name        : vault.py
Location    : ~/
Author      : Tom Eleff
Published   : 2024-03-17
Revised on  : .

Description
---------------------------------------------------------------------
Utility functions for authenticating, creating, updating and deleting
user-credentials.
"""

import hashlib
import datetime
import argon2
from argon2 import PasswordHasher
from email_validator import validate_email, EmailNotValidError
import streamlit as st
from getstreamy import setup, db
from getstreamy.components import _core


# Define generic authentication function(s)
def authenticate(
    username: str,
    password: str
) -> dict:
    """ Authenticates the log-in credentials of a user and returns the associated
    user name and id as a `dict`.

    Parameters
    ----------
    username : `str`
        Username credential as a valid email. If an invalid email is provided,
            an `InvalidEmail` is raised. If the user does not exist,
            a `UserNotFound` is raised.
    password : `str`
        Password credential. If the incorrect password is provided,
            an `IncorrectPassword` is raised.
    """

    # Escape the username and password
    username = username.strip()
    password = password.strip()

    # Check that the email address is valid
    try:
        email = validate_email(username, check_deliverability=False)
        username = email.normalized

        # Initialize Argon2id password hasher class
        Argon2id = PasswordHasher()

        # Initialize connection to the users database
        Users = db.Handler(
            db_name=setup.USERS_DB_NAME
        )

        # Create table in database
        Users.create_table(
            table_name='credentials',
            cols=(
                [
                    setup.USERS_DB_QUERY_INDEX,
                    'username',
                    'password',
                    'first_name'
                ]
            )
        )

        # Check if the user exists
        if Users.table_record_exists(
            table_name='credentials',
            filtr={
                'col': 'username',
                'val': username
            }
        ):

            # Check if the user provided the correct password
            try:
                Argon2id.verify(
                        Users.select_table_column_value(
                            table_name='credentials',
                            col='password',
                            filtr={
                                'col': 'username',
                                'val': username
                            }
                        ),
                        password
                )

                # TO DO, Update the password and update the database

                # Return the first name and user id
                return {
                    'name': Users.select_table_column_value(
                        table_name='credentials',
                        col='first_name',
                        filtr={
                            'col': 'username',
                            'val': username
                        }
                    ),
                    setup.USERS_DB_QUERY_INDEX: (
                        Users.select_table_column_value(
                            table_name='credentials',
                            col=setup.USERS_DB_QUERY_INDEX,
                            filtr={
                                'col': 'username',
                                'val': username
                            }
                        )
                    )
                }

            except argon2.exceptions.VerifyMismatchError:

                raise IncorrectPassword(
                    'Incorrect password.'
                )

        else:

            raise UserNotFound(
                'User {%s} not found.' % (
                    username
                )
            )

    except EmailNotValidError as e:
        raise InvalidEmail(e)


# Define generic database account management function(s)
def add_credentials(
    first_name: str,
    username: str,
    password0: str,
    password1: str
) -> dict:
    """ Adds a new user and credentials returns the associated user name and id as a `dict`.

    Parameters
    ----------
    username : `str`
        Username credential as a valid email. If an invalid email is provided,
            an `InvalidEmail` is raised. If the user already exists,
            a `UserAlreadyExists` is raised.
    password0 : `str`
        Password credential.
    password1 : `str`
        Repeated password credential, must match `password0`. If an invalid password is
            provided then a `PasswordsDoNotMatch` is raised.
    """

    # Escape the first name, username and password
    first_name = first_name.strip()
    username = username.strip()
    password0 = password0.strip()
    password1 = password1.strip()

    # Check that the email address is valid
    try:
        email = validate_email(username, check_deliverability=True)
        username = email.normalized

        # Check if the two passwords match
        if password0 == password1:

            # Initialize Argon2id password hasher class
            Argon2id = PasswordHasher()

            # Initialize connection to the users database
            Users = db.Handler(
                db_name=setup.USERS_DB_NAME
            )

            # Create table in database
            Users.create_table(
                table_name='credentials',
                cols=(
                    [
                        setup.USERS_DB_QUERY_INDEX,
                        'username',
                        'password',
                        'first_name'
                    ]
                )
            )

            # Generate a password hashkey
            hashkey = Argon2id.hash(password=password0)

            # Generate a user-id
            user_id = hashlib.md5(
                ''.join([
                    str(datetime.datetime.now()),
                    str(username)
                ]).encode('utf-8')
            ).hexdigest()

            # Add the user
            try:
                Users.insert(
                    table_name='credentials',
                    values={
                        setup.USERS_DB_QUERY_INDEX: user_id,
                        'username': username,
                        'password': hashkey,
                        'first_name': first_name
                    },
                    validate={
                        'col': 'username',
                        'val': username
                    }
                )

                return {
                    'name': first_name,
                    setup.USERS_DB_QUERY_INDEX: user_id
                }

            except ValueError:

                raise UserAlreadyExists(
                    'The user already exists.'
                )

        else:
            raise PasswordsDoNotMatch(
                'The passwords do not match.'
            )

    except EmailNotValidError as e:
        raise InvalidEmail(e)


def update_credentials(
    response: dict
):

    # Apply form submission to the database
    if response:

        # Update username
        if 'change_username' in response:
            try:
                update_username(
                    user_id=(
                        st.session_state[setup.NAME][setup.USERS_DB_NAME][setup.USERS_DB_QUERY_INDEX]
                    ),
                    username=response['change_username']
                )

                # Log success
                st.session_state[setup.NAME][setup.USERS_DB_NAME]['successes'] = (
                    st.session_state[setup.NAME][setup.USERS_DB_NAME]['successes'] + [
                        """
                        Username successfully changed to %s.
                        """ % (response['change_username'])
                    ]
                )

            except UserAlreadyExists as e:

                # Log error
                st.session_state[setup.NAME][setup.USERS_DB_NAME]['errors'] = (
                    st.session_state[setup.NAME][setup.USERS_DB_NAME]['errors'] + [str(e)]
                )

            except InvalidEmail as e:

                # Log error
                st.session_state[setup.NAME][setup.USERS_DB_NAME]['errors'] = (
                    st.session_state[setup.NAME][setup.USERS_DB_NAME]['errors'] + [str(e)]
                )

        # Update password
        if (
            ('change_password0' in response)
            and ('change_password1' in response)
        ):
            try:
                update_password(
                    user_id=(
                        st.session_state[setup.NAME][setup.USERS_DB_NAME][setup.USERS_DB_QUERY_INDEX]
                    ),
                    password0=response['change_password0'],
                    password1=response['change_password1']
                )

                # Log success
                st.session_state[setup.NAME][setup.USERS_DB_NAME]['successes'] = (
                    st.session_state[setup.NAME][setup.USERS_DB_NAME]['successes'] + [
                        """
                        Password successfully changed.
                        """
                    ]
                )

            except UserAlreadyExists as e:

                # Log error
                st.session_state[setup.NAME][setup.USERS_DB_NAME]['errors'] = (
                    st.session_state[setup.NAME][setup.USERS_DB_NAME]['errors'] + [str(e)]
                )

            except PasswordsDoNotMatch as e:

                # Log error
                st.session_state[setup.NAME][setup.USERS_DB_NAME]['errors'] = (
                    st.session_state[setup.NAME][setup.USERS_DB_NAME]['errors'] + [str(e)]
                )

        if 'delete_account' in response:

            # Delete account
            delete_account(
                user_id=(
                    st.session_state[setup.NAME][setup.USERS_DB_NAME][setup.USERS_DB_QUERY_INDEX]
                )
            )

            # Return to home-page
            st.switch_page(st.session_state[setup.NAME]['pages']['home'])


def update_username(
    user_id: str,
    username: str
):
    """ Updates the username of an existing user.

    Parameters
    ----------
    user_id : `str`
        User ID of the existing user.
    username : `str`
        Username credential as a valid email. If an invalid email is provided,
            an `InvalidEmail` is raised. If the user already exists,
            a `UserAlreadyExists` is raised.
    """

    # Escape the username
    username = username.strip()

    # Check that the email address is valid
    try:
        email = validate_email(username, check_deliverability=True)
        username = email.normalized

        # Initialize connection to the users database
        Users = db.Handler(
            db_name=setup.USERS_DB_NAME
        )

        # Check if the user exists
        if not Users.table_record_exists(
            table_name='credentials',
            filtr={
                'col': 'username',
                'val': username
            }
        ):

            # Update username
            Users.update(
                table_name='credentials',
                values={
                    'col': 'username',
                    'val': username
                },
                filtr={
                    'col': setup.USERS_DB_QUERY_INDEX,
                    'val': user_id
                }
            )

        else:
            raise UserAlreadyExists(
                ' '.join([
                    'The email address entered',
                    'is already associated with an account.'
                ])
            )

    except EmailNotValidError as e:
        raise InvalidEmail(e)


def update_password(
    user_id: str,
    password0: str,
    password1: str,
):
    """ Updates the password of an existing user.

    Parameters
    ----------
    user_id : `str`
        User ID of the existing user.
    password0 : `str`
        Password credential.
    password1 : `str`
        Repeated password credential, must match `password0`. If an invalid password is
            provided then a `PasswordsDoNotMatch` is raised.
    """

    # Escape the password
    password0 = password0.strip()
    password1 = password1.strip()

    # Check if the two passwords match
    if password0 == password1:

        # Initialize Argon2id password hasher class
        Argon2id = PasswordHasher()

        # Initialize connection to the users database
        Users = db.Handler(
            db_name=setup.USERS_DB_NAME
        )

        # Generate a password hashkey
        hashkey = Argon2id.hash(password=password0)

        # Add the user
        Users.update(
            table_name='credentials',
            values={
                'col': 'password',
                'val': hashkey
            },
            filtr={
                'col': setup.USERS_DB_QUERY_INDEX,
                'val': user_id
            }
        )

    else:
        raise PasswordsDoNotMatch(
            'The passwords do not match.'
        )


def delete_account(
    user_id: str
):
    """ Deletes all database table information associated with the selected user.

    Parameters
    ----------
    user_id : `str`
        User ID of the selected user.
    """

    # Initialize connection to the users database
    Users = db.Handler(
        db_name=setup.USERS_DB_NAME
    )

    # Initialize connection to the sessions database
    Sessions = db.Handler(
        db_name=setup.SESSIONS_DB_NAME
    )

    # Initialize connection to the data-ingestion database
    Data = db.Handler(
        db_name=setup.DATA_DB_NAME
    )

    # Build database table objects to remove users from the users database
    users_db_query_index_objects_to_delete = Users.build_database_table_objects_to_delete(
        table_names=Users.select_all_tables_with_column_name(
            col=setup.USERS_DB_QUERY_INDEX
        ),
        query_index=setup.USERS_DB_QUERY_INDEX,
        query_index_values=[user_id]
    )

    # Get all orphaned sessions-db-query-index values
    sessions_to_delete = Users.create_database_table_dependencies(
        table_names=Users.select_all_tables_with_column_name(
            col=setup.SESSIONS_DB_QUERY_INDEX
        ),
        query_index=setup.USERS_DB_QUERY_INDEX,
        query_index_value=user_id,
        dependent_query_index=setup.SESSIONS_DB_QUERY_INDEX
    )

    # Build database table objects to remove sessions from the sessions database
    if sessions_to_delete:
        sessions_db_query_index_objects_to_delete = Sessions.build_database_table_objects_to_delete(
            table_names=Sessions.select_all_tables_with_column_name(
                col=setup.SESSIONS_DB_QUERY_INDEX
            ),
            query_index=setup.SESSIONS_DB_QUERY_INDEX,
            query_index_values=sessions_to_delete
        )

        # Get all orphaned data-db-query-index values
        data_to_delete = Sessions.create_database_table_dependencies(
            table_names=Sessions.select_all_tables_with_column_name(
                col=setup.DATA_DB_QUERY_INDEX
            ),
            query_index=setup.SESSIONS_DB_QUERY_INDEX,
            query_index_value=sessions_to_delete,
            dependent_query_index=setup.DATA_DB_QUERY_INDEX
        )

        # Build database table objects to remove datasets from the data database
        if data_to_delete:
            data_db_query_index_objects_to_delete = Data.build_database_table_objects_to_delete(
                table_names=Data.select_all_tables_with_column_name(
                    col=setup.DATA_DB_QUERY_INDEX
                ),
                query_index=setup.DATA_DB_QUERY_INDEX,
                query_index_values=data_to_delete
            )

            # Drop all data-ingestion database tables
            for table in data_to_delete:
                Data.drop_table(
                    table_name=table
                )

            # Delete all data-ingestion database table values
            Data.delete(
                database_table_object=data_db_query_index_objects_to_delete
            )

        # Delete all sessions database table values
        Sessions.delete(
            database_table_object=sessions_db_query_index_objects_to_delete
        )

    # Delete all user database table values
    Users.delete(
        database_table_object=users_db_query_index_objects_to_delete
    )

    # Logout to reset the session state
    logout()


# Define generic user-session mangement function(s)
def login():
    """ Handles login requests.
    """

    # Authenticate
    try:
        st.session_state[setup.NAME][setup.USERS_DB_NAME] = authenticate(
            username=st.session_state['username'],
            password=st.session_state['password']
        )

    except IncorrectPassword:
        st.session_state[setup.NAME][setup.AUTH_NAME]['login-error'] = (
            'Incorrect username and/or password.'
        )

    except UserNotFound:
        st.session_state[setup.NAME][setup.AUTH_NAME]['login-error'] = (
            'Incorrect username and/or password.'
        )

    except InvalidEmail as e:
        st.session_state[setup.NAME][setup.AUTH_NAME]['login-error'] = str(e)

    # Set authentication status
    if not st.session_state[setup.NAME][setup.AUTH_NAME]['login-error']:
        st.session_state[setup.NAME][setup.AUTH_NAME][setup.AUTH_QUERY_INDEX] = True
    else:
        st.session_state[setup.NAME][setup.AUTH_NAME][setup.AUTH_QUERY_INDEX] = False

    # Reset log-in session state variables
    del st.session_state['username']
    del st.session_state['password']


def sign_up():
    """ Handles sign-up requests.
    """

    # Authenticate
    try:
        st.session_state[setup.NAME][setup.USERS_DB_NAME] = add_credentials(
            first_name=st.session_state['name'],
            username=st.session_state['username'],
            password0=st.session_state['password0'],
            password1=st.session_state['password1']
        )

    except UserAlreadyExists:
        st.session_state[setup.NAME][setup.AUTH_NAME]['sign-up-error'] = (
            'User already exists. Please login instead.'
        )

    except PasswordsDoNotMatch:
        st.session_state[setup.NAME][setup.AUTH_NAME]['sign-up-error'] = (
            'Passwords do not match.'
        )

    except InvalidEmail as e:
        st.session_state[setup.NAME][setup.AUTH_NAME]['sign-up-error'] = str(e)

    # Set authentication status
    if not st.session_state[setup.NAME][setup.AUTH_NAME]['sign-up-error']:
        st.session_state[setup.NAME][setup.AUTH_NAME][setup.AUTH_QUERY_INDEX] = True
    else:
        st.session_state[setup.NAME][setup.AUTH_NAME][setup.AUTH_QUERY_INDEX] = False

    # Reset sign-up session state variables
    del st.session_state['name']
    del st.session_state['username']
    del st.session_state['password0']
    del st.session_state['password1']


def logout():
    """ Handles logout requests.
    """

    # Reset the session state
    del st.session_state[setup.NAME]

    # Initialize session state defaults
    _core.initialize_session_state_defaults()


# Define authentication & account management exception classes
class IncorrectPassword(Exception):
    pass


class UserNotFound(Exception):
    pass


class InvalidEmail(Exception):
    pass


class UserAlreadyExists(Exception):
    pass


class PasswordsDoNotMatch(Exception):
    pass


class AuthenticationNotRequired(Exception):
    pass
