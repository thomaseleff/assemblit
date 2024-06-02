"""
Information
---------------------------------------------------------------------
Name        : _selector.py
Location    : ~/_components
Author      : Tom Eleff
Published   : 2024-03-17
Revised on  : .

Description
---------------------------------------------------------------------
Contains the generic methods for a session-selector.
"""

import hashlib
import streamlit as st
from assemblit import setup, db
from assemblit.pages._components import _core, _key_value
from pytensils import utils


# Define core-component selector function(s)
def display_selector(
    db_name: str,
    table_name: str,
    query_index: str,
    scope_db_name: str,
    scope_query_index: str,
    options: list,
    index: int,
    disabled: bool
):
    """ Displays the database table drop-down options and default value as a selector.

    Parameters
    ----------
    db_name : `str`
        Name of the database to store the drop-down options & default value.
    table_name : `str`
        Name of the table within `db_name` to store the drop-down options & default value.
    query_index : `str`
        Name of the index within `db_name` & `table_name`. May only be one column.
    scope_db_name : `str`
        Name of the database that contains the associated scope for the selector
    scope_query_index : `str`
        Name of the index within `scope_db_name` & `table_name`. May only be one column.
    options: `list`
        The list containing the the drop-down options.
    index : `int`
        The index position of the value to be displayed as the default selection.
    disabled : `int`
        `True` or `False`, whether the selector is displayed disabled or not.
    """

    # Display the session-selector input object
    if st.session_state[setup.NAME][db_name][table_name]['selector']['kwargs']:
        st.selectbox(
            key='Selector:%s' % generate_selector_key(
                db_name=db_name,
                table_name=table_name,
                parameter=st.session_state[setup.NAME][db_name][table_name]['selector']['parameter']
            ),
            label=st.session_state[setup.NAME][db_name][table_name]['selector']['name'],
            options=options,
            index=index,
            placeholder=st.session_state[setup.NAME][db_name][table_name]['selector']['description'],
            on_change=set_query_index_value,
            kwargs={
                'db_name': db_name,
                'table_name': table_name,
                'query_index': query_index,
                'scope_db_name': scope_db_name,
                'scope_query_index': scope_query_index
            },
            disabled=disabled,
            label_visibility='collapsed',
            **st.session_state[setup.NAME][db_name][table_name]['selector']['kwargs']
        )

    else:
        st.selectbox(
            key='Selector:%s' % generate_selector_key(
                db_name=db_name,
                table_name=table_name,
                parameter=st.session_state[setup.NAME][db_name][table_name]['selector']['parameter']
            ),
            label=st.session_state[setup.NAME][db_name][table_name]['selector']['name'],
            options=options,
            index=index,
            placeholder=st.session_state[setup.NAME][db_name][table_name]['selector']['description'],
            on_change=set_query_index_value,
            kwargs={
                'db_name': db_name,
                'table_name': table_name,
                'query_index': query_index,
                'scope_db_name': scope_db_name,
                'scope_query_index': scope_query_index
            },
            disabled=disabled,
            label_visibility='collapsed'
        )


# Define function(s) for creating selectors
def generate_selector_key(
    db_name: str,
    table_name: str,
    parameter: str
):
    """ Generates a database table-specific key that contains the selector content.

    Parameters
    ----------
    db_name : `str`
        Name of the database to store the drop-down options & default value.
    table_name : `str`
        Name of the table within `db_name` to store the drop-down options & default value.
    parameter : `str`
        Name of the parameter.
    """

    return str('%s-%s-%s-%s').strip().lower() % (
        setup.NAME,
        str(db_name).strip().lower(),
        str(table_name).strip().lower(),
        str(parameter).strip().lower()
    )


# Define function(s) for standard selector database queries
def select_selector_dropdown_options(
    db_name: str,
    table_name: str,
    query_index: str,
    scope_db_name: str,
    scope_query_index: str
) -> list:
    """ Returns the drop-down options from the database table as a `list`.

    Parameters
    ----------
    db_name : `str`
        Name of the database to store the drop-down options & default value.
    table_name : `str`
        Name of the table within `db_name` to store the drop-down options & default value.
    query_index : `str`
        Name of the index within `db_name` & `table_name`. May only be one column.
    scope_db_name : `str`
        Name of the database that contains the associated scope for the selector
    scope_query_index : `str`
        Name of the index within `scope_db_name` & `table_name`. May only be one column.
    """

    # Initialize connection to the scope-database
    Scope = db.Handler(
        db_name=scope_db_name
    )

    # Initialize the connection to the session-selector database
    Db = db.Handler(
        db_name=db_name
    )

    # Select session-selector drop-down options
    if Scope.table_record_exists(
        table_name=table_name,
        filtr={
            'col': scope_query_index,
            'val': st.session_state[setup.NAME][scope_db_name][scope_query_index]
        }
    ):
        options = Db.select_table_column_value(
            table_name=table_name,
            col=st.session_state[setup.NAME][db_name][table_name]['selector']['parameter'],
            filtr={
                'col': query_index,
                'val': Scope.select_table_column_value(
                    table_name=table_name,
                    col=query_index,
                    filtr={
                        'col': scope_query_index,
                        'val': st.session_state[setup.NAME][scope_db_name][scope_query_index]
                    },
                    multi=True
                )
            },
            multi=True
        )

    else:
        options = []

    return options


