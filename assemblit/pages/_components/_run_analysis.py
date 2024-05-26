"""
Information
---------------------------------------------------------------------
Name        : _run_analysis.py
Location    : ~/components
Author      : Tom Eleff
Published   : 2024-03-28
Revised on  : .

Description
---------------------------------------------------------------------
Contains the generic methods for a run-analysis-page.
"""

import os
import hashlib
import datetime
import json
import pandas as pd
import streamlit as st
from assemblit import setup, db
from assemblit.server import layer
from assemblit.server import setup as server_setup
from assemblit.pages._components import _selector
from pytensils import utils


# Define core-component key-value pair function(s)
def initialize_key_value_pair_table(
    db_name: str,
    table_name: str,
    query_index: str,
    settings: list
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
    settings : `list`
        List of dictionary objects containing the setting(s) parameters & values.
    """

    # Initialize the key-value database
    Db = db.initialize_table(
        db_name=db_name,
        table_name=table_name,
        cols=(
            [query_index] + get_key_value_pair_parameters(
                db_name=db_name,
                table_name=table_name
            )
        )
    )

    # Manage unset query parameters
    if st.session_state[setup.NAME][db_name][query_index]:

        # Assign the table information to the session state for the form content
        if Db.table_record_exists(
            table_name=table_name,
            filtr={
                'col': query_index,
                'val': st.session_state[setup.NAME][db_name][query_index]
            }
        ):

            # Retrieve the table information
            dictionary = (
                Db.select_multi_table_column_value(
                    table_name=table_name,
                    cols=get_key_value_pair_parameters(
                        db_name=db_name,
                        table_name=table_name
                    ),
                    filtr={
                        'col': query_index,
                        'val': st.session_state[setup.NAME][db_name][query_index]
                    }
                )
            )

            # Apply the table information to the session state
            for index, item in enumerate(
                st.session_state[setup.NAME][db_name][table_name]['settings']
            ):
                st.session_state[setup.NAME][db_name][table_name]['settings'][index]['value'] = utils.as_type(
                    value=dictionary[item['parameter']],
                    return_dtype=st.session_state[setup.NAME][db_name][table_name]['settings'][index]['dtype']
                )

        else:

            # Insert the table information as defaults
            Db.insert(
                table_name=table_name,
                values=get_default_key_value_pair_settings(
                    db_name=db_name,
                    query_index=query_index,
                    settings=settings
                ),
                validate={
                    'col': query_index,
                    'val': st.session_state[setup.NAME][db_name][query_index]
                }
            )


# def display_run_analysis_context(
#     header: str = None,
#     tagline: str = None
# ):
#     """ Displays the context about the session.
#     """

#     # Layout columns
#     _, col2, _ = st.columns(setup.CONTENT_COLUMNS)

#     # # Display the context header
#     # with col2:
#     #     if header and tagline:
#     #         st.write('### %s' % header)
#     #         st.write('%s' % tagline)
#     #         # st.write('')
#     #         # st.write('')

#     # Display the run-analysis context container
#     with col2.container():

#         # Retain context
#         context = st.session_state[setup.NAME][setup.SESSIONS_DB_NAME][setup.SESSIONS_DB_NAME]['settings']
#         num_cols = 4

#         # Layout columns
#         cols = st.columns(num_cols)

#         # Set style
#         st.markdown(
#             """
#                 <style>
#                     .context {
#                         font-size:36px;
#                     }
#                 </style>
#             """,
#             unsafe_allow_html=True
#         )

#         # Display context parameters
#         for i in range(min(num_cols, len(context))):
#             with cols[i]:
#                 with st.container(border=True):
#                     st.write(context[i]['name'])
#                     st.markdown(
#                         """
#                         <p class="context">%s</p>
#                         """ % context[i]['value'],
#                         unsafe_allow_html=True
#                     )


def display_run_analysis_form(
    db_name: str,
    table_name: str,
    header: str = None,
    tagline: str = None
):
    """ Displays the database table setting(s) parameters & values as a key-value pair form.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the setting(s) parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the setting(s) parameters & values.
    """

    # Layout columns
    _, col2, col3 = st.columns(setup.CONTENT_COLUMNS)

    # Display the form header
    if header and tagline:
        col2.write('### %s' % header)
        col2.write('%s' % tagline)
        # st.write('')
        # st.write('')

    # Display the key-value pair configuration form
    with col2.form(
        key=generate_form_key(
            db_name=db_name,
            table_name=table_name
        ),
        border=True,
        clear_on_submit=True
    ):

        # Retreive run-analysis parameter options
        options = _selector.select_selector_dropdown_options(
            db_name=setup.DATA_DB_NAME,
            table_name='datasets',
            query_index=setup.DATA_DB_QUERY_INDEX,
            scope_db_name=setup.SESSIONS_DB_NAME,
            scope_query_index=setup.SESSIONS_DB_QUERY_INDEX
        )

        # Set run-analysis drop-down default query index
        index = _selector.select_selector_default_value(
            db_name=setup.DATA_DB_NAME,
            table_name='datasets',
            query_index=setup.DATA_DB_QUERY_INDEX,
            scope_db_name=setup.SESSIONS_DB_NAME,
            scope_query_index=setup.SESSIONS_DB_QUERY_INDEX,
            options=options
        )

        # Display the run-analysis drop-down
        st.selectbox(
            key='dataset',
            label='Dataset',
            options=options,
            index=index,
            placeholder='Select a dataset for the model analysis.',
            disabled=False,
            label_visibility='visible'
        )

        # Display run-information
        st.text_area(
            key='run_information',
            label='Run information',
            placeholder='Enter context about the model analysis run.',
            disabled=False,
            label_visibility='visible'
        )

        # Layout form columns
        col1, col2, col3 = st.columns([.6, .2, .2])

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
            label='Run',
            type='primary',
            on_click=run,
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
    """ Parses the form response and returns the values that changed as
    a dictionary to be handled outside the callback.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the setting(s) parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the setting(s) parameters & values.
    """

    # Initialize response
    response = {}

    if (
        (st.session_state[setup.NAME][db_name][table_name]['form-submission'])
        and ('FormSubmitter:%s-%s' % (
            generate_form_key(
                db_name=db_name,
                table_name=table_name
            ),
            'Run'
        ) in st.session_state)
    ):

        # Parse the form values into a dictionary
        for field in st.session_state[setup.NAME][db_name][table_name]['settings']:
            if field['parameter'] in st.session_state:

                # Preserve all response values
                response[field['parameter']] = st.session_state[field['parameter']]

                # Reset session state variables
                del st.session_state[field['parameter']]

        # Reset session state variables
        st.session_state[setup.NAME][db_name][table_name]['form-submission'] = False
        del st.session_state['FormSubmitter:%s-%s' % (
            generate_form_key(
                db_name=db_name,
                table_name=table_name
            ),
            'Run'
        )]

    else:

        # Pass to clear the form values
        pass

    return response


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
        i['parameter'] for i in (
            st.session_state[setup.NAME][db_name][table_name]['settings']
        )
    ]


