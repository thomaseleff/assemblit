"""
Information
---------------------------------------------------------------------
Name        : _selector.py
Location    : ~/
Author      : Tom Eleff
Published   : 2024-02-19
Revised on  : .

Description
---------------------------------------------------------------------
Contains the generic methods for a session-selector.
"""

import hashlib
import streamlit as st
from getstreamy import setup, db
from getstreamy.components import _key_value


# Define core-component key-value pair function(s)
def display_selector(
    db_name: str,
    table_name: str,
    query_index: str,
    options: list,
    index: int
):
    """ Displays the database table drop-down options and default value as a selector.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the drop-down options & default value.
    table_name : 'str'
        Name of the table within `db_name` to store the drop-down options & default value.
    query_index : 'str'
        Name of the index within `db_name` & `table_name`. May only be one column.
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

        # Display the session-selector input object
        if not st.session_state[setup.NAME][db_name][table_name]['set-up']:
            if st.session_state[setup.NAME][db_name][table_name]['selector']['kwargs']:
                col1.selectbox(
                    key='Selector:%s' % generate_selector_key(
                        db_name=db_name,
                        table_name=table_name
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
                    },
                    label_visibility='collapsed',
                    **st.session_state[setup.NAME][db_name][table_name]['selector']['kwargs']
                )

            else:
                col1.selectbox(
                    key='Selector:%s' % generate_selector_key(
                        db_name=db_name,
                        table_name=table_name
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
                    },
                    label_visibility='collapsed'
                )
        else:
            col1.selectbox(
                key='Selector:%s' % generate_selector_key(
                    db_name=db_name,
                    table_name=table_name
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
                },
                disabled=True,
                label_visibility='collapsed'
            )

        # Display the 'Delete' button
        if (
            (options)
            and (not st.session_state[setup.NAME][db_name][table_name]['set-up'])
        ):
            col2.button(
                label='Delete',
                key='Button:%s-Delete' % generate_selector_key(
                    db_name=db_name,
                    table_name=table_name
                ),
                # on_click=delete,
                type='secondary',
                disabled=False,
                use_container_width=True
            )
        else:
            col2.button(
                label='Delete',
                key='Button:%s-Delete' % generate_selector_key(
                    db_name=db_name,
                    table_name=table_name
                ),
                # on_click=delete,
                type='secondary',
                disabled=True,
                use_container_width=True
            )

        # Display the 'New' or 'Reset' button
        if (
            (options)
            and (st.session_state[setup.NAME][db_name][table_name]['set-up'])
        ):
            col3.button(
                label='Edit',
                key='Button:%s-Edit' % generate_selector_key(
                    db_name=db_name,
                    table_name=table_name
                ),
                type='primary',
                disabled=False,
                on_click=display_session_setup_form,
                kwargs={
                    'db_name': db_name,
                    'table_name': table_name,
                    'value': False
                },
                use_container_width=True
            )
        else:
            col3.button(
                label='New',
                key='Button:%s-New' % generate_selector_key(
                    db_name=db_name,
                    table_name=table_name
                ),
                type='primary',
                disabled=False,
                on_click=display_session_setup_form,
                kwargs={
                    'db_name': db_name,
                    'table_name': table_name,
                    'value': True
                },
                use_container_width=True
            )


# Define function(s) for creating selectors
def generate_selector_key(
    db_name: str,
    table_name: str
):
    """ Generates a database table-specific key that contains the selector content.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the drop-down options & default value.
    table_name : 'str'
        Name of the table within `db_name` to store the drop-down options & default value.
    """

    return str('%s-%s-%s-%s').strip().lower() % (
        setup.NAME,
        str(db_name).strip().lower(),
        str(table_name).strip().lower(),
        str(st.session_state[setup.NAME][db_name][table_name]['selector']['parameter']).strip().lower()
    )


# Define function(s) for standard selector database queries
def select_selector_table_column_values(
    db_name: str,
    table_name: str,
    query_index: str
) -> list:
    """ Returns the drop-down options from the database table as a `list`.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the drop-down options & default value.
    table_name : 'str'
        Name of the table within `db_name` to store the drop-down options & default value.
    query_index : 'str'
        Name of the index within `db_name` & `table_name`. May only be one column.
    """

    # Initialize connection to the users-database
    Users = db.Handler(
        db_name=setup.USERS_DB_NAME
    )

    # Initialize the connection to the session-selector database
    Database = db.Handler(
        db_name=db_name
    )

    # Select session-selector drop-down options
    if Users.table_record_exists(
        table_name=table_name,
        filtr={
            'col': setup.USERS_DB_QUERY_INDEX,
            'val': st.session_state[setup.NAME][setup.USERS_DB_NAME][setup.USERS_DB_QUERY_INDEX]
        }
    ):
        options = Database.select_table_column_value(
            table_name=table_name,
            col=st.session_state[setup.NAME][db_name][table_name]['selector']['parameter'],
            filtr={
                'col': query_index,
                'val': Users.select_table_column_value(
                    table_name=table_name,
                    col=query_index,
                    filtr={
                        'col': setup.USERS_DB_QUERY_INDEX,
                        'val': st.session_state[setup.NAME][setup.USERS_DB_NAME][setup.USERS_DB_QUERY_INDEX]
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
    options: list
) -> int:
    """ Selects the default value and returns the index position of the value in `options` as an `int`.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the drop-down options & default value.
    table_name : 'str'
        Name of the table within `db_name` to store the drop-down options & default value.
    query_index : 'str'
        Name of the index within `db_name` & `table_name`. May only be one column.
    options: `list`
        The list containing the the drop-down options.
    """

    # Select the index of the default drop-down selection
    if options:
        try:
            index = options.index(st.session_state[setup.NAME][db_name]['name'])

            # Apply selector values to the session state
            # st.session_state[setup.NAME][self.db_name]['name'] = options[index]
            # st.session_state[setup.NAME][self.db_name][self.table_name]['selector']['value'] = options[index]

            # Set query index value
            st.session_state[setup.NAME][db_name]['name'] = options[index]
            st.session_state[setup.NAME][db_name][query_index] = select_query_index_value(
                db_name=db_name,
                table_name=table_name,
                query_index=query_index,
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
    query_index: str
):
    """ Sets the session state name and query index value to the selected value.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the drop-down options & default value.
    table_name : 'str'
        Name of the table within `db_name` to store the drop-down options & default value.
    query_index : 'str'
        Name of the index within `db_name` & `table_name`. May only be one column.
    """

    # Retrieve selected value
    selected_value = st.session_state[
        'Selector:%s' % generate_selector_key(
            db_name=db_name,
            table_name=table_name
        )
    ]

    # Update session state
    if st.session_state[setup.NAME][db_name]['name'] != selected_value:
        st.session_state[setup.NAME][db_name]['name'] = st.session_state[
            'Selector:%s' % generate_selector_key(
                db_name=db_name,
                table_name=table_name
            )
        ]

        st.session_state[setup.NAME][db_name][query_index] = select_query_index_value(
            db_name=db_name,
            table_name=table_name,
            query_index=query_index,
            filtr={
                'col': st.session_state[setup.NAME][db_name][table_name]['selector']['parameter'],
                'val': st.session_state[
                    'Selector:%s' % generate_selector_key(
                        db_name=db_name,
                        table_name=table_name
                    )
                ]
            }
        )


def select_query_index_value(
    db_name: str,
    table_name: str,
    query_index: str,
    filtr: dict
) -> str:
    """ Returns the query index value from a filtered database table.

    filtr : `dict`
        Dictionary object containing the column `col` and value
            `val` to filter `table_name`. If the filtered table
            returns more than one record, a `ValueError` is raised.

            e.g., {
                'col' : 'id',
                'val' : '1'
            }
    """

    # Initialize connection to the users-database
    Users = db.Handler(
        db_name=setup.USERS_DB_NAME
    )

    # Initialize connection to the session-selector database
    Database = db.Handler(
        db_name=db_name
    )

    values = Database.cursor.execute(
        """
        SELECT %s
            FROM %s
                WHERE %s IN (%s)
                    AND %s = '%s';
        """ % (
            query_index,
            table_name,
            query_index,
            ', '.join(
                ["'%s'" % (i) for i in Users.select_table_column_value(
                    table_name=table_name,
                    col=query_index,
                    filtr={
                        'col': setup.USERS_DB_QUERY_INDEX,
                        'val': st.session_state[setup.NAME][setup.USERS_DB_NAME][setup.USERS_DB_QUERY_INDEX]
                    },
                    return_dtype='str',
                    multi=True
                )]
            ),
            filtr['col'],
            filtr['val']
        )
    ).fetchall()

    return db.as_type(
        [i[0] for i in values][0],
        return_dtype='str'
    )


# Define function(s) for handling call-backs
def display_session_setup_form(
    db_name,
    table_name,
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
    response: dict
):
    """ Inserts a new session into the database table containing the settings parameters & values
    within the form `response`.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the drop-down options & default value.
    table_name : 'str'
        Name of the table within `db_name` to store the drop-down options & default value.
    query_index : 'str'
        Name of the index within `db_name` & `table_name`. May only be one column.
    response : `dict`
        Dictionary object containing the form responses.
    """

    # Initialize connection to the users-database
    Users = db.Handler(
        db_name=setup.USERS_DB_NAME
    )

    # Initialize connection to the session-selector database
    Database = db.Handler(
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
            [response[st.session_state[setup.NAME][db_name][table_name]['selector']['parameter']]]
            + [st.session_state[setup.NAME][setup.USERS_DB_NAME][setup.USERS_DB_QUERY_INDEX]]
        )

        # Generate id
        id = hashlib.md5(
            string_to_hash.lower().encode('utf-8')
        ).hexdigest()

        # Check if the id already exists
        try:
            ids = Users.select_table_column_value(
                table_name=table_name,
                col=query_index,
                filtr={
                    'col': setup.USERS_DB_QUERY_INDEX,
                    'val': st.session_state[setup.NAME][setup.USERS_DB_NAME][setup.USERS_DB_QUERY_INDEX]
                },
                multi=True
            )
        except db.NullReturnValue:
            ids = []

        if id not in ids:

            # Add to user database
            Users.insert(
                table_name=table_name,
                values={
                    setup.USERS_DB_QUERY_INDEX: (
                        st.session_state[setup.NAME][setup.USERS_DB_NAME][setup.USERS_DB_QUERY_INDEX]
                    ),
                    query_index: id
                }
            )

            # Create dictionary of columns and values to insert
            values = {query_index: id}
            values.update(response)

            # Add to studies database
            Database.insert(
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
            #   self.query_index_value is already set
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
    response: dict
):
    """ Updates an existing session within the database table with the settings parameters & values
    within the form `response`.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the drop-down options & default value.
    table_name : 'str'
        Name of the table within `db_name` to store the drop-down options & default value.
    query_index : 'str'
        Name of the index within `db_name` & `table_name`. May only be one column.
    response : `dict`
        Dictionary object containing the form responses.
    """

    # Initialize connection to the session-selector database
    Database = db.Handler(
        db_name=db_name
    )

    # Check for existing session-selector values
    if response[st.session_state[setup.NAME][db_name][table_name]['selector']['parameter']] not in (
        select_selector_table_column_values(
            db_name=db_name,
            table_name=table_name,
            query_index=query_index
        )
    ):

        # Check for empty form entries
        if '' not in [str(i).strip() for i in response.values()]:

            print(response.values())

            # Update session-selector parameters
            for parameter in list(response.keys()):

                if Database.table_record_exists(
                    table_name=table_name,
                    filtr={
                        'col': query_index,
                        'val': st.session_state[setup.NAME][db_name][query_index]
                    }
                ):

                    try:
                        Database.update(
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


def delete_session():

    # # Initialize connection to the users-database
    # Users = db.Handler(
    #     db_name=setup.USERS_DB_NAME
    # )

    # # Remove study id from users-database
    # Users.delete(
    #     table_name=self.table_name,
    #     filtr={
    #         'col': self.query_index,
    #         'val': self.query_index_value
    #     }
    # )

    # # Initialize connection to the session-selector database
    # Database = db.Handler(
    #     db_name=self.db_name
    # )

    # # Get all tables with study id
    # tables = Database.select_all_tables_with_column_name(
    #     col=self.query_index
    # )

    # # Delete all session-selector records in all tables
    # for table in tables:

    #     # Remove study id from session-selector database
    #     Database.delete(
    #         table_name=table,
    #         filtr={
    #             'col': self.query_index,
    #             'val': self.query_index_value
    #         }
    #     )

    # # Delete work directory for the selected study
    # if os.path.isdir(
    #     os.path.join(
    #         os.path.join(
    #             st.session_state[setup.NAME]['dir'],
    #             self.db_name,
    #             self.query_index_value
    #         )
    #     )
    # ):
    #     os.rmdir(
    #         os.path.join(
    #             st.session_state[setup.NAME]['dir'],
    #             self.db_name,
    #             self.query_index_value
    #         )
    #     )

    # # Log successes
    # st.session_state[setup.NAME][self.db_name]['successes'] = (
    #     st.session_state[setup.NAME][self.db_name]['successes'] + [
    #         'The entry {%s} was deleted successfully.' % (
    #             st.session_state[setup.NAME][self.db_name]['name']
    #         )
    #     ]
    # )

    # # Reset session state
    # del st.session_state[setup.NAME][self.db_name]['name']
    # del st.session_state[setup.NAME][self.db_name][self.query_index]
    # self.query_index_value = None

    # # Reset button
    # del st.session_state['delete_%s' % self.table_name]
    pass
