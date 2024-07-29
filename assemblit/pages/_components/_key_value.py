"""
Information
---------------------------------------------------------------------
Name        : _key_value.py
Location    : ~/pages/_components

Description
---------------------------------------------------------------------
Contains the generic methods for a key-value pair settings-page.
"""

import streamlit as st
from assemblit import setup
from assemblit.blocks.structures import Setting
from assemblit.database import _generic
from assemblit.database._structures import Filter, Validate, Value, Row
from pytensils import utils


# Define core-component key-value pair function(s)
def initialize_key_value_pair_table(
    db_name: str,
    table_name: str,
    query_index: str,
    settings: list[Setting]
):
    """ Initializes the key-value pair database table and parses the database
    table values into the session state when `table_name` is not `None`.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the setting(s) parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the setting(s) parameters & values.
    query_index : 'str'
        Name of the index within `db_name` & `table_name`. May only be one column.
    settings : `list[Setting]`
        List of `assemblit.app.structures.Setting` objects containing the setting(s) parameters & values.
    """

    # Initialize the key-value database
    Database = _generic.Connection(
        db_name=db_name,
        dir_name=setup.DB_DIR
    )

    # Construct key-value settings schema
    schema: _generic.Schema = _generic.Schema.from_settings(
        name=table_name,
        settings_object=settings,
        primary_key=query_index
    )

    # Create the key-value settings table
    Database.create_table(
        table_name=table_name,
        schema=schema
    )

    # Manage unset query parameters
    if st.session_state[setup.NAME][db_name][query_index]:

        # Assign the table information to the session state for the form content
        if Database.table_record_exists(
            table_name=table_name,
            filtr=Filter(
                col=query_index,
                val=st.session_state[setup.NAME][db_name][query_index]
            )
        ):

            # Retrieve the table information
            dictionary = (
                Database.select_multi_table_column_value(
                    table_name=table_name,
                    cols=get_key_value_pair_parameters(
                        db_name=db_name,
                        table_name=table_name
                    ),
                    filtr=Filter(
                        col=query_index,
                        val=st.session_state[setup.NAME][db_name][query_index]
                    )
                )
            )

            # Apply the table information to the session state
            for index, item in enumerate(
                st.session_state[setup.NAME][db_name][table_name]['settings']
            ):
                item: Setting

                # Parse settings
                st.session_state[setup.NAME][db_name][table_name]['settings'][index].value = utils.as_type(
                    value=dictionary[item.parameter],
                    return_dtype=st.session_state[setup.NAME][db_name][table_name]['settings'][index].dtype
                )

        else:

            # Insert the table information as defaults
            Database.insert(
                table_name=table_name,
                row=get_default_key_value_pair_settings(
                    db_name=db_name,
                    query_index=query_index,
                    settings=settings
                ),
                validate=Validate(
                    col=query_index,
                    val=st.session_state[setup.NAME][db_name][query_index]
                )
            )


def display_key_value_pair_settings_form(
    db_name: str,
    table_name: str,
    query_index: str,
    apply_db_values: bool,
    header: str = None,
    tagline: str = None,
    clear_on_submit: bool = True,
):
    """ Displays the database table setting(s) parameters & values as a key-value pair form.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the setting(s) parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the setting(s) parameters & values.
    query_index : 'str'
        Name of the index within `db_name` & `table_name`. May only be one column.
    apply_db_values: `bool`
        `True` or `False`, determines whether to apply the current database table
            value as the placeholder value in the form component.
    clear_on_submit : `bool`
        `True` or `False`, determines whether to clear the form-submission responses
            after submission
    """

    # Layout columns
    _, col2, col3 = st.columns(setup.CONTENT_COLUMNS)

    # Display the key-value pair configuration form
    with col2.form(
        key=generate_form_key(
            db_name=db_name,
            table_name=table_name
        ),
        clear_on_submit=clear_on_submit,
        border=True
    ):

        # Display the form header
        if header and tagline:
            st.write('### %s' % header)
            st.write('%s' % tagline)
            st.write('')
            st.write('')

        # Display table information as key-value pair configuration
        for setting in st.session_state[setup.NAME][db_name][table_name]['settings']:
            display_key_value_pair_setting(
                db_name=db_name,
                table_name=table_name,
                query_index=query_index,
                apply_db_values=apply_db_values,
                setting=setting
            )

        # Layout form columns
        _, col2, col3 = st.columns([.6, .2, .2])

        # Display the 'Clear' button
        col2.write('')
        col2.form_submit_button(
            label='Clear',
            type='secondary',
            on_click=clear,
            kwargs={
                'db_name': db_name,
                'table_name': table_name
            },
            use_container_width=True
        )

        # Display the 'Save' button
        col3.write('')
        col3.form_submit_button(
            label='Save',
            type='primary',
            on_click=save,
            kwargs={
                'db_name': db_name,
                'table_name': table_name
            },
            use_container_width=True
        )