def select_selector_default_value(
    db_name: str,
    table_name: str,
    query_index: str,
    scope_db_name: str,
    scope_query_index: str,
    options: list
) -> int:
    """ Selects the default value and returns the index position of the value in `options` as an `int`.

    Parameters
    ----------
    db_name : `str`
        Name of the database to store the drop-down options & default value.
    table_name : `str`
        Name of the table within `db_name` to store the drop-down options & default value.
    query_index : `str`
        Name of the index within `db_name` & `table_name`. May only be one column.
    scope_db_name : `str`
        Name of the database that contains the associated scope for the selector
    scope_query_index : `str`
        Name of the index within `scope_db_name` & `table_name`. May only be one column.
    options: `list`
        The list containing the the drop-down options.
    """

    # Select the index of the default drop-down selection
    if options:
        try:
            index = options.index(st.session_state[setup.NAME][db_name]['name'])

            # Set query index value
            st.session_state[setup.NAME][db_name]['name'] = options[index]
            st.session_state[setup.NAME][db_name][query_index] = select_query_index_value(
                db_name=db_name,
                table_name=table_name,
                query_index=query_index,
                scope_db_name=scope_db_name,
                scope_query_index=scope_query_index,
                filtr={
                    'col': st.session_state[setup.NAME][db_name][table_name]['selector']['parameter'],
                    'val': options[index]
                }
            )
        except ValueError:
            index = 0

            # Set query index value
            st.session_state[setup.NAME][db_name]['name'] = options[index]
            st.session_state[setup.NAME][db_name][query_index] = select_query_index_value(
                db_name=db_name,
                table_name=table_name,
                query_index=query_index,
                scope_db_name=scope_db_name,
                scope_query_index=scope_query_index,
                filtr={
                    'col': st.session_state[setup.NAME][db_name][table_name]['selector']['parameter'],
                    'val': options[index]
                }
            )
    else:
        index = 0

    return index


def set_query_index_value(
    db_name: str,
    table_name: str,
    query_index: str,
    scope_db_name: str,
    scope_query_index: str
):
    """ Sets the session state name and query index value to the selected value.

    Parameters
    ----------
    db_name : `str`
        Name of the database to store the drop-down options & default value.
    table_name : `str`
        Name of the table within `db_name` to store the drop-down options & default value.
    query_index : `str`
        Name of the index within `db_name` & `table_name`. May only be one column.
    scope_db_name : `str`
        Name of the database that contains the associated scope for the selector
    scope_query_index : `str`
        Name of the index within `scope_db_name` & `table_name`. May only be one column.
    """

    # Retrieve selected value
    selected_value = st.session_state[
        'Selector:%s' % generate_selector_key(
            db_name=db_name,
            table_name=table_name,
            parameter=st.session_state[setup.NAME][db_name][table_name]['selector']['parameter']
        )
    ]

    # Update session state
    if st.session_state[setup.NAME][db_name]['name'] != selected_value:
        st.session_state[setup.NAME][db_name]['name'] = selected_value

        st.session_state[setup.NAME][db_name][query_index] = select_query_index_value(
            db_name=db_name,
            table_name=table_name,
            query_index=query_index,
            scope_db_name=scope_db_name,
            scope_query_index=scope_query_index,
            filtr={
                'col': st.session_state[setup.NAME][db_name][table_name]['selector']['parameter'],
                'val': selected_value
            }
        )


