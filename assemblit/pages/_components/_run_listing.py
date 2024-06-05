'''
Information
---------------------------------------------------------------------
Name        : _run_listing.py
Location    : ~/_components
Author      : Tom Eleff
Published   : 2024-06-02
Revised on  : .

Description
---------------------------------------------------------------------
Contains the generic methods for a run-listing-page.
'''

# import os
# import hashlib
# import datetime
# import json
import pandas as pd
import streamlit as st
from assemblit import setup, db
from assemblit.server import layer
from assemblit.server import setup as server_setup
from assemblit.pages._components import _selector


# Define core-component run-listing function(s)
def display_run_listing_table(
    db_name: str,
    table_name: str,
    query_index: str,
    scope_db_name: str,
    scope_query_index: str
):
    ''' Displays the run-listing table.

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
    '''

    # Initialize connection to the analysis database
    Analysis = db.Handler(
        db_name=db_name
    )

    # Check server-health
    server_health = layer.health_check(
        server_name=server_setup.SERVER_NAME,
        server_type=server_setup.SERVER_TYPE,
        server_port=server_setup.SERVER_PORT,
        root_dir=setup.DB_DIR
    )

    # Get analysis-runs
    df = pd.read_sql(
        sql="SELECT * FROM '%s'" % (table_name),
        con=Analysis.connection
    )
    df = df[[
        'created_on',
        'name',
        'submitted_by',
        'state',
        'start_time',
        'end_time',
        'run_time',
        'outputs',
        'url'
    ]].merge(
        right=pd.DataFrame(
            {
                'state': [
                    'SCHEDULED',
                    'LATE',
                    'AWAITINGRETRY',
                    'PENDING',
                    'RUNNING',
                    'RETRYING',
                    'PAUSED',
                    'CANCELLING',
                    'CANCELLED',
                    'COMPLETED',
                    'FAILED',
                    'CRASHED'
                ],
                'status': [
                    '🆕 Scheduled',
                    '⚠️ Late',
                    '⚠️ Awaiting retry',
                    '🔜 Pending',
                    '⏳ Running',
                    '⚠️ Retrying',
                    '⏸️ Paused',
                    '⚪ Cancelling',
                    '⚪ Cancelled',
                    '✅ Succeeded',
                    '⛔ Failed',
                    '⚠️ Crashed'
                ]
            }
        ),
        how='left',
        left_on=['state'],
        right_on=['state'],
        validate='m:1'
    )
    # --TODO Add session-scope details
    # --TODO Get status from orchestrator library

    # Layout form columns
    _, col2, col3, col4, _, col6, _ = st.columns([.075, .175, .175, .175, .175, .175, .05])

    created_on_filter = col2.multiselect(
        key='MultiSelect:%s' % _selector.generate_selector_key(
            db_name=db_name,
            table_name=table_name,
            parameter='Created on'
        ),
        label='Created on',
        options=sorted(list(df['created_on'].unique()), reverse=True),
        max_selections=1,
        placeholder="""
            Select a date
        """
    )
    name_filter = col3.multiselect(
        key='MultiSelect:%s' % _selector.generate_selector_key(
            db_name=db_name,
            table_name=table_name,
            parameter='Analysis'
        ),
        label='Analysis',
        options=sorted(list(df['name'].unique())),
        max_selections=1,
        placeholder="""
            Select an analysis
        """
    )
    submitted_by_filter = col4.multiselect(
        key='MultiSelect:%s' % _selector.generate_selector_key(
            db_name=db_name,
            table_name=table_name,
            parameter='Submitted by'
        ),
        label='Submitted by',
        options=sorted(list(df['submitted_by'].unique())),
        default=st.session_state[setup.NAME][setup.USERS_DB_NAME]['name'],
        placeholder="""
            Select a submitter
        """
    )

    # Display the 'Refresh' button
    col6.button(
        label='Refresh',
        type='primary',
        on_click=refresh,
        use_container_width=True,
        disabled=not server_health
    )

    # Layout columns
    _, col2, _ = st.columns(setup.CONTENT_COLUMNS)

    # Filter
    if created_on_filter:
        df = df[df['created_on'].isin(created_on_filter)]
    if name_filter:
        df = df[df['name'].isin(name_filter)]
    if submitted_by_filter:
        df = df[df['submitted_by'].isin(submitted_by_filter)]

    # Sort
    df = df.sort_values(by='created_on', ascending=False)

    # Display the run-listing table
    with col2:
        st.dataframe(
            data=df[[
                'created_on',
                'name',
                'submitted_by',
                'status',
                'start_time',
                'end_time',
                'run_time',
                'url'
            ]],
            height=475,
            use_container_width=True,
            hide_index=True,
            column_config={
                'created_on': st.column_config.DateColumn(
                    label='Created on',
                    format='MMM D, YYYY, h:mm:ss a'
                ),
                'name': st.column_config.TextColumn(
                    label='Analysis'
                ),
                'submitted_by': st.column_config.TextColumn(
                    label='Submitted by'
                ),
                'status': st.column_config.TextColumn(
                    label='Status'
                ),
                'start_time': st.column_config.TimeColumn(
                    label='Run start',
                    format='h:mm:ss a'
                ),
                'end_time': st.column_config.TimeColumn(
                    label='Run end',
                    format='h:mm:ss a'
                ),
                'run_time': st.column_config.TimeColumn(
                    label='Run time',
                    format='H [hr.] m [min.] s [sec.]'
                ),
                'url': st.column_config.LinkColumn(
                    label='Direct link',
                    display_text='Link'
                )
            }
        )

    # Log errors
    if not server_health:
        st.session_state[setup.NAME][db_name]['errors'] = (
            st.session_state[setup.NAME][db_name]['errors'] + [
                '''
                    The {%s} orchestration server is currently unavailable.
                ''' % (
                    ''.join([
                        server_setup.SERVER_TYPE[0].upper(),
                        server_setup.SERVER_TYPE[1:].lower()
                    ])
                )
            ]
        )