def parse_form_response(
    db_name: str,
    table_name: str,
) -> dict:
    """ Parses the form responses and returns the values that changed as
    a dictionary to be handled outside the callback.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the setting(s) parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the setting(s) parameters & values.
    """

    # Initialize responses
    responses = {}

    if (
        (st.session_state[setup.NAME][db_name][table_name]['form-submission'])
        and ('FormSubmitter:%s-%s' % (
            generate_form_key(
                db_name=db_name,
                table_name=table_name
            ),
            'Save'
        ) in st.session_state)
    ):

        # Parse the form values into a dictionary
        for setting in st.session_state[setup.NAME][db_name][table_name]['settings']:
            setting: Setting

            if setting.parameter in st.session_state:
                if setting.value != st.session_state[setting.parameter]:
                    responses[setting.parameter] = st.session_state[setting.parameter]

                # Reset session state variables
                del st.session_state[setting.parameter]

        # Reset session state variables
        st.session_state[setup.NAME][db_name][table_name]['form-submission'] = False
        del st.session_state['FormSubmitter:%s-%s' % (
            generate_form_key(
                db_name=db_name,
                table_name=table_name
            ),
            'Save'
        )]

    else:

        # Pass to clear the form values
        pass

    return responses


# Define function(s) for managing key-value pair setting(s) parameters
def get_key_value_pair_parameters(
    db_name: str,
    table_name: str
) -> list:
    """ Parses the setting(s) parameters and returns a list

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the setting(s) parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the setting(s) parameters & values.
    """
    return [
        i.parameter for i in (
            st.session_state[setup.NAME][db_name][table_name]['settings']
        )
    ]


def get_default_key_value_pair_settings(
    db_name: str,
    query_index: str,
    settings: list[Setting],
) -> Row:
    """ Parses the default setting(s) parameters and values and
    returns a `Row` object.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the setting(s) parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the setting(s) parameters & values.
    query_index : 'str'
        Name of the index within `db_name` & `table_name`. May only be one column.
    settings : `list[Setting]`
        List of `assemblit.app.structures.Setting` objects containing the setting(s) parameters & values.
    """
    defaults = {
        query_index: st.session_state[setup.NAME][db_name][query_index]
    }

    for setting in settings:
        setting: Setting
        defaults[setting.parameter] = setting.value

    return Row(
        cols=list(defaults.keys()),
        vals=list(defaults.values())
    )


# Define function(s) for creating key-value pair forms
def generate_form_key(
    db_name: str,
    table_name: str
):
    """ Generates a database table-specific key that contains the form submission content.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the setting(s) parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the setting(s) parameters & values.
    """

    return str('%s-%s-%s').strip().lower() % (
        setup.NAME,
        str(db_name).strip().lower(),
        str(table_name).strip().lower()
    )


# Define function(s) for handling key-value pair form call-backs
def save(
    db_name: str,
    table_name: str
):
    """ Dummy function that triggers the form-submission.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the setting(s) parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the setting(s) parameters & values.
    """

    # Set the session state
    st.session_state[setup.NAME][db_name][table_name]['form-submission'] = True


def clear(
    db_name: str,
    table_name: str
):
    """ Dummy function that triggers the form-submission.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the setting(s) parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the setting(s) parameters & values.
    """

    # Set the session state
    st.session_state[setup.NAME][db_name][table_name]['form-submission'] = False