def select_query_index_value(
    db_name: str,
    table_name: str,
    query_index: str,
    scope_db_name: str,
    scope_query_index: str,
    filtr: dict
) -> str:
    """ Returns the query index value from a filtered database table.

    Parameters
    ----------
    db_name : `str`
        Name of the database to store the drop-down options & default value.
    table_name : `str`
        Name of the table within `db_name` to store the drop-down options & default value.
    query_index : `str`
        Name of the index within `db_name` & `table_name`. May only be one column.
    scope_db_name : `str`
        Name of the database that contains the associated scope for the selector
    scope_query_index : `str`
        Name of the index within `scope_db_name` & `table_name`. May only be one column.
    filtr : `dict`
        Dictionary object containing the column `col` and value
            `val` to filter `table_name`. If the filtered table
            returns more than one record, a `ValueError` is raised.

            e.g., {
                'col' : 'id',
                'val' : '1'
            }
    """

    # Initialize connection to the scope-database
    Scope = db.Handler(
        db_name=scope_db_name
    )

    # Initialize connection to the session-selector database
    Db = db.Handler(
        db_name=db_name
    )

    values = Db.cursor.execute(
        """
        SELECT %s
            FROM %s
                WHERE %s IN (%s)
                    AND %s = '%s';
        """ % (
            str(query_index),
            str(table_name),
            str(query_index),
            ', '.join(
                ["'%s'" % (i) for i in Scope.select_table_column_value(
                    table_name=table_name,
                    col=query_index,
                    filtr={
                        'col': scope_query_index,
                        'val': st.session_state[setup.NAME][scope_db_name][scope_query_index]
                    },
                    return_dtype='str',
                    multi=True
                )]
            ),
            str(filtr['col']),
            db.normalize(string=filtr['val'])
        )
    ).fetchall()

    return utils.as_type(
        [i[0] for i in values][0],
        return_dtype='str'
    )


# Define function(s) for handling call-backs
def display_session_setup_form(
    db_name: str,
    table_name: str,
    value: bool
):
    """ Sets the session state flag to display the sessions-set-up form.

    Parameters
    ----------
    value : `bool`
        Boolean value to that determines when to display the
            sessions-set-up form.
    """

    # Switch form
    st.session_state[setup.NAME][db_name][table_name]['set-up'] = value


# Define function(s) for managing selector database setting(s)
def create_session(
    db_name: str,
    table_name: str,
    query_index: str,
    scope_db_name: str,
    scope_query_index: str,
    response: dict
):
    """ Inserts a new session into the database table containing the settings parameters & values
    within the form `response`.

    Parameters
    ----------
    db_name : `str`
        Name of the database to store the drop-down options & default value.
    table_name : `str`
        Name of the table within `db_name` to store the drop-down options & default value.
    query_index : `str`
        Name of the index within `db_name` & `table_name`. May only be one column.
    scope_db_name : `str`
        Name of the database that contains the associated scope for the selector
    scope_query_index : `str`
        Name of the index within `scope_db_name` & `table_name`. May only be one column.
    response : `dict`
        Dictionary object containing the form responses.
    """

    # Initialize connection to the scope-database
    Scope = db.Handler(
        db_name=scope_db_name
    )

    # Initialize connection to the session-selector database
    Db = db.Handler(
        db_name=db_name
    )

    if (
        _key_value.get_key_value_pair_parameters(
            db_name=db_name,
            table_name=table_name
        ) == list(response.keys())
        and ('' not in [str(i).strip() for i in response.values()])
    ):

        # Create an id from query index values
        string_to_hash = ''.join(
            [str(st.session_state[setup.NAME][scope_db_name][scope_query_index])]
            + [str(response[st.session_state[setup.NAME][db_name][table_name]['selector']['parameter']])]
        )

        # Generate id
        id = hashlib.md5(
            string_to_hash.lower().encode('utf-8')
        ).hexdigest()

        # Check if the id already exists
        try:
            ids = Scope.select_table_column_value(
                table_name=table_name,
                col=query_index,
                filtr={
                    'col': scope_query_index,
                    'val': st.session_state[setup.NAME][scope_db_name][scope_query_index]
                },
                multi=True
            )
        except db.NullReturnValue:
            ids = []

        if id not in ids:

            # Add to user database
            Scope.insert(
                table_name=table_name,
                values={
                    scope_query_index: (
                        st.session_state[setup.NAME][scope_db_name][scope_query_index]
                    ),
                    query_index: id
                }
            )

            # Create dictionary of columns and values to insert
            values = {query_index: id}
            values.update(response)

            # Add to studies database
            Db.insert(
                table_name=table_name,
                values=values
            )

            # Log successes
            st.session_state[setup.NAME][db_name]['successes'] = (
                st.session_state[setup.NAME][db_name]['successes'] + [
                    'The entry was created successfully.'
                ]
            )

            # Set session state
            st.session_state[setup.NAME][db_name]['name'] = response[
                st.session_state[setup.NAME][db_name][table_name]['selector']['parameter']
            ]
            st.session_state[setup.NAME][db_name][query_index] = (
                id
            )

        else:

            # Log error
            st.session_state[setup.NAME][db_name]['errors'] = (
                st.session_state[setup.NAME][db_name]['errors'] + [
                    'The entry already exists.'
                ]
            )

    else:

        # Log error
        st.session_state[setup.NAME][db_name]['errors'] = (
            st.session_state[setup.NAME][db_name]['errors'] + [
                """
                    The entry is incomplete. Please fill out the entire form.
                """
            ]
        )