# Define function(s) for creating run-listing tables
def generate_table_key(
    db_name: str,
    table_name: str
):
    ''' Generates a database table-specific key that contains the dataframe table status.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the run-analysis parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the run-analysis parameters & values.
    '''

    return str('%s-%s-%s').strip().lower() % (
        setup.NAME,
        str(db_name).strip().lower(),
        str(table_name).strip().lower()
    )


# Define function(s) for handling call-backs
def refresh():
    ''' Dummy function that refreshes the run-listing-page.
    '''
    pass


# Define function(s) for refreshing the run-listing table
def refresh_run_listing_table(
    db_name: str,
    table_name: str,
    query_index: str
):
    ''' Submits an analysis job-run to the orchestration server.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the setting(s) parameters & values
    table_name : 'str'
        Name of the table within `db_name` to store the setting(s) parameters & values.
    query_index : 'str'
        Name of the index within `db_name` & `table_name`. May only be one column.
    '''

    # Apply form response to the database & run
    if layer.health_check(
        server_name=server_setup.SERVER_NAME,
        server_type=server_setup.SERVER_TYPE,
        server_port=server_setup.SERVER_PORT,
        root_dir=setup.DB_DIR
    ):

        # Initialize connection to the analysis database
        Analysis = db.Handler(
            db_name=db_name
        )

        # Get all run-ids with non-terminal states
        run_ids = Analysis.select_table_column_value(
            table_name=table_name,
            col=query_index,
            filtr={
                'col': 'state',
                'val': ['CANCELLED', 'COMPLETED', 'FAILED', 'CRASHED']
            },
            return_dtype='str',
            multi=True,
            order='DESC',
            contains=False
        )

        # Poll the status of each run-id
        for run_id in run_ids:
            status = layer.poll_job_run(
                server_name=server_setup.SERVER_NAME,
                server_type=server_setup.SERVER_TYPE,
                server_port=server_setup.SERVER_PORT,
                root_dir=setup.DB_DIR,
                run_id=run_id
            )

            # Update
            if status:
                for key, value in status.items():

                    Analysis.update(
                        table_name=table_name,
                        values={
                            'col': key,
                            'val': value,
                        },
                        filtr={
                            'col': query_index,
                            'val': run_id
                        }
                    )
