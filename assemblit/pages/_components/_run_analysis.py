"""
Information
---------------------------------------------------------------------
Name        : _run_analysis.py
Location    : ~/_components
Author      : Tom Eleff
Published   : 2024-06-02
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


# Define core-component key-value pair function(s)
def display_run_analysis_form(
    db_name: str,
    table_name: str,
    header: str = None,
    tagline: str = None
):
    """ Displays the run-analysis setting(s) parameters & values as a key-value pair form.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the setting(s) parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the setting(s) parameters & values.
    header : `str`
        String to display as the form header.
    tagline : `str`
        String to display as the form tagline.
    """

    # Layout columns
    _, col2, col3 = st.columns(setup.CONTENT_COLUMNS)

    # Display the form header
    if header and tagline:
        col2.write('### %s' % header)
        col2.write('%s' % tagline)

    # Check server-health
    server_health = layer.health_check(
        server_name=server_setup.SERVER_NAME,
        server_type=server_setup.SERVER_TYPE,
        server_port=server_setup.SERVER_PORT,
        root_dir=setup.DB_DIR
    )

    # Display the run-analysis form
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
            disabled=not server_health,
            label_visibility='visible'
        )

        # Display run-information
        st.text_area(
            key='run_information',
            label='Run information',
            placeholder='Enter context about the model analysis run.',
            disabled=not server_health,
            label_visibility='visible'
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
            use_container_width=True,
            disabled=not server_health
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
            use_container_width=True,
            disabled=not server_health
        )

    # Log errors
    if not server_health:
        st.session_state[setup.NAME][db_name]['errors'] = (
            st.session_state[setup.NAME][db_name]['errors'] + [
                """
                    The {%s} orchestration server is currently unavailable.
                """ % (
                    ''.join([
                        server_setup.SERVER_TYPE[0].upper(),
                        server_setup.SERVER_TYPE[1:].lower()
                    ])
                )
            ]
        )


def parse_form_response(
    db_name: str,
    table_name: str,
) -> dict:
    """ Parses the form response and returns all values as
    a dictionary to be handled outside the callback.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the run-analysis parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the run-analysis parameters & values.
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