def update_session(
    db_name: str,
    table_name: str,
    query_index: str,
    scope_db_name: str,
    scope_query_index: str,
    response: dict
):
    """ Updates an existing session within the database table with the settings parameters & values
    within the form `response`.

    Parameters
    ----------
    db_name : `str`
        Name of the database to store the drop-down options & default value.
    table_name : `str`
        Name of the table within `db_name` to store the drop-down options & default value.
    query_index : `str`
        Name of the index within `db_name` & `table_name`. May only be one column.
    scope_db_name : `str`
        Name of the database that contains the associated scope for the selector
    scope_query_index : `str`
        Name of the index within `scope_db_name` & `table_name`. May only be one column.
    response : `dict`
        Dictionary object containing the form responses.
    """

    # Initialize connection to the session-selector database
    Db = db.Handler(
        db_name=db_name
    )

    # Check for existing session-selector values
    if response[st.session_state[setup.NAME][db_name][table_name]['selector']['parameter']] not in (
        select_selector_dropdown_options(
            db_name=db_name,
            table_name=table_name,
            query_index=query_index,
            scope_db_name=scope_db_name,
            scope_query_index=scope_query_index
        )
    ):

        # Check for empty form entries
        if '' not in [str(i).strip() for i in response.values()]:

            # Update session-selector parameters
            for parameter in list(response.keys()):

                if Db.table_record_exists(
                    table_name=table_name,
                    filtr={
                        'col': query_index,
                        'val': st.session_state[setup.NAME][db_name][query_index]
                    }
                ):

                    try:
                        Db.update(
                            table_name=table_name,
                            values={
                                'col': parameter,
                                'val': response[parameter]
                            },
                            filtr={
                                'col': query_index,
                                'val': st.session_state[setup.NAME][db_name][query_index]
                            }
                        )

                        # Log success
                        st.session_state[setup.NAME][db_name]['successes'] = (
                            st.session_state[setup.NAME][db_name]['successes'] + [
                                """
                                {%s} successfully changed to '%s'.
                                """ % (
                                    parameter,
                                    response[parameter]
                                )
                            ]
                        )

                    except ValueError as e:

                        # Log error
                        st.session_state[setup.NAME][db_name]['errors'] = (
                            st.session_state[setup.NAME][db_name]['errors'] + [str(e)]
                        )

                else:

                    # Log error
                    st.session_state[setup.NAME][db_name]['errors'] = (
                        st.session_state[setup.NAME][db_name]['errors'] + [
                            'No table record found.'
                        ]
                    )

        else:

            # Log error
            st.session_state[setup.NAME][db_name]['errors'] = (
                st.session_state[setup.NAME][db_name]['errors'] + [
                    """
                        The entry is incomplete. Please fill out the entire form.
                    """
                ]
            )

    else:

        # Log error
        st.session_state[setup.NAME][db_name]['errors'] = (
            st.session_state[setup.NAME][db_name]['errors'] + [
                "The entry {%s} already exists. Please enter a unique value for {%s}." % (
                    response[st.session_state[setup.NAME][db_name][table_name]['selector']['parameter']],
                    st.session_state[setup.NAME][db_name][table_name]['selector']['name']
                )
            ]
        )


def delete_session(
    session_id: str
):
    """ Deletes all database table information associated with the selected session.

    Parameters
    ----------
    session_id : `str`
        Session ID of the selected session.
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

    # Build database table objects to remove sessions from the users database
    users_db_query_index_objects_to_delete = Users.build_database_table_objects_to_delete(
        table_names=Users.select_all_tables_with_column_name(
            col=setup.SESSIONS_DB_QUERY_INDEX
        ),
        query_index=setup.SESSIONS_DB_QUERY_INDEX,
        query_index_values=[session_id]
    )

    # Build database table objects to remove sessions from the sessions database
    sessions_db_query_index_objects_to_delete = Sessions.build_database_table_objects_to_delete(
        table_names=Sessions.select_all_tables_with_column_name(
            col=setup.SESSIONS_DB_QUERY_INDEX
        ),
        query_index=setup.SESSIONS_DB_QUERY_INDEX,
        query_index_values=[session_id]
    )

    # Get all orphaned data-db-query-index values
    data_to_delete = Sessions.create_database_table_dependencies(
        table_names=Sessions.select_all_tables_with_column_name(
            col=setup.DATA_DB_QUERY_INDEX
        ),
        query_index=setup.SESSIONS_DB_QUERY_INDEX,
        query_index_value=session_id,
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

    # Reset session state
    _core.initialize_session_state_database_defaults(
        db_name=setup.SESSIONS_DB_NAME,
        defaults=setup.SESSIONS_DEFAULTS
    )
    _core.initialize_session_state_database_defaults(
        db_name=setup.DATA_DB_NAME,
        defaults=setup.DATA_DEFAULTS
    )
