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

import datetime
import pandas as pd
import streamlit as st
from assemblit import setup, db
from assemblit.server import layer
from assemblit.server import setup as server_setup
from assemblit.pages._components import _core, _selector


# Define core-component run-listing function(s)
def display_run_listing_table(
    db_name: str,
    table_name: str,
    query_index: str,
    scope_db_name: str,
    scope_query_index: str,
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

    # Initialize the connection to the scope database
    Session = db.Handler(
        db_name=scope_db_name
    )

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

    if server_health:

        # Get analysis-runs
        try:
            df = pd.read_sql(
                sql="SELECT * FROM %s WHERE %s IN (%s)" % (
                    table_name,
                    query_index,
                    ', '.join(["'%s'" % (i) for i in Session.select_table_column_value(
                        table_name=table_name,
                        col=query_index,
                        filtr={
                            'col': scope_query_index,
                            'val': st.session_state[setup.NAME][scope_db_name][scope_query_index]
                        },
                        multi=True
                    )])
                ),
                con=Analysis.connection
            )
            df = df[[
                'created_on',
                'file_name',
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
                        'state': layer.all_job_states(server_type=server_setup.SERVER_TYPE),
                        'status': layer.all_job_statuses(server_type=server_setup.SERVER_TYPE)
                    }
                ),
                how='left',
                left_on=['state'],
                right_on=['state'],
                validate='m:1'
            )
            df['created_on'] = pd.to_datetime(df['created_on'])
        except db.NullReturnValue:
            df = pd.DataFrame(
                columns=[
                    'created_on',
                    'file_name',
                    'name',
                    'submitted_by',
                    'state',
                    'start_time',
                    'end_time',
                    'run_time',
                    'outputs',
                    'url',
                    'status'
                ]
            )

        if not df.empty:
            # Layout form columns
            _, col2, col3, col4, col5, col6, _ = st.columns([.075, .175, .175, .175, .175, .175, .05])

            # Filter date-range
            created_on_filter = col2.date_input(
                key='DateInput:%s' % _selector.generate_selector_key(
                    db_name=db_name,
                    table_name=table_name,
                    parameter='File name'
                ),
                label='Date range',
                value=(
                    max(
                        datetime.datetime.now() - datetime.timedelta(30),
                        min(list(df['created_on']))
                    ),
                    datetime.datetime.now()
                ),
                min_value=min(list(df['created_on'])),
                max_value=datetime.datetime.now(),
                format='MM/DD/YYYY'
            )

            if len(created_on_filter) == 2:
                df = df[
                    (df['created_on'] >= pd.Timestamp(created_on_filter[0]))
                    & (
                        df['created_on'] <= datetime.datetime.combine(
                            pd.Timestamp(created_on_filter[1]),
                            datetime.time.max
                        )
                    )
                ]

            file_name_filter = col3.multiselect(
                key='MultiSelect:%s' % _selector.generate_selector_key(
                    db_name=db_name,
                    table_name=table_name,
                    parameter='File name'
                ),
                label='File name',
                options=sorted(list(df['file_name'].unique())),
                max_selections=1,
                placeholder="""
                    Select a file name
                """
            )
            name_filter = col4.multiselect(
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
            if st.session_state[setup.NAME][setup.USERS_DB_NAME]['name'] in sorted(list(df['submitted_by'].unique())):
                submitted_by_filter = col5.multiselect(
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
            else:
                submitted_by_filter = col5.multiselect(
                    key='MultiSelect:%s' % _selector.generate_selector_key(
                        db_name=db_name,
                        table_name=table_name,
                        parameter='Submitted by'
                    ),
                    label='Submitted by',
                    options=sorted(list(df['submitted_by'].unique())),
                    placeholder="""
                        Select a submitter
                    """
                )

            # Display the 'Refresh' button
            col6.write('')
            col6.button(
                label='Refresh',
                type='primary',
                on_click=refresh,
                use_container_width=True,
                disabled=(not server_health or df.empty)
            )

            # Layout columns
            _, col2, _ = st.columns(setup.CONTENT_COLUMNS)

            if file_name_filter:
                df = df[df['file_name'].isin(file_name_filter)]
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
                        'file_name',
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
                        'file_name': st.column_config.TextColumn(
                            label='File name'
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

        # Display content information
        else:
            _core.display_page_content_info(
                content_info="Run an analysis to browse the listing report."
            )

    # Log errors
    else:
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
        try:
            run_ids = Analysis.select_table_column_value(
                table_name=table_name,
                col=query_index,
                filtr={
                    'col': 'state',
                    'val': layer.terminal_job_states(server_type=server_setup.SERVER_TYPE)
                },
                return_dtype='str',
                multi=True,
                order='DESC',
                contains=False
            )
        except db.NullReturnValue:
            run_ids = []

        # Poll the status of each run-id
        if run_ids:
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