def get_default_key_value_pair_settings(
    db_name: str,
    query_index: str,
    settings: list,
) -> dict:
    """ Parses the default setting(s) parameters and values and
    returns a dictionary.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the setting(s) parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the setting(s) parameters & values.
    query_index : 'str'
        Name of the index within `db_name` & `table_name`. May only be one column.
    settings : `list`
        List of dictionary objects containing the setting(s) parameters & values.
    """
    defaults = {
        query_index: st.session_state[setup.NAME][db_name][query_index]
    }

    for i in settings:
        defaults[i['parameter']] = i['value']

    return defaults


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
def run(
    db_name: str,
    table_name: str
):
    """ Dummy function that triggers the workflow-run.

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
    """ Dummy function that triggers the workflow-run.

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
# def display_key_value_pair_setting(
#     db_name: str,
#     table_name: str,
#     query_index: str,
#     apply_db_values: bool,
#     d: dict
# ):
#     """ Displays a dictionary object as key-value pair configuration.

#     Parameters
#     ----------
#     db_name : 'str'
#         Name of the database to store the setting(s) parameters & values
#     table_name : 'str'
#         Name of the table within `db_name` to store the setting(s) parameters & values.
#     query_index : 'str'
#         Name of the index within `db_name` & `table_name`. May only be one column.
#     apply_db_values: `bool`
#         `True` or `False`, determines whether to apply the current database table
#             value as the placeholder value in the form component.
#     d : `dict`
#         Dictionary object
#     """

