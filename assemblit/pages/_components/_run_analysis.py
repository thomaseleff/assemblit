""" Contains the generic methods for a run-analysis-page """

import os
import hashlib
import datetime
import json
import pandas as pd
import streamlit as st
from assemblit import setup
from assemblit.blocks.structures import Setting
from assemblit.pages._components import _core, _selector
from assemblit._database import _generic, sessions, data, analysis
from assemblit._database._structures import Filter, Validate, Row
from assemblit._orchestrator import layer
from assemblit._orchestrator import setup as server_setup

# --TODO Remove scope_db_name and scope_query_index from all function(s).
#       Scope for analysis is not dynamic, it can only be the sessions-db.


# Define core-component key-value pair function(s)
def display_run_analysis_form(
    db_name: str,
    table_name: str,
    scope_db_name: str,
    scope_query_index: str,
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
    scope_db_name : `str`
        Name of the database that contains the associated scope for the job.
    scope_query_index : `str`
        Name of the index within `scope_db_name` & `table_name`. May only be one column.
    header : `str`
        String to display as the form header.
    tagline : `str`
        String to display as the form tagline.
    """

    # Layout columns
    _, col2 = st.columns(setup.CONTENT_COLUMNS)

    # Display the form header
    if header and tagline:
        col2.write('### %s' % header)
        col2.write('%s' % tagline)

    # Check server-health
    server_health = layer.health_check(
        server_type=server_setup.SERVER_TYPE,
        server_port=server_setup.SERVER_PORT,
        job_name=server_setup.SERVER_JOB_NAME,
        job_entrypoint=server_setup.SERVER_JOB_ENTRYPOINT,
        deployment_name=server_setup.SERVER_DEPLOYMENT_NAME,
        root_dir=server_setup.SERVER_DIR
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
        try:
            options = _selector.select_selector_dropdown_options(
                db_name=setup.DATA_DB_NAME,
                table_name=setup.DATA_DB_NAME,
                query_index=setup.DATA_DB_QUERY_INDEX,
                scope_db_name=scope_db_name,
                scope_query_index=scope_query_index
            )
        except _generic.NullReturnValue:
            options = []

        # Set run-analysis drop-down default query index
        try:
            index = _selector.select_selector_default_value(
                db_name=setup.DATA_DB_NAME,
                table_name=setup.DATA_DB_NAME,
                query_index=setup.DATA_DB_QUERY_INDEX,
                scope_db_name=scope_db_name,
                scope_query_index=scope_query_index,
                options=options
            )
        except _generic.NullReturnValue:
            index = None

        # Display the run-analysis drop-down
        st.selectbox(
            key='dataset',
            label='Dataset',
            options=options,
            index=index,
            placeholder='Select a dataset for the model analysis.',
            disabled=(not server_health or not options),
            label_visibility='visible'
        )

        # Display run-information
        st.text_area(
            key='run_information',
            label='Run information',
            placeholder='Enter context about the model analysis run.',
            disabled=(not server_health or not options),
            label_visibility='visible'
        )

        # Layout form columns
        _, col2, col3 = st.columns([.6, .2, .2])

        # Display the 'Clear' button
        col2.form_submit_button(
            label='Clear',
            type='secondary',
            on_click=clear,
            kwargs={
                'db_name': db_name,
                'table_name': table_name
            },
            use_container_width=True,
            disabled=(not server_health or not options)
        )

        # Display the 'Save' button
        col3.form_submit_button(
            label='Run',
            type='primary',
            on_click=run,
            kwargs={
                'db_name': db_name,
                'table_name': table_name
            },
            use_container_width=True,
            disabled=(not server_health or not options)
        )

    # Display content information
    if not options:
        _core.display_page_content_info(
            content_info="Upload a datafile to run an analysis."
        )

    # Log errors
    elif not server_health:
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
        for setting in st.session_state[setup.NAME][db_name][table_name]['settings']:
            setting: Setting

            if setting.parameter in st.session_state:

                # Preserve all response values
                response[setting.parameter] = st.session_state[setting.parameter]

                # Reset session state variables
                del st.session_state[setting.parameter]

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
        server_type=server_setup.SERVER_TYPE,
        server_port=server_setup.SERVER_PORT,
        job_name=server_setup.SERVER_JOB_NAME,
        job_entrypoint=server_setup.SERVER_JOB_ENTRYPOINT,
        deployment_name=server_setup.SERVER_DEPLOYMENT_NAME,
        root_dir=server_setup.SERVER_DIR
    ):

        # Initialize the connection to the sessions database
        Sessions = sessions.Connection()

        # Initialize connection to the data-ingestion database
        Data = data.Connection()

        # Initialize connection to the analysis database
        Analysis = analysis.Connection()

        # Generate a job-run name
        name = hashlib.md5((str(datetime.datetime.now())).encode('utf-8')).hexdigest()

        # Make job-run directories
        if not os.path.isdir(os.path.join(setup.ROOT_DIR, 'workspace')):
            os.mkdir(os.path.join(setup.ROOT_DIR, 'workspace'))

        if not os.path.isdir(os.path.join(setup.ROOT_DIR, 'workspace', db_name)):
            os.mkdir(os.path.join(setup.ROOT_DIR, 'workspace', db_name))

        if not os.path.isdir(os.path.join(setup.ROOT_DIR, 'workspace', db_name, name)):
            os.mkdir(os.path.join(setup.ROOT_DIR, 'workspace', db_name, name))

            if not os.path.isdir(os.path.join(setup.ROOT_DIR, 'workspace', db_name, name, 'inputs')):
                os.mkdir(os.path.join(setup.ROOT_DIR, 'workspace', db_name, name, 'inputs'))

                if not os.path.isdir(os.path.join(setup.ROOT_DIR, 'workspace', db_name, name, 'inputs', setup.DATA_DB_NAME)):
                    os.mkdir(os.path.join(setup.ROOT_DIR, 'workspace', db_name, name, 'inputs', setup.DATA_DB_NAME))

            if not os.path.isdir(os.path.join(setup.ROOT_DIR, 'workspace', db_name, name, 'outputs')):
                os.mkdir(os.path.join(setup.ROOT_DIR, 'workspace', db_name, name, 'outputs'))

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
                setup.DATA_DB_NAME,
                setup.DATA_DB_QUERY_INDEX,
                ', '.join(["'%s'" % (i) for i in Sessions.select_table_column_value(
                    table_name=setup.DATA_DB_NAME,
                    col=setup.DATA_DB_QUERY_INDEX,
                    filtr=Filter(
                        col=scope_query_index,
                        val=st.session_state[setup.NAME][scope_db_name][scope_query_index]
                    ),
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
                setup.DATA_DB_NAME,
                setup.DATA_DB_QUERY_INDEX,
                ', '.join(["'%s'" % (i) for i in Sessions.select_table_column_value(
                    table_name=setup.DATA_DB_NAME,
                    col=setup.DATA_DB_QUERY_INDEX,
                    filtr=Filter(
                        col=scope_query_index,
                        val=st.session_state[setup.NAME][scope_db_name][scope_query_index]
                    ),
                    multi=True
                )]),
                response['dataset']
            ),
            return_dtype='str'
        )

        # Unload the data
        df = pd.read_sql(
            sql="SELECT * FROM '%s'" % (dataset_id),
            con=Data.connection()
        )

        if dataset_dbms == '.CSV':
            df.to_csv(
                os.path.join(
                    setup.ROOT_DIR,
                    'workspace',
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
                    'workspace',
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
                'deployment': server_setup.SERVER_DEPLOYMENT_NAME,
                'session-name': st.session_state[setup.NAME][scope_db_name]['name'],
                'session-id': st.session_state[setup.NAME][scope_db_name][scope_query_index],
                'dataset-name': response['dataset'],
                'dataset-id': dataset_id,
                'inputs': os.path.join(setup.ROOT_DIR, 'workspace', db_name, name, 'inputs'),
                'outputs': os.path.join(setup.ROOT_DIR, 'workspace', db_name, name, 'outputs'),
            },
            'dir': {
                'inputs': os.path.join(setup.ROOT_DIR, 'workspace', db_name, name, 'inputs'),
                'outputs': os.path.join(setup.ROOT_DIR, 'workspace', db_name, name, 'outputs')
            },
            'workflow': Sessions.select_multi_table_column_value(
                table_name='workflow',
                cols=[col for col in Sessions.select_table_column_names_as_list(
                    table_name='workflow'
                ) if col != scope_query_index],
                filtr=Filter(
                    col=scope_query_index,
                    val=st.session_state[setup.NAME][scope_db_name][scope_query_index]
                )
            )
        }

        # Unload the run-request parameters
        with open(
            os.path.join(
                setup.ROOT_DIR,
                'workspace',
                db_name,
                name,
                'inputs',
                'run_request.json'
            ),
            mode='w'
        ) as file:
            json.dump(
                run_request,
                file,
                indent=4
            )

        # Run job
        job_run = layer.run_job(
            server_type=server_setup.SERVER_TYPE,
            server_port=server_setup.SERVER_PORT,
            root_dir=setup.DB_DIR,
            name=name,
            job_name=server_setup.SERVER_JOB_NAME,
            job_entrypoint=server_setup.SERVER_JOB_ENTRYPOINT,
            deployment_name=server_setup.SERVER_DEPLOYMENT_NAME,
            run_request=run_request
        )

        # Update the scope database
        Sessions.insert(
            table_name=table_name,
            row=Row(
                cols=sessions.Schemas.analysis.cols(),
                vals=[
                    st.session_state[setup.NAME][scope_db_name][scope_query_index],
                    job_run['id']
                ]
            )
        )

        # Update the run-analysis database
        Analysis.insert(
            table_name=table_name,
            row=Row(
                cols=analysis.Schemas.analysis.cols(),
                vals=[
                    job_run['id'],
                    name,
                    server_setup.SERVER_TYPE,
                    st.session_state[setup.NAME][setup.USERS_DB_NAME]['name'],
                    run_request['run-information']['start-date'],
                    job_run['state'],
                    job_run['start_time'],
                    job_run['end_time'],
                    job_run['run_time'],
                    response['dataset'],
                    run_request['dir']['inputs'],
                    run_request['dir']['outputs'],
                    response['run_information'],
                    job_run['parameters'],
                    job_run['tags'],
                    job_run['url']
                ]
            ),
            validate=Validate(
                col=query_index,
                val=job_run['id']
            )
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