# Define function(s) for creating key-value pair forms
def generate_form_key(
    db_name: str,
    table_name: str
):
    """ Generates a database table-specific key that contains the form submission content.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the run-analysis parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the run-analysis parameters & values.
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
    """ Dummy function that submits the job-run.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the run-analysis parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the run-analysis parameters & values.
    """

    # Set the session state
    st.session_state[setup.NAME][db_name][table_name]['form-submission'] = True


def clear(
    db_name: str,
    table_name: str
):
    """ Dummy function that clears the job-run.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the run-analysis parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the run-analysis parameters & values.
    """

    # Set the session state
    st.session_state[setup.NAME][db_name][table_name]['form-submission'] = False


# Define function(s) for submitting analysis job-runs
def run_job(
    db_name: str,
    table_name: str,
    query_index: str,
    scope_db_name: str,
    scope_query_index: str,
    response: dict
):
    """ Submits an analysis job-run to the orchestration server.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the setting(s) parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the setting(s) parameters & values.
    query_index : 'str'
        Name of the index within `db_name` & `table_name`. May only be one column.
    scope_db_name : `str`
        Name of the database that contains the associated scope for the job.
    scope_query_index : `str`
        Name of the index within `scope_db_name` & `table_name`. May only be one column.
    response : `dict`
        Dictionary object containing the form response.
    """

    # Apply form response to the database & run
    if response and layer.health_check(
        server_name=server_setup.SERVER_NAME,
        server_type=server_setup.SERVER_TYPE,
        server_port=server_setup.SERVER_PORT,
        root_dir=setup.DB_DIR
    ):

        # Initialize the connection to the scope database
        Session = db.Handler(
            db_name=scope_db_name
        )

        # Initialize connection to the data-ingestion database
        Data = db.Handler(
            db_name=setup.DATA_DB_NAME
        )

        # Initialize connection to the analysis database
        Analysis = db.Handler(
            db_name=db_name
        )

        # Generate a job-run name
        name = hashlib.md5((str(datetime.datetime.now())).encode('utf-8')).hexdigest()

        # Make job-run directories
        if not os.path.isdir(os.path.join(setup.ROOT_DIR, db_name)):
            os.mkdir(os.path.join(setup.ROOT_DIR, db_name))

        if not os.path.isdir(os.path.join(setup.ROOT_DIR, db_name, name)):
            os.mkdir(os.path.join(setup.ROOT_DIR, db_name, name))

            if not os.path.isdir(os.path.join(setup.ROOT_DIR, db_name, name, 'inputs')):
                os.mkdir(os.path.join(setup.ROOT_DIR, db_name, name, 'inputs'))

                if not os.path.isdir(os.path.join(setup.ROOT_DIR, db_name, name, 'inputs', setup.DATA_DB_NAME)):
                    os.mkdir(os.path.join(setup.ROOT_DIR, db_name, name, 'inputs', setup.DATA_DB_NAME))

            if not os.path.isdir(os.path.join(setup.ROOT_DIR, db_name, name, 'outputs')):
                os.mkdir(os.path.join(setup.ROOT_DIR, db_name, name, 'outputs'))

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
                setup.DATA_DB_QUERY_INDEX,
                setup.DATA_DB_QUERY_INDEX,
                'datasets',
                setup.DATA_DB_QUERY_INDEX,
                ', '.join(["'%s'" % (i) for i in Session.select_table_column_value(
                    table_name='datasets',
                    col=setup.DATA_DB_QUERY_INDEX,
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
                setup.DATA_DB_QUERY_INDEX,
                'datasets',
                setup.DATA_DB_QUERY_INDEX,
                ', '.join(["'%s'" % (i) for i in Session.select_table_column_value(
                    table_name='datasets',
                    col=setup.DATA_DB_QUERY_INDEX,
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
                    name,
                    'inputs',
                    setup.DATA_DB_NAME,
                    response['dataset']
                ),
                sep=',',
                index=False
            )
        elif dataset_dbms == '.PARQUET':
            df.to_parquet(
                os.path.join(
                    setup.ROOT_DIR,
                    db_name,
                    name,
                    'inputs',
                    setup.DATA_DB_NAME,
                    response['dataset']
                ),
                index=False
            )

        # Build the run-request
        run_request = {
            'run-information': {
                'run-name': name,
                'start-date': str(datetime.datetime.now()),
                'version': server_setup.SERVER_DEPLOYMENT_VERSION,
                'session-name': st.session_state[setup.NAME][scope_db_name]['name'],
                'session-id': st.session_state[setup.NAME][scope_db_name][scope_query_index],
                'dataset-name': response['dataset'],
                'dataset-id': dataset_id,
                'inputs': os.path.join(setup.ROOT_DIR, db_name, name, 'inputs'),
                'outputs': os.path.join(setup.ROOT_DIR, db_name, name, 'outputs'),
            },
            'dir': {
                'inputs': os.path.join(setup.ROOT_DIR, db_name, name, 'inputs'),
                'outputs': os.path.join(setup.ROOT_DIR, db_name, name, 'outputs')
            },
            'workflow': Session.select_multi_table_column_value(
                table_name='workflow',
                cols=[col for col in Session.select_table_column_names_as_list(
                    table_name='workflow'
                ) if col != scope_query_index],
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
                name,
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

        # Run job
        job_run = layer.run_job(
            server_name=server_setup.SERVER_NAME,
            server_type=server_setup.SERVER_TYPE,
            server_port=server_setup.SERVER_PORT,
            root_dir=setup.DB_DIR,
            name=name,
            job_name=server_setup.SERVER_JOB_NAME,
            deployment_name=server_setup.SERVER_DEPLOYMENT_NAME,
            deployment_version=server_setup.SERVER_DEPLOYMENT_VERSION,
            run_request=run_request
        )

        # Update the scope database
        Session.insert(
            table_name=table_name,
            values={
                scope_query_index: (
                    st.session_state[setup.NAME][scope_db_name][scope_query_index]
                ),
                query_index: job_run['id']
            }
        )

        # Update the run-analysis database
        Analysis.insert(
            table_name=table_name,
            values={
                query_index: job_run['id'],
                'name': name,
                'server_type': server_setup.SERVER_TYPE,
                'submitted_by': st.session_state[setup.NAME][setup.USERS_DB_NAME]['name'],
                'created_on': run_request['run-information']['start-date'],
                'state': job_run['state'],
                'start_time': job_run['start_time'],
                'end_time': job_run['end_time'],
                'run_time': job_run['run_time'],
                'file_name': response['dataset'],
                'inputs': run_request['dir']['inputs'],
                'outputs': run_request['dir']['outputs'],
                'run_information': response['run_information'],
                'parameters': job_run['parameters'],
                'tags': job_run['tags'],
                'url': job_run['url']
            },
            validate={
                'col': query_index,
                'val': job_run['id']
            }
        )

        # Log success
        st.session_state[setup.NAME][db_name]['successes'] = (
            st.session_state[setup.NAME][db_name]['successes'] + [
                """
                    Analysis-run {%s} successfully created.
                """ % (
                    name
                )
            ]
        )