# Define function(s) for displaying key-value pair setting(s)
def display_key_value_pair_setting(
    db_name: str,
    table_name: str,
    query_index: str,
    apply_db_values: bool,
    setting: Setting
):
    """ Displays a `assemblit.app.structures.Setting` object as key-value pair configuration.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the setting(s) parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the setting(s) parameters & values.
    query_index : 'str'
        Name of the index within `db_name` & `table_name`. May only be one column.
    apply_db_values: `bool`
        `True` or `False`, determines whether to apply the current database table
            value as the placeholder value in the form component.
    setting : `Setting`
        `assemblit.app.structures.Setting` object.
    """

    # Layout columns
    col1, col2, col3 = st.columns([.25, .25, .5])

    # Display parameter name
    col1.markdown('_%s_' % (setting.name))

    # Update values based on query settings
    if (
        (apply_db_values)
        and (st.session_state[setup.NAME][db_name][query_index])
    ):
        try:
            setting.value = select_setting_table_column_value(
                db_name=db_name,
                query="""
                    SELECT %s FROM %s WHERE %s = '%s';
                """ % (
                    setting.parameter,
                    table_name,
                    query_index,
                    st.session_state[setup.NAME][db_name][query_index]
                ),
                return_dtype=setting.dtype
            )
        except _generic.NullReturnValue:
            setting.value = ''

    # Parse null value
    try:
        setting.value = utils.as_type(setting.value, return_dtype='bool')
    except TypeError:
        pass

    # Display parameter input-object
    if str(setting.type).strip().upper() == 'TEXT-INPUT':
        if setting.kwargs:
            col2.text_input(
                key=setting.parameter,
                label=setting.name,
                value=setting.value,
                label_visibility='collapsed',
                **setting.kwargs
            )
        else:
            col2.text_input(
                key=setting.parameter,
                label=setting.name,
                value=setting.value,
                label_visibility='collapsed'
            )
    elif str(setting.type).strip().upper() == 'TOGGLE':
        if setting.kwargs:
            col2.toggle(
                key=setting.parameter,
                label='Enable',
                value=setting.value,
                label_visibility='collapsed',
                **setting.kwargs
            )
        else:
            col2.toggle(
                key=setting.parameter,
                label='Enable',
                value=setting.value,
                label_visibility='collapsed',
            )
    elif str(setting.type).strip().upper() == 'SLIDER':
        if setting.kwargs:
            col2.slider(
                key=setting.parameter,
                label=setting.name,
                value=setting.value,
                label_visibility='collapsed',
                **setting.kwargs
            )
        else:
            raise KeyError(
                "st.slider() cannot be built without 'kwargs'."
            )
    elif str(setting.type).strip().upper() == 'MULTISELECT':
        if setting.kwargs:
            col2.multiselect(
                key=setting.parameter,
                label=setting.name,
                default=setting.value,
                label_visibility='collapsed',
                **setting.kwargs
            )
        else:
            raise KeyError(
                "st.multiselect() cannot be built without 'kwargs'."
            )
    else:
        raise NameError(
            "st.%s() is currently not supported." % (setting.type)
        )

    # Display parameter description
    if setting.description:
        col3.write(setting.description)


# Define function(s) for standard key-value pair database queries
def select_setting_table_column_value(
    db_name: str,
    query: str,
    return_dtype: str
) -> str | int | float | bool | list | dict:
    """ Submits {query} to {db_name} and returns the value in the
    {return_dtype}.

    Parameters
    ----------
    db_name : `str`
        Database name
    query : `str`
        SQL query as a string
    return_dtype : `str`
        Data-type of the returned value
    """

    # Initialize the connection to the Database
    Database = _generic.Connection(
        db_name=db_name,
        dir_name=setup.DB_DIR
    )

    # Return the table column value
    return (
        Database.select_generic_query(
            query=query,
            return_dtype=return_dtype
        )
    )


# Define function(s) for managing key-value pair database setting(s)
def update_settings(
    db_name: str,
    table_name: str,
    query_index: str,
    response: dict
):
    """ Updates the settings database table with the settings parameters & values within the form `response`.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the setting(s) parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the setting(s) parameters & values.
    query_index : 'str'
        Name of the index within `db_name` & `table_name`. May only be one column.
    response : `dict`
        Dictionary object containing the form responses.
    """

    # Apply form response to the database
    if response:

        # Initialize connection to the database
        Database = _generic.Connection(
            db_name=db_name,
            dir_name=setup.DB_DIR
        )

        # Update database settings
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
                            val=str(response[parameter]).strip()
                        ),
                        filtr=Filter(
                            col=query_index,
                            val=st.session_state[setup.NAME][db_name][query_index]
                        )
                    )

                    # Log success
                    st.session_state[setup.NAME][db_name]['successes'] = (
                        st.session_state[setup.NAME][db_name]['successes'] + [
                            """
                                {%s} successfully changed to %s.
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
