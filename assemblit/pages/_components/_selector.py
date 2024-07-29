"""
Information
---------------------------------------------------------------------
Name        : _selector.py
Location    : ~/pages/_components

Description
---------------------------------------------------------------------
Contains the generic methods for a session-selector.
"""

from typing import List
import hashlib
import streamlit as st
from assemblit import setup
from assemblit.blocks.structures import Setting, Selector
from assemblit.pages._components import _core, _key_value
from assemblit.database import _generic, users, sessions, data
from assemblit.database._structures import Filter, Value, Row
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
    selector: Selector = st.session_state[setup.NAME][db_name][table_name]['selector']

    st.selectbox(
        key='Selector:%s' % generate_selector_key(
            db_name=db_name,
            table_name=table_name,
            parameter=selector.parameter
        ),
        label=selector.name,
        options=options,
        index=index,
        placeholder=selector.description,
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

    return str('%s-%s-%s-%s').lower() % (
        setup.NAME.strip(),
        str(db_name).strip(),
        str(table_name).strip(),
        str(parameter).strip()
    )


def parse_selector(
    parameter: str,
    settings: List[Setting]
) -> Selector:
    """ Returns a `Selector` object from a `Settings` object when passed the name of a parameter within the `Settings` object.

    Parameters
    ----------
    parameter: `str`
        Name of the parameter.
    settings : `list[Setting]`
        List of `assemblit.app.structures.Setting` objects containing the setting(s) parameters & values.
    """

    # Validate the selector-parameter
    if parameter.strip().lower() not in [setting.parameter.strip().lower() for setting in settings]:
        raise ValueError('The parameter {%s} does not exist within the settings.' % parameter.strip())

    # Parse the selector object
    return [setting.to_selector() for setting in settings if setting.parameter == parameter][0]


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
    Scope = _generic.Connection(
        db_name=scope_db_name,
        dir_name=setup.DB_DIR
    )

    # Initialize the connection to the session-selector database
    Database = _generic.Connection(
        db_name=db_name,
        dir_name=setup.DB_DIR
    )

    # Select session-selector drop-down options
    selector: Selector = st.session_state[setup.NAME][db_name][table_name]['selector']

    if Scope.table_record_exists(
        table_name=table_name,
        filtr=Filter(
            col=scope_query_index,
            val=st.session_state[setup.NAME][scope_db_name][scope_query_index]
        )
    ):
        options = Database.select_table_column_value(
            table_name=table_name,
            col=selector.parameter,
            filtr=Filter(
                col=query_index,
                val=Scope.select_table_column_value(
                    table_name=table_name,
                    col=query_index,
                    filtr=Filter(
                        col=scope_query_index,
                        val=st.session_state[setup.NAME][scope_db_name][scope_query_index]
                    ),
                    multi=True
                )
            ),
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
    selector: Selector = st.session_state[setup.NAME][db_name][table_name]['selector']

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
                filtr=Filter(
                    col=selector.parameter,
                    val=options[index]
                )
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
                filtr=Filter(
                    col=selector.parameter,
                    val=options[index]
                )
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
    selector: Selector = st.session_state[setup.NAME][db_name][table_name]['selector']
    selected_value = st.session_state[
        'Selector:%s' % generate_selector_key(
            db_name=db_name,
            table_name=table_name,
            parameter=selector.parameter
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
            filtr=Filter(
                col=selector.parameter,
                val=selected_value
            )
        )


def select_query_index_value(
    db_name: str,
    table_name: str,
    query_index: str,
    scope_db_name: str,
    scope_query_index: str,
    filtr: Filter
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
    filtr : `Filter`
        `assemblit.database.structures.Filter` object containing the column `col` and value
            `val` to filter `table_name`. If the filtered table
            returns more than one record, a `ValueError` is raised.

            e.g., {
                'col' : 'id',
                'val' : '1'
            }
    """

    # Initialize connection to the scope-database
    Scope = _generic.Connection(
        db_name=scope_db_name,
        dir_name=setup.DB_DIR
    )

    # Initialize connection to the session-selector database
    Database = _generic.Connection(
        db_name=db_name,
        dir_name=setup.DB_DIR
    )

    values = Database.conn.cursor().execute(
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
                    filtr=Filter(
                        col=scope_query_index,
                        val=st.session_state[setup.NAME][scope_db_name][scope_query_index]
                    ),
                    return_dtype='str',
                    multi=True
                )]
            ),
            str(filtr.col),
            _generic.normalize(string=filtr.val)
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
    Scope = _generic.Connection(
        db_name=scope_db_name,
        dir_name=setup.DB_DIR
    )

    # Initialize connection to the session-selector database
    Database = _generic.Connection(
        db_name=db_name,
        dir_name=setup.DB_DIR
    )

    if (
        _key_value.get_key_value_pair_parameters(
            db_name=db_name,
            table_name=table_name
        ) == list(response.keys())
        and ('' not in [str(i).strip() for i in response.values()])
    ):

        # Create an id from query index values
        selector: Selector = st.session_state[setup.NAME][db_name][table_name]['selector']

        string_to_hash = ''.join(
            [str(st.session_state[setup.NAME][scope_db_name][scope_query_index])]
            + [str(response[selector.parameter])]
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
                filtr=Filter(
                    col=scope_query_index,
                    val=st.session_state[setup.NAME][scope_db_name][scope_query_index]
                ),
                multi=True
            )
        except _generic.NullReturnValue:
            ids = []

        if id not in ids:

            # Add to user database
            Scope.insert(
                table_name=table_name,
                row=Row(
                    cols=[scope_query_index, query_index],
                    vals=[st.session_state[setup.NAME][scope_db_name][scope_query_index], id]
                )
            )

            # Create dictionary of columns and values to insert
            values = {query_index: id}
            values.update(response)

            # Add to studies database
            Database.insert(
                table_name=table_name,
                row=Row(
                    cols=list(values.keys()),
                    vals=list(values.values())
                )
            )

            # Log successes
            st.session_state[setup.NAME][db_name]['successes'] = (
                st.session_state[setup.NAME][db_name]['successes'] + [
                    'The entry was created successfully.'
                ]
            )

            # Set session state
            st.session_state[setup.NAME][db_name]['name'] = response[selector.parameter]
            st.session_state[setup.NAME][db_name][query_index] = id

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
                'The entry is incomplete. Please fill out the entire form.'
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
    Database = _generic.Connection(
        db_name=db_name,
        dir_name=setup.DB_DIR
    )

    # Check for existing session-selector values
    selector: Selector = st.session_state[setup.NAME][db_name][table_name]['selector']

    if response[selector.parameter] not in (
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

                if Database.table_record_exists(
                    table_name=table_name,
                    filtr=Filter(
                        col=query_index,
                        val=st.session_state[setup.NAME][db_name][query_index]
                    )
                ):

                    try:
                        Database.update(
                            table_name=table_name,
                            value=Value(
                                col=parameter,
                                val=response[parameter]
                            ),
                            filtr=Filter(
                                col=query_index,
                                val=st.session_state[setup.NAME][db_name][query_index]
                            )
                        )

                        # Log success
                        st.session_state[setup.NAME][db_name]['successes'] = (
                            st.session_state[setup.NAME][db_name]['successes'] + [
                                "{%s} successfully changed to '%s'." % (
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
                    'The entry is incomplete. Please fill out the entire form.'
                ]
            )

    else:

        # Log error
        st.session_state[setup.NAME][db_name]['errors'] = (
            st.session_state[setup.NAME][db_name]['errors'] + [
                "The entry {%s} already exists. Please enter a unique value for {%s}." % (
                    response[selector.parameter],
                    selector.name
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
    Users = users.Connection()

    # Initialize connection to the sessions database
    Sessions = sessions.Connection()

    # Initialize connection to the data-ingestion database
    Data = data.Connection()

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
            tables=data_db_query_index_objects_to_delete
        )

    # Delete all sessions database table values
    Sessions.delete(
        tables=sessions_db_query_index_objects_to_delete
    )

    # Delete all user database table values
    Users.delete(
        tables=users_db_query_index_objects_to_delete
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