#     # Layout columns
#     col1, col2, col3 = st.columns([.25, .25, .5])

#     # Display parameter name
#     col1.markdown('_%s_' % (d['name']))

#     # Update values based on query settings
#     if (
#         (apply_db_values)
#         and (st.session_state[setup.NAME][db_name][query_index])
#     ):
#         try:
#             d['value'] = select_setting_table_column_value(
#                 db_name=db_name,
#                 query="""
#                     SELECT %s FROM %s WHERE %s = '%s';
#                 """ % (
#                     d['parameter'],
#                     table_name,
#                     query_index,
#                     st.session_state[setup.NAME][db_name][query_index]
#                 ),
#                 return_dtype=d['dtype']
#             )
#         except db.NullReturnValue:
#             d['value'] = ''

#     # Display parameter input-object
#     if str(d['type']).strip().upper() == 'TEXT-INPUT':
#         if d['kwargs']:
#             col2.text_input(
#                 key=d['parameter'],
#                 label=d['name'],
#                 value=d['value'],
#                 label_visibility='collapsed',
#                 **d['kwargs']
#             )
#         else:
#             col2.text_input(
#                 key=d['parameter'],
#                 label=d['name'],
#                 value=d['value'],
#                 label_visibility='collapsed'
#             )
#     elif str(d['type']).strip().upper() == 'TOGGLE':
#         if d['kwargs']:
#             col2.toggle(
#                 key=d['parameter'],
#                 label='Enable',
#                 value=d['value'],
#                 label_visibility='collapsed',
#                 **d['kwargs']
#             )
#         else:
#             col2.toggle(
#                 key=d['parameter'],
#                 label='Enable',
#                 value=d['value'],
#                 label_visibility='collapsed',
#             )
#     elif str(d['type']).strip().upper() == 'SLIDER':
#         if d['kwargs']:
#             col2.slider(
#                 key=d['parameter'],
#                 label=d['name'],
#                 value=d['value'],
#                 label_visibility='collapsed',
#                 **d['kwargs']
#             )
#         else:
#             raise KeyError(
#                 "st.slider() cannot be built without 'kwargs'."
#             )
#     elif str(d['type']).strip().upper() == 'MULTISELECT':
#         if d['kwargs']:
#             col2.multiselect(
#                 key=d['parameter'],
#                 label=d['name'],
#                 default=d['value'],
#                 label_visibility='collapsed',
#                 **d['kwargs']
#             )
#         else:
#             raise KeyError(
#                 "st.multiselect() cannot be built without 'kwargs'."
#             )
#     else:
#         raise NameError(
#             "st.%s() is currently not supported." % (d['type'])
#         )

#     # Display parameter description
#     if d['description']:
#         col3.write(d['description'])


# Define function(s) for standard key-value pair database queries
# def select_setting_table_column_value(
#     db_name: str,
#     query: str,
#     return_dtype: str
# ) -> str | int | float | bool | list | dict:
#     """ Submits {query} to {db_name} and returns the value in the
#     {return_dtype}.

#     Parameters
#     ----------
#     db_name : `str`
#         Database name
#     query : `str`
#         SQL query as a string
#     return_dtype : `str`
#         Data-type of the returned value
#     """

#     # Initialize the connection to the Database
#     Db = db.Handler(
#         db_name=db_name
#     )

#     # Return the table column value
#     return (
#         Db.select_generic_query(
#             query=query,
#             return_dtype=return_dtype
#         )
#     )


# Define function(s) for managing key-value pair database setting(s)
def run_workflow(
    db_name: str,
    table_name: str,
    query_index: str,
    scope_db_name: str,
    scope_query_index: str,
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
    scope_db_name : `str`
        Name of the database that contains the associated scope for the workflow.
    scope_query_index : `str`
        Name of the index within `scope_db_name` & `table_name`. May only be one column.
    response : `dict`
        Dictionary object containing the form response.
    """

    # Apply form response to the database & run
    if response:

        # Initialize the connection to the scope database
        Session = db.Handler(
            db_name=setup.SESSIONS_DB_NAME
        )

        # Initialize connection to the data-ingestion database
        Data = db.Handler(
            db_name=setup.DATA_DB_NAME
        )

        # Initialize connection to the analysis database
        # Analysis = db.Handler(
        #     db_name=db_name
        # )

        # Generate a run-id
        run_id = hashlib.md5((str(datetime.datetime.now())).encode('utf-8')).hexdigest()

        # Make workflow-run directories
        if not os.path.isdir(os.path.join(setup.ROOT_DIR, db_name)):
            os.mkdir(os.path.join(setup.ROOT_DIR, db_name))

        if not os.path.isdir(os.path.join(setup.ROOT_DIR, db_name, run_id)):
            os.mkdir(os.path.join(setup.ROOT_DIR, db_name, run_id))

            if not os.path.isdir(os.path.join(setup.ROOT_DIR, db_name, run_id, 'inputs')):
                os.mkdir(os.path.join(setup.ROOT_DIR, db_name, run_id, 'inputs'))

                if not os.path.isdir(os.path.join(setup.ROOT_DIR, db_name, run_id, 'inputs', setup.DATA_DB_NAME)):
                    os.mkdir(os.path.join(setup.ROOT_DIR, db_name, run_id, 'inputs', setup.DATA_DB_NAME))

            if not os.path.isdir(os.path.join(setup.ROOT_DIR, db_name, run_id, 'outputs')):
                os.mkdir(os.path.join(setup.ROOT_DIR, db_name, run_id, 'outputs'))

        # Get dataset id
        dataset_id = Data.select_generic_query(
            query="""
                SELECT %s FROM (
                    SELECT file_name, %s, dbms
                        FROM %s
                            WHERE %s IN (%s)
                )
                    WHERE file_name = '%s';
            """ % (
                'dataset_id',
                'dataset_id',
                'datasets',
                'dataset_id',
                ', '.join(["'%s'" % (i) for i in Session.select_table_column_value(
                    table_name='datasets',
                    col='dataset_id',
                    filtr={
                        'col': scope_query_index,
                        'val': st.session_state[setup.NAME][scope_db_name][scope_query_index]
                    },
                    multi=True
                )]),
                response['dataset']
            ),
            return_dtype='str'
        )

        # Get dataset dbms
        dataset_dbms = Data.select_generic_query(
            query="""
                SELECT %s FROM (
                    SELECT file_name, %s, dbms
                        FROM %s
                            WHERE %s IN (%s)
                )
                    WHERE file_name = '%s';
            """ % (
                'dbms',
                'dataset_id',
                'datasets',
                'dataset_id',
                ', '.join(["'%s'" % (i) for i in Session.select_table_column_value(
                    table_name='datasets',
                    col='dataset_id',
                    filtr={
                        'col': scope_query_index,
                        'val': st.session_state[setup.NAME][scope_db_name][scope_query_index]
                    },
                    multi=True
                )]),
                response['dataset']
            ),
            return_dtype='str'
        )

        # Unload the data
        df = pd.read_sql(
            sql="SELECT * FROM '%s'" % (dataset_id),
            con=Data.connection
        )

        if dataset_dbms == '.CSV':
            df.to_csv(
                os.path.join(
                    setup.ROOT_DIR,
                    db_name,
                    run_id,
                    'inputs',
                    setup.DATA_DB_NAME,
                    response['dataset']
                ),
                sep=',',
                index=False
            )
        elif dataset_dbms == '.PARQUET':
            df.to_csv(
                os.path.join(
                    setup.ROOT_DIR,
                    db_name,
                    run_id,
                    'inputs',
                    setup.DATA_DB_NAME,
                    response['dataset']
                ),
                sep=',',
                index=False
            )

        # Build the run-request
        run_request = {
            'run-information': {
                'run-id': run_id,
                'start-date': str(datetime.datetime.now()),
                'version': server_setup.SERVER_DEPLOYMENT_VERSION,
                'session-name': st.session_state[setup.NAME][scope_db_name]['name'],
                'session-id': st.session_state[setup.NAME][scope_db_name][scope_query_index],
                'dataset-name': response['dataset'],
                'dataset-id': dataset_id,
                'inputs': os.path.join(setup.ROOT_DIR, db_name, run_id, 'inputs'),
                'outputs': os.path.join(setup.ROOT_DIR, db_name, run_id, 'outputs'),
            },
            'dir': {
                'inputs': os.path.join(setup.ROOT_DIR, db_name, run_id, 'inputs'),
                'outputs': os.path.join(setup.ROOT_DIR, db_name, run_id, 'outputs')
            },
            'workflow': Session.select_multi_table_column_value(
                table_name='workflow',
                cols=Session.select_table_column_names_as_list(table_name='workflow'),
                filtr={
                    'col': scope_query_index,
                    'val': st.session_state[setup.NAME][scope_db_name][scope_query_index]
                }
            )
        }

        # Unload the run-request parameters
        with open(
            os.path.join(
                setup.ROOT_DIR,
                db_name,
                run_id,
                'inputs',
                'run_request.json'
            ),
            mode='w+'
        ) as file:
            json.dump(
                run_request,
                file,
                indent=4
            )

        # Run workflow
        details = layer.run_workflow(
            server_name=server_setup.SERVER_NAME,
            server_type=server_setup.SERVER_TYPE,
            server_port=server_setup.SERVER_PORT,
            root_dir=setup.DB_DIR,
            workflow_id=run_id,
            deployment_id=server_setup.SERVER_DEPLOYMENT_ID,
            deployment_version=server_setup.SERVER_DEPLOYMENT_VERSION,
            run_request=run_request
        )

        print(response)
        # # Initialize connection to the database
        # Db = db.Handler(
        #     db_name=db_name
        # )

        # # Update database settings
        # for parameter in list(response.keys()):

        #     if Db.table_record_exists(
        #         table_name=table_name,
        #         filtr={
        #             'col': query_index,
        #             'val': st.session_state[setup.NAME][db_name][query_index]
        #         }
        #     ):
        #         try:
        #             Db.update(
        #                 table_name=table_name,
        #                 values={
        #                     'col': parameter,
        #                     'val': str(response[parameter]).strip()
        #                 },
        #                 filtr={
        #                     'col': query_index,
        #                     'val': st.session_state[setup.NAME][db_name][query_index]
        #                 }
        #             )

        #             # Log success
        #             st.session_state[setup.NAME][db_name]['successes'] = (
        #                 st.session_state[setup.NAME][db_name]['successes'] + [
        #                     """
        #                         {%s} successfully changed to %s.
        #                     """ % (
        #                         parameter,
        #                         response[parameter]
        #                     )
        #                 ]
        #             )

        #         except ValueError as e:

        #             # Log error
        #             st.session_state[setup.NAME][db_name]['errors'] = (
        #                 st.session_state[setup.NAME][db_name]['errors'] + [str(e)]
        #             )

        #     else:

        #         # Log error
        #         st.session_state[setup.NAME][db_name]['errors'] = (
        #             st.session_state[setup.NAME][db_name]['errors'] + [
        #                 'No table record found.'
        #             ]
        #         )

        # Log success
        st.session_state[setup.NAME][db_name]['successes'] = (
            st.session_state[setup.NAME][db_name]['successes'] + [
                """
                    Analysis-run {%s} successfully created.
                """ % (
                    details['id']
                )
            ]
        )
