"""
Information
---------------------------------------------------------------------
Name        : data.py
Location    : ~/
Author      : Tom Eleff
Published   : 2024-02-21
Revised on  : .

Description
---------------------------------------------------------------------
Contains the web-page class for creating a data-uploader.
"""

import os
import copy
import json
import hashlib
import streamlit as st
from getstreamy import setup, db
from getstreamy.components import _core
import pandas as pd
import pandera as pa
from pandera.engines import pandas_engine
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


class Content():

    def __init__(
        self,
        header: str = 'Data',
        tagline: str = 'Upload, review and verify data for the session.',
        content_info: str = (
            'Navigate to the **%s** page to load a session.' % (
                ''.join([
                    setup.SESSIONS_DB_NAME[0].upper(),
                    setup.SESSIONS_DB_NAME[1:].lower()
                ])
            )
        ),
        db_name: str = setup.DATA_DB_NAME,
        table_name: str = 'datasets',
        query_index: str = setup.DATA_DB_QUERY_INDEX,
        query_index_value: str = None,
        selector: dict = {
            "sort": 0,
            "type": "selectbox",
            "dtype": "str",
            "parameter": "file_name",
            "name": "Datafile name",
            "value": "",
            "kwargs": None,
            "query": {
                'db_name': setup.SESSIONS_DB_NAME,
                'table_name': 'datasets',
                'col': setup.DATA_DB_QUERY_INDEX
            },
            "description": "Select a datafile to review."
        },
        headerless: bool = False,
        data_dictionary: pd.DataFrame = pd.DataFrame(),
        data_example: pd.DataFrame = pd.DataFrame()
    ):
        """ Initializes an instance of the data-ingestion-page Class().

        Parameters
        ----------
        header : `str`
            String to display as the web-page header.
        tagline : `str`
            String to display as the web-page tagline.
        content_info : `str`
            String to display as `streamlit.info()` when there is no selected session.
        db_name : 'str'
            Name of the database to store the setting parameters & values.
        table_name : 'str'
            Name of the table within `db_name` to store the setting parameters & values.
        query_index : 'str'
            Name of the index within `db_name` & `table_name`. May only be one column.
        query_index_value : 'str'
            Name of the active or selected index value within `db_name` & `table_name`.
        selector : `list`
            Dictionary object containing the setting parameter & value to populate the
                drop-down selection options.
        data_dictionary : `pd.DataFrame`
            An optional data dictionary that describes the structure and format of the
                expected datafile.
        data_example : `pd.DataFrame`
            An optional dataframe that provides a reference for a valid datafile.
        """

        # Assign content class variables
        self.header = header
        self.tagline = tagline
        self.headerless = headerless
        self.content_info = content_info
        self.data_dictionary = data_dictionary
        self.data_example = data_example

        # Assign database class variables
        self.db_name = db_name
        self.table_name = table_name
        self.query_index = query_index
        self.query_index_value = query_index_value

        # Assign data-context class variables
        self.uploaded_df = pd.DataFrame()
        self.data_df = pd.DataFrame()
        self.datetime = None
        self.dimensions = None
        self.metrics = None
        self.aggrules = {
            'Count': 'count',
            'Sum': 'sum',
            'Min': 'min',
            'Max': 'max',
            'Mean': 'mean',
            'Median': 'median',
            'Mode': 'mode',
            'Standard Deviation': 'std',
            'Variance': 'var'
        }
        self.selected_datetime = []
        self.selected_dimensions = []
        self.selected_metrics = []
        self.selected_aggrules = []
        self.selected_file_name = []

        # Assign default session state class variables
        self.selector = selector

        # Initialize session state defaults
        if setup.NAME not in st.session_state:
            st.session_state[setup.NAME] = {}
            for index, (key, value) in enumerate(
                setup.SESSION_STATE_DEFAULTS.items()
            ):
                st.session_state[setup.NAME][key] = copy.deepcopy(value)

        # Assign key-value pair defaults
        if self.db_name not in st.session_state[setup.NAME]:
            st.session_state[setup.NAME][self.db_name] = {
                'selector': selector
            }
        else:
            if 'selector' not in st.session_state[setup.NAME][self.db_name]:
                st.session_state[setup.NAME][self.db_name]['selector'] = selector
            for index, (key, value) in enumerate(
                setup.DATA_DEFAULTS.items()
            ):
                st.session_state[setup.NAME][self.db_name][key] = copy.deepcopy(value)

        # Initialize error handling
        if 'errors' not in st.session_state[setup.NAME][self.db_name]:
            st.session_state[setup.NAME][self.db_name]['errors'] = []
        if 'successes' not in st.session_state[setup.NAME][self.db_name]:
            st.session_state[setup.NAME][self.db_name]['successes'] = []

    def serve(self):
        """ Serves the data-ingestion-page content.
        """

        # Manage authentication
        if st.session_state[setup.NAME][setup.AUTH_NAME][setup.AUTH_QUERY_INDEX]:

            # Display standard web-page header
            _core.display_page_header(
                header=self.header,
                tagline=self.tagline,
                headerless=self.headerless
            )

            # Manage the active session
            if st.session_state[setup.NAME][setup.SESSIONS_DB_NAME][setup.SESSIONS_DB_QUERY_INDEX]:

                # Layout columns
                col1, col2, col3 = st.columns(setup.CONTENT_COLUMNS)

                # Initialize the connection to the session-selector database
                Sessions = db.Handler(
                    db_name=setup.SESSIONS_DB_NAME
                )

                # Create table in users
                Sessions.create_table(
                    table_name=self.table_name,
                    cols=(
                        [setup.SESSIONS_DB_QUERY_INDEX] + [self.query_index]
                    )
                )

                # Initialize the connection to the data-ingestion database
                Database = db.Handler(
                    db_name=self.db_name
                )

                # Create table in the data-ingestion database
                Database.create_table(
                    table_name=self.table_name,
                    cols=(
                        [
                            self.query_index,
                            'uploaded_by',
                            'created_on',
                            'final',
                            'version',
                            'file_name',
                            'dbms',
                            'datetime',
                            'dimensions',
                            'metrics',
                            'selected_datetime',
                            'selected_dimensions',
                            'selected_metrics',
                            'selected_aggrules',
                            'size_mb',
                            'sha256'
                        ]
                    )
                )

                # Display the data-ingestion-page content
                with col2:

                    # Display the data contract
                    if (
                        (not self.data_dictionary.empty) or (not self.data_example.empty)
                    ):

                        # Display the header
                        st.subheader('Data contract')
                        st.write('The **data contract** defines the structure and format of the data.')

                        # Display the expander
                        with st.expander(
                            label='📝 Expand for details on the **data contract**.',
                            expanded=False
                        ):
                            # Display the data dictionary
                            if not self.data_dictionary.empty:
                                st.write('#### Dictionary')
                                st.write('The data dictionary describes the **data contract** of the data.')
                                st.dataframe(
                                    data=self.data_dictionary,
                                    hide_index=True,
                                    use_container_width=True
                                )

                            # Display the data example
                            if not self.data_example.empty:
                                st.write('#### Example')
                                st.write('Click ```Download``` to download a reference datafile in the **data contract**.')
                                st.download_button(
                                    label='Download',
                                    data=self.data_example.to_csv(
                                        sep=',',
                                        index=False
                                    ).encode('utf8'),
                                    file_name='data_example.csv',
                                    mime='text/csv',
                                    type='primary'
                                )

                    # Display the data uploader
                    st.subheader('Upload')
                    st.write(
                        'Upload a datafile in ```.csv``` or ```.parquet``` format. Click ```Upload``` to save the datafile.'
                    )

                    with st.form(
                        key='uploader-%s' % (self.table_name),
                        border=True,
                        clear_on_submit=True
                    ):

                        # Display the data-ingestion file uploader
                        data = st.file_uploader(
                            label=('Upload a datafile in ```.csv``` or ```.parquet``` format.'),
                            key='FileUploader:%s' % (self.db_name),
                            type=['csv', 'parquet'],
                            label_visibility='collapsed'
                        )

                        # Layout form columns
                        col1, col2, col3 = st.columns([.6, .2, .2])

                        # Display the 'Upload' button
                        upload = col2.form_submit_button(
                            label='Upload',
                            type='primary',
                            use_container_width=True
                        )
                        col3.form_submit_button(
                            label='Cancel',
                            type='secondary',
                            use_container_width=True
                        )

                    # Display schema validation and data-preview
                    if data is not None and upload:

                        # Check the datafile format
                        dbms = str(os.path.splitext(data.name)[1]).strip().upper()

                        # Read the datafile
                        if dbms in ['.CSV', '.PARQUET']:
                            if dbms == '.CSV':

                                # Read '.csv'
                                df = pd.read_csv(
                                    data,
                                    sep=','
                                )

                            if dbms == '.PARQUET':

                                # Read '.parquet'
                                df = pd.read_parquet(
                                    data,
                                    engine='pyarrow'
                                )

                            # Normalize column names
                            df.columns = [c.lower() for c in df.columns]

                            # Identify and format the datetime dimension
                            self.datetime = parse_datetime_dimension(df=df)

                            # Identify categorical dimensions
                            #   If the datatype is a(n),
                            #       <b> boolean
                            #       <O> object
                            #       <S> (byte-)string
                            #       <U> unicode
                            #
                            #   > Then the column is a dimension
                            self.dimensions = [
                                dim for dim in set(df.columns) if (
                                    (df[dim].dtype.kind in 'bOSU')
                                    and (dim not in [dt[0] for dt in self.datetime])
                                )
                            ]

                            # Identify metrics
                            #   If the datatype is a(n),
                            #       <i> signed integer
                            #       <u> unsighted integer
                            #       <f> floating-point
                            #       <c> complex floating-point
                            #
                            #   > Then the column is a metric
                            self.metrics = [
                                dim for dim in set(df.columns) if (
                                    (df[dim].dtype.kind in 'iufc')
                                )
                            ]

                            # Compile schema validation rules
                            rules = {}

                            # Add datetime rules
                            for dt in self.datetime:
                                rules[dt[0]] = pa.Column(
                                    pandas_engine.DateTime(
                                        to_datetime_kwargs={
                                            "format": dt[1]
                                        }
                                    )
                                )

                            # Add dimension rules
                            for col in self.dimensions:
                                rules[col] = pa.Column(
                                    str,
                                    nullable=False
                                )

                            # Add metric rules
                            for col in self.metrics:
                                rules[col] = pa.Column(
                                    float,
                                    nullable=True
                                )

                            # Create unique dimensions
                            if self.datetime:
                                unique_dimensions = (
                                    [d[0] for d in self.datetime] + self.dimensions
                                )
                            else:
                                unique_dimensions = self.dimensions

                            # Check the dataframe schema and column data-types
                            schema = pa.DataFrameSchema(
                                rules,
                                strict=True,
                                coerce=True,
                                unique=unique_dimensions,
                                report_duplicates='all',
                                checks=pa.Check(
                                    lambda df: df.shape[0] > 0,
                                    name='not_empty'
                                )
                            )

                            # Display the schema validation content
                            st.subheader('Schema validation')
                            st.write(
                                """
                                    Schema validation checks the datafile, identifying date-time dimensions,
                                     categorical dimensions and metrics, raising any inconsistencies with the
                                     **data contract**.
                                """
                            )

                            # Apply schema
                            try:
                                df = schema.validate(df, lazy=True)

                                # Apply datetime formatting
                                for dt in self.datetime:
                                    df[dt[0]] = df[dt[0]].dt.strftime(dt[1])

                                # Display the status
                                st.success(
                                    body='Schema validation completed successfully.',
                                    icon='✅'
                                )

                                # Display the data-preview content
                                st.subheader(
                                    'Preview'
                                )
                                st.write('Preview of the first 5 observations.')
                                st.dataframe(
                                    df.head(5),
                                    hide_index=True,
                                    use_container_width=True
                                )

                                # Promote the uploaded datafile to the database
                                self.promote_data_to_database(
                                    df=df.copy(),
                                    dbms=dbms,
                                    file_name=data.name,
                                    file_size=data.size
                                )

                            # Raise schema errors
                            except pa.errors.SchemaErrors as err:
                                st.error(
                                    body="""
                                        Schema validation failed. The dataframe structure does not
                                         comply with the **data contract** requirements. See the dataframe
                                         output below for more information. Please re-upload the datafile.
                                    """,
                                    icon='⛔'
                                )
                                col1, col2 = st.columns([0.25, 6.75])
                                col2.dataframe(
                                    err.failure_cases,
                                    hide_index=True,
                                    use_container_width=True,
                                    column_config={
                                        "schema_context": None,
                                        "column": (
                                            st.column_config.TextColumn(
                                                "Column",
                                                help=''.join([
                                                    'Name of the column',
                                                    ' (if applicable)'
                                                ])
                                            )
                                        ),
                                        "check": (
                                            st.column_config.TextColumn(
                                                "Schema Check",
                                                help=''.join([
                                                    'Name of the schema',
                                                    ' validation check'
                                                ])
                                            )
                                        ),
                                        "check_number": None,
                                        "failure_case": (
                                            st.column_config.TextColumn(
                                                "Validation Check",
                                                help=''.join([
                                                    'Status of the schema',
                                                    ' validation error'
                                                ])
                                            )
                                        ),
                                        "index": (
                                            st.column_config.NumberColumn(
                                                "Dataframe Index",
                                                help=''.join([
                                                    'Index of the schema'
                                                    ' validation error'
                                                ]),
                                                format="%d",
                                            )
                                        )
                                    }
                                )

                        else:

                            # Log errors
                            st.session_state[setup.NAME][self.db_name]['errors'] = (
                                st.session_state[setup.NAME][self.db_name]['errors']
                                + [''.join([
                                    'Invalid file format. The data uploader expects either a comma-separated',
                                    ' ```.csv``` or a ```.parquet``` file. Please re-upload the datafile in a',
                                    ' supported format.'
                                ])]
                            )

                        # Reset the data uploader variable
                        del data

                    # Display the data-review
                    st.subheader('Review')
                    st.write(
                        """
                            Select an uploaded datafile and review the summary report.
                            - Click ```Finalize``` to set the selected datafile as final.
                            - Click ```Save``` to update the default drop-down selections for the selected datafile.
                            - Click ```Delete``` to delete the selected datafile.
                        """
                    )

                    try:

                        # Display the datafile selectors
                        with st.container(border=True):

                            # Retreive drop-down selector options & set button state
                            try:
                                options = Database.select_table_column_value(
                                    table_name=self.table_name,
                                    col=st.session_state[setup.NAME][self.db_name]['selector']['parameter'],
                                    filtr={
                                        'col': self.query_index,
                                        'val': Sessions.select_table_column_value(
                                            table_name=self.table_name,
                                            col=self.query_index,
                                            filtr={
                                                'col': setup.SESSIONS_DB_QUERY_INDEX,
                                                'val': st.session_state[
                                                    setup.NAME
                                                ][
                                                    setup.SESSIONS_DB_NAME
                                                ][
                                                    setup.SESSIONS_DB_QUERY_INDEX
                                                ]
                                            },
                                            multi=True,
                                            return_dtype='str'
                                        )
                                    },
                                    multi=True,
                                    return_dtype='str'
                                )
                                button_state = False
                            except db.NullReturnValue:
                                options = []
                                button_state = True

                            # Select the index of the default drop-down selection
                            try:

                                # Select the 'Final' version of the session datafile
                                index = options.index(
                                    Database.select_table_column_value(
                                        table_name=self.table_name,
                                        col=st.session_state[setup.NAME][self.db_name]['selector']['parameter'],
                                        filtr={
                                            'col': 'final',
                                            'val': True
                                        },
                                        return_dtype='str'
                                    )
                                )

                            except db.NullReturnValue:

                                # Select the most recent version of the session datafile
                                try:
                                    index = options.index(
                                        db.as_type(
                                            [
                                                i[0] for i in Database.cursor.execute(
                                                    """
                                                        SELECT %s FROM %s
                                                            WHERE %s IN (%s)
                                                                ORDER BY %s DESC
                                                                    LIMIT 1;
                                                    """ % (
                                                        st.session_state[setup.NAME][self.db_name]['selector']['parameter'],
                                                        self.table_name,
                                                        self.query_index,
                                                        ', '.join(["'%s'" % (i) for i in Sessions.select_table_column_value(
                                                            table_name=self.table_name,
                                                            col=self.query_index,
                                                            filtr={
                                                                'col': setup.SESSIONS_DB_QUERY_INDEX,
                                                                'val': st.session_state[
                                                                    setup.NAME
                                                                ][
                                                                    setup.SESSIONS_DB_NAME
                                                                ][
                                                                    setup.SESSIONS_DB_QUERY_INDEX
                                                                ]
                                                            },
                                                            multi=True,
                                                            return_dtype='str'
                                                        )]),
                                                        'version'
                                                    )
                                                ).fetchall()
                                            ][0],
                                            return_dtype='str'
                                        )
                                    )

                                except IndexError:

                                    # Set the default index
                                    index = 0

                            # Apply defaults to the session state
                            if options:
                                st.session_state[setup.NAME][self.db_name]['name'] = options[index]
                                st.session_state[setup.NAME][self.db_name]['selector']['value'] = options[index]

                                # Set query index value
                                st.session_state[setup.NAME][self.db_name][self.query_index] = self.select_query_index_value(
                                    filtr={
                                        'col': st.session_state[setup.NAME][self.db_name]['selector']['parameter'],
                                        'val': options[index]
                                    }
                                )
                                self.query_index_value = st.session_state[setup.NAME][self.db_name][self.query_index]

                            # Layout selector columns
                            col1, col2, col3, col4 = st.columns([.4, .2, .2, .2])

                            # Display datafile selector
                            self.selected_file_name = col1.selectbox(
                                label='Datafile name',
                                key='Selector:%s-%s' % (
                                    self.db_name,
                                    st.session_state[setup.NAME][self.db_name]['selector']['parameter']
                                ),
                                options=options,
                                index=index,
                                placeholder='Select a datafile for review',
                                on_change=self.set_query_index_value
                            )

                            # Display the 'Finalize' button
                            col2.subheader('')
                            col2.button(
                                label='Finalize',
                                key='Button:%s-finalize' % (self.db_name),
                                on_click=self.finalize,
                                type='primary',
                                use_container_width=True,
                                disabled=button_state
                            )

                            # Display the 'Save' button
                            col3.subheader('')
                            col3.button(
                                label='Save',
                                key='Button:%s-save' % (self.db_name),
                                on_click=self.save,
                                type='secondary',
                                use_container_width=True,
                                disabled=button_state
                            )

                            # Display the 'Delete' button
                            col4.subheader('')
                            col4.button(
                                label='Delete',
                                key='Button:%s-delete' % (self.db_name),
                                on_click=self.delete,
                                type='secondary',
                                use_container_width=True,
                                disabled=button_state
                            )

                        # Display the data-review summary report
                        if options:
                            self.data_df = self.retrieve_data_from_database()

                            if not self.data_df.empty:
                                self.display_data_review(
                                    df=self.data_df
                                )
                            else:
                                st.info(
                                    'Upload a datafile to review the summary report.',
                                    icon='ℹ️'
                                )
                        else:
                            st.info(
                                'Upload a datafile to review the summary report.',
                                icon='ℹ️'
                            )

                    except db.NullReturnValue:

                        # Display information
                        st.info(
                            body="""
                                Upload a datafile in the **data contract**
                                 to review the summary report.
                            """,
                            icon='ℹ️'
                        )

                    # Check data upload successes
                    if st.session_state[setup.NAME][self.db_name]['successes']:
                        for success in st.session_state[setup.NAME][self.db_name]['successes']:
                            st.success(
                                body=success,
                                icon='✅'
                            )

                    # Reset data upload successes
                    st.session_state[setup.NAME][self.db_name]['successes'] = []

                    # Check data upload errors
                    if st.session_state[setup.NAME][self.db_name]['errors']:
                        for error in st.session_state[setup.NAME][self.db_name]['errors']:
                            st.error(
                                body=error,
                                icon='⛔'
                            )

                    # Reset data upload errors
                    st.session_state[setup.NAME][self.db_name]['errors'] = []

            else:

                # Display content information
                _core.display_page_content_info(
                    content_info=self.content_info
                )

        else:

            # Return to home-page
            st.switch_page(st.session_state[setup.NAME]['pages']['home'])

    # Define call-back function(s)
    def display_data_review(
        self,
        df: pd.DataFrame
    ):
        """ Displays the data review content.

        Parameters
        ----------
        df : `pd.DataFrame`
            Pandas dataframe object to review.
        """

        # Format selector options
        self.datetime.sort()
        self.dimensions.sort()
        self.metrics.sort()

        # Display selectors
        with st.container(border=True):

            if self.datetime:

                # Layout columns when (a) datetime dimension(s) exist(s)
                col1, col2, col3, col4 = st.columns(
                    [.25, .25, .25, .25]
                )
                self.selected_datetime = col1.multiselect(
                    key='MultiSelect:datetime',
                    label='Timeseries name',
                    options=[dt[0] for dt in self.datetime],
                    default=self.selected_datetime,
                    max_selections=1,
                    placeholder="""
                        Select the datetime dimension
                    """
                )
                self.selected_dimensions = col2.multiselect(
                    key='MultiSelect:dimensions',
                    label='Dimension name',
                    options=self.dimensions,
                    default=self.selected_dimensions,
                    max_selections=1,
                    placeholder="""
                        Select a summary dimension
                    """
                )
                self.selected_metrics = col3.multiselect(
                    key='MultiSelect:metrics',
                    label='Metric name',
                    options=self.metrics,
                    default=self.selected_metrics,
                    max_selections=1,
                    placeholder="""
                        Select a summary metric
                    """
                )
                self.selected_aggrules = col4.multiselect(
                    key='MultiSelect:aggrules',
                    label='Metric agg. rule',
                    options=self.aggrules.keys(),
                    default=self.selected_aggrules,
                    max_selections=1,
                    placeholder="""
                        Select a metric aggregation rule
                    """
                )

            else:

                # Layout columns when no datetime dimension exists
                col1, col2, col3 = st.columns(
                    [.333, .333, .333]
                )
                self.selected_dimensions = col1.multiselect(
                    key='MultiSelect:dimensions',
                    label='Dimension name',
                    options=self.dimensions,
                    default=self.selected_dimensions,
                    max_selections=1,
                    placeholder="""
                        Select a summary dimension
                    """
                )
                self.selected_metrics = col2.multiselect(
                    key='MultiSelect:metrics',
                    label='Metric name',
                    options=self.metrics,
                    default=self.selected_metrics,
                    max_selections=1,
                    placeholder="""
                        Select a summary metric
                    """
                )
                self.selected_aggrules = col3.multiselect(
                    key='MultiSelect:aggrules',
                    label='Metric aggregation rule',
                    options=self.aggrules.keys(),
                    default=self.selected_aggrules,
                    max_selections=1,
                    placeholder="""
                        Select a metric aggregation rule
                    """
                )

        # Display plots
        if (
            (self.selected_metrics)
            and (self.selected_aggrules)
        ):

            # Plot timeseries
            if self.selected_datetime:
                with st.container(border=True):

                    # Display subheader
                    st.write('#### Timeseries plot')
                    st.write(
                        """
                            Review the trends of the data over-time. Use the 📷 icon
                             in the upper-right corner of the plot to download a ```.png``` screenshot.
                        """
                    )

                    if self.selected_dimensions:
                        st.plotly_chart(
                            figure_or_data=self.plot_timeseries(
                                df=df,
                                datetime=self.selected_datetime,
                                dimension=self.selected_dimensions,
                                metrics=self.selected_metrics,
                                aggrules=[
                                    self.aggrules[r] for r in (self.selected_aggrules)
                                ]
                            ),
                            theme='streamlit',
                            use_container_width=True
                        )
                    else:
                        st.plotly_chart(
                            figure_or_data=self.plot_timeseries(
                                df=df,
                                datetime=self.selected_datetime,
                                dimension=None,
                                metrics=self.selected_metrics,
                                aggrules=[
                                    self.aggrules[r] for r in (self.selected_aggrules)
                                ]
                            ),
                            theme='streamlit',
                            use_container_width=True
                        )

            # Display descriptive statistics
            with st.container(border=True):

                # Display subheader
                st.write('#### Descriptive summary')
                st.write(
                    """
                        Review the descriptive statistics of the data. Use the 📷 icon
                         in the upper-right corner of the table to download a ```.png``` screenshot.
                    """
                )

                if self.selected_dimensions:
                    descriptives_df = self.describe_df(
                        df=df,
                        dimension=self.selected_dimensions,
                        metrics=self.selected_metrics,
                        aggrules=[
                            self.aggrules[r] for r in (self.selected_aggrules)
                        ]
                    )
                    formats = [
                        ',.2f' if (
                            descriptives_df[col].dtype == 'float64'
                        ) else '' for col in descriptives_df.columns
                    ]
                    alignments = [
                        'right' if (
                            descriptives_df[col].dtype == 'float64'
                        ) else 'center' for col in descriptives_df.columns
                    ]

                    st.plotly_chart(
                        figure_or_data=go.Figure(
                            data=[
                                go.Table(
                                    header=dict(
                                        values=list(descriptives_df.columns),
                                        align='center',
                                        height=24
                                    ),
                                    cells=dict(
                                        values=descriptives_df.T.values.tolist(),
                                        align=alignments,
                                        height=24,
                                        format=formats
                                    )
                                )
                            ],
                        ).update_layout(
                            height=24*int(len(descriptives_df) + 1) + 25,
                            margin={
                                't': 24,
                                'l': 0,
                                'b': 0,
                                'r': 1
                            }
                        ),
                        theme='streamlit',
                        use_container_width=True
                    )

                else:
                    descriptives_df = self.describe_df(
                        df=df,
                        dimension=None,
                        metrics=self.selected_metrics,
                        aggrules=[
                            self.aggrules[r] for r in (self.selected_aggrules)
                        ]
                    )
                    formats = [
                        ',.2f' if (
                            descriptives_df[col].dtype == 'float64'
                        ) else '' for col in descriptives_df.columns
                    ]
                    alignments = [
                        'right' if (
                            descriptives_df[col].dtype == 'float64'
                        ) else 'center' for col in descriptives_df.columns
                    ]

                    st.plotly_chart(
                        figure_or_data=go.Figure(
                            data=[
                                go.Table(
                                    header=dict(
                                        values=list(descriptives_df.columns),
                                        align='center',
                                        height=24
                                    ),
                                    cells=dict(
                                        values=descriptives_df.T.values.tolist(),
                                        align=alignments,
                                        height=24,
                                        format=formats
                                    )
                                )
                            ]
                        ).update_layout(
                            height=24*int(len(descriptives_df) + 1) + 25,
                            margin={
                                't': 24,
                                'l': 0,
                                'b': 0,
                                'r': 1
                            }
                        ),
                        theme='streamlit',
                        use_container_width=True
                    )

        else:

            # Display information
            st.info(
                'Select a metric and aggregation rule to produce the data-review reports.',
                icon='ℹ️'
            )

    def set_query_index_value(self):

        # Update session state
        st.session_state[setup.NAME][self.db_name]['name'] = st.session_state['Selector:%s-%s' % (
                self.db_name,
                st.session_state[setup.NAME][self.db_name]['selector']['parameter']
            )
        ]

        st.session_state[setup.NAME][self.db_name][self.query_index] = self.select_query_index_value(
            filtr={
                'col': st.session_state[setup.NAME][self.db_name]['selector']['parameter'],
                'val': st.session_state['Selector:%s-%s' % (
                    self.db_name,
                    st.session_state[setup.NAME][self.db_name]['selector']['parameter']
                )]
            }
        )

        # Set query index value
        self.query_index_value = st.session_state[setup.NAME][self.db_name][self.query_index]

    def select_query_index_value(self, filtr):
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

        # Initialize connection to the sessions-database
        Sessions = db.Handler(
            db_name=setup.SESSIONS_DB_NAME
        )

        # Initialize connection to the data-ingestion database
        Database = db.Handler(
            db_name=self.db_name
        )

        values = Database.cursor.execute(
            """
            SELECT %s
                FROM %s
                    WHERE %s IN (%s)
                        AND %s = '%s';
            """ % (
                self.query_index,
                self.table_name,
                self.query_index,
                ', '.join(
                    ["'%s'" % (i) for i in Sessions.select_table_column_value(
                        table_name=self.table_name,
                        col=self.query_index,
                        filtr={
                            'col': setup.SESSIONS_DB_QUERY_INDEX,
                            'val': st.session_state[setup.NAME][setup.SESSIONS_DB_NAME][setup.SESSIONS_DB_QUERY_INDEX]
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

    def retrieve_data_from_database(
        self
    ) -> pd.DataFrame:
        """ Retrieves a database table and returns it as a `pd.DataFrame`.
        """

        # Initialize the connection to the session-selector database
        Sessions = db.Handler(
            db_name=setup.SESSIONS_DB_NAME
        )

        # Initialize connection to the data-ingestion database
        Database = db.Handler(
            db_name=self.db_name
        )

        # Retrieve the selected datafile
        if self.selected_file_name:

            # Create an id from the session name and file name
            string_to_hash = ''.join(
                [st.session_state[setup.NAME][setup.SESSIONS_DB_NAME]['name']] + [self.selected_file_name]
            )

            # Generate id
            dataset_id = hashlib.md5(
                string_to_hash.lower().encode('utf-8')
            ).hexdigest()

            # Check if the id already exists
            try:
                ids = Sessions.select_table_column_value(
                    table_name=self.table_name,
                    col=self.query_index,
                    filtr={
                        'col': setup.SESSIONS_DB_QUERY_INDEX,
                        'val': st.session_state[setup.NAME][setup.SESSIONS_DB_NAME][setup.SESSIONS_DB_QUERY_INDEX]
                    },
                    multi=True
                )
            except db.NullReturnValue:
                ids = []

            if dataset_id in ids:

                # Import the datafile
                df = pd.read_sql(
                    sql="""
                        SELECT * FROM '%s';
                    """ % dataset_id,
                    con=Database.connection
                )

                # Set selector options
                self.datetime = Database.select_generic_query(
                    query="""
                        SELECT datetime FROM %s
                            WHERE %s = '%s';
                    """ % (
                        self.table_name,
                        self.query_index,
                        dataset_id
                    ),
                    return_dtype='list'
                )
                self.dimensions = Database.select_generic_query(
                    query="""
                        SELECT dimensions FROM %s
                            WHERE %s = '%s';
                    """ % (
                        self.table_name,
                        self.query_index,
                        dataset_id
                    ),
                    return_dtype='list'
                )
                self.metrics = Database.select_generic_query(
                    query="""
                        SELECT metrics FROM %s
                            WHERE %s = '%s';
                    """ % (
                        self.table_name,
                        self.query_index,
                        dataset_id
                    ),
                    return_dtype='list'
                )

                # Set selector defaults
                try:
                    self.selected_datetime = Database.select_generic_query(
                        query="""
                            SELECT selected_datetime FROM %s
                                WHERE %s = '%s';
                        """ % (
                            self.table_name,
                            self.query_index,
                            dataset_id
                        ),
                        return_dtype='list'
                    )
                except db.NullReturnValue:
                    self.selected_datetime = []
                self.selected_dimensions = Database.select_generic_query(
                    query="""
                        SELECT selected_dimensions FROM %s
                            WHERE %s = '%s';
                    """ % (
                        self.table_name,
                        self.query_index,
                        dataset_id
                    ),
                    return_dtype='list'
                )
                self.selected_metrics = Database.select_generic_query(
                    query="""
                        SELECT selected_metrics FROM %s
                            WHERE %s = '%s';
                    """ % (
                        self.table_name,
                        self.query_index,
                        dataset_id
                    ),
                    return_dtype='list'
                )
                self.selected_aggrules = Database.select_generic_query(
                    query="""
                        SELECT selected_aggrules FROM %s
                            WHERE %s = '%s';
                    """ % (
                        self.table_name,
                        self.query_index,
                        dataset_id
                    ),
                    return_dtype='list'
                )

                # Check that the datafile hash matches
                if not hashlib.sha256(
                    df.to_string().encode('utf8')
                ).hexdigest() == Database.select_generic_query(
                    query="""
                        SELECT sha256 FROM %s
                            WHERE %s = '%s';
                    """ % (
                        self.table_name,
                        self.query_index,
                        dataset_id
                    ),
                    return_dtype='str'
                ):
                    st.warning("""
                            Modified content. The hash of the most recently uploaded datafile ```%s```
                             does not match the hash of the original data. There may be un-expected
                             changes to the data as a result.
                        """ % (
                            self.selected_file_name
                        ),
                        icon='⚠️'
                    )

            else:

                # Set empty dataframe
                df = pd.DataFrame()

                # Log errors
                st.session_state[setup.NAME][self.db_name]['errors'] = (
                    st.session_state[setup.NAME][self.db_name]['errors']
                    + [''.join([
                        """
                            Missing datafile. The selected data file ```%s``` does not exist.
                             Please upload a new datafile.
                        """ % (
                            self.selected_file_name
                        )
                    ])]
                )

        return df

    def promote_data_to_database(
        self,
        df: pd.DataFrame,
        dbms: str,
        file_name: str,
        file_size: float
    ):
        """ Promotes the uploaded datafile to the database.

        Parameters
        ----------
        df : `pd.DataFrame`
            Pandas dataframe object to promote to the database.
        dbms : `str`
            Database management system name of the data to promote ('csv', 'parquet').
        file_name : `str`
            Name of the datafile.
        file_size : `str`
            Size of the datafile.
        """

        # Initialize the connection to the session-selector database
        Sessions = db.Handler(
            db_name=setup.SESSIONS_DB_NAME
        )

        # Initialize connection to the data-ingestion database
        Database = db.Handler(
            db_name=self.db_name
        )

        # Retrieve the latest data version number
        try:
            version = int(
                Database.select_generic_query(
                    query="""
                        SELECT MAX(version) FROM %s
                            WHERE %s in (%s);
                    """ % (
                        self.table_name,
                        self.query_index,
                        ', '.join(["'%s'" % (i) for i in Sessions.select_table_column_value(
                            table_name=self.table_name,
                            col=self.query_index,
                            filtr={
                                'col': setup.SESSIONS_DB_QUERY_INDEX,
                                'val': st.session_state[
                                    setup.NAME
                                ][
                                    setup.SESSIONS_DB_NAME
                                ][
                                    setup.SESSIONS_DB_QUERY_INDEX
                                ]
                            },
                            multi=True
                        )])
                    ),
                    return_dtype='int'
                ) + 1
            )

        except (TypeError, db.NullReturnValue):
            version = 1

        # Create an id from the session name and file name
        string_to_hash = ''.join(
            [st.session_state[setup.NAME][setup.SESSIONS_DB_NAME]['name']] + [file_name]
        )

        # Generate id
        self.query_index_value = hashlib.md5(
            string_to_hash.lower().encode('utf-8')
        ).hexdigest()

        # Check if the file name already exists
        if Database.table_exists(table_name=self.query_index_value) == 0:

            # Update the session-selector database
            Sessions.insert(
                table_name=self.table_name,
                values={
                    setup.SESSIONS_DB_QUERY_INDEX: (
                        st.session_state[setup.NAME][setup.SESSIONS_DB_NAME][setup.SESSIONS_DB_QUERY_INDEX]
                    ),
                    self.query_index: self.query_index_value
                }
            )

            # Update the data ingestion database
            Database.insert(
                table_name=self.table_name,
                values={
                    self.query_index: (
                        self.query_index_value
                    ),
                    'uploaded_by': st.session_state[setup.NAME][setup.USERS_DB_NAME]['name'],
                    'created_on': datetime.now(),
                    'final': False,
                    'version': version,
                    'file_name': file_name,
                    'dbms': dbms,
                    'datetime': json.dumps(self.datetime),
                    'dimensions': json.dumps(self.dimensions),
                    'metrics': json.dumps(self.metrics),
                    'selected_datetime': json.dumps(self.selected_datetime),
                    'selected_dimensions': json.dumps(self.selected_dimensions),
                    'selected_metrics': json.dumps(self.selected_metrics),
                    'selected_aggrules': json.dumps(self.selected_aggrules),
                    'size_mb': round(file_size / 1024, 6),
                    'sha256': hashlib.sha256(df.to_string().encode('utf8')).hexdigest()
                },
                validate={
                    'col': 'file_name',
                    'val': file_name
                }
            )

            # Promote the datafile to the data-ingestion database as a table
            df.to_sql(
                name=self.query_index_value,
                con=Database.connection,
                index=False
            )

            # Set session state
            #   self.query_index_value is already set
            st.session_state[setup.NAME][self.db_name]['name'] = file_name
            st.session_state[setup.NAME][self.db_name][self.query_index] = (
                self.query_index_value
            )

            # Log successes
            st.success(
                body="""
                    The file ```%s``` was uploaded successfully.
                """ % (file_name),
                icon='✅'
            )

        else:

            # ADD CONDITION TO "UPDATE" A PREVIOUSLY UPLOADED FILE

            # Log successes
            st.success(
                body="""
                    The file ```%s``` was uploaded successfully.
                """ % (file_name),
                icon='✅'
            )

    def finalize(
        self
    ):
        """ Finalizes the selected datafile within the data-ingestion database table.
        """

        # Initialize connection to the data-ingestion database
        Database = db.Handler(
            db_name=self.db_name
        )

        # Reset all datasets
        Database.reset_table_column_value(
            table_name=self.table_name,
            values={
                'col': 'final',
                'val': False
            }
        )

        # Set the selected datafile as final
        Database.update(
            table_name=self.table_name,
            values={
                'col': 'final',
                'val': True
            },
            filtr={
                'col': self.query_index,
                'val': st.session_state[setup.NAME][self.db_name][self.query_index]
            }
        )

    def save(
        self
    ):
        """ Updates the drop-down selection defaults stored within the data-ingestion database table for the selected datafile.
        """

        # Initialize connection to the data-ingestion database
        Database = db.Handler(
            db_name=self.db_name
        )

        # Update the database with the latest selected values
        Database.update(
            table_name=self.table_name,
            values={
                'col': 'selected_datetime',
                'val': json.dumps(self.selected_datetime)
            },
            filtr={
                'col': self.query_index,
                'val': st.session_state[setup.NAME][self.db_name][self.query_index]
            }
        )
        Database.update(
            table_name=self.table_name,
            values={
                'col': 'selected_dimensions',
                'val': json.dumps(self.selected_dimensions)
            },
            filtr={
                'col': self.query_index,
                'val': st.session_state[setup.NAME][self.db_name][self.query_index]
            }
        )
        Database.update(
            table_name=self.table_name,
            values={
                'col': 'selected_metrics',
                'val': json.dumps(self.selected_metrics)
            },
            filtr={
                'col': self.query_index,
                'val': st.session_state[setup.NAME][self.db_name][self.query_index]
            }
        )
        Database.update(
            table_name=self.table_name,
            values={
                'col': 'selected_aggrules',
                'val': json.dumps(self.selected_aggrules)
            },
            filtr={
                'col': self.query_index,
                'val': st.session_state[setup.NAME][self.db_name][self.query_index]
            }
        )

    def delete(
        self
    ):
        """ Deletes the selected datafile from all tables within the data-ingestion database.
        """

        # Initialize connection to the data-ingestion database
        Database = db.Handler(
            db_name=self.db_name
        )

        # Remove the table metadata
        Database.delete(
            table_name=self.table_name,
            filtr={
                'col': self.query_index,
                'val': st.session_state[setup.NAME][self.db_name][self.query_index]
            }
        )

        # Remove the datafile table
        Database.drop_table(
            table_name=st.session_state[setup.NAME][self.db_name][self.query_index]
        )

    def plot_timeseries(
        self,
        df: pd.DataFrame,
        datetime: list = None,
        dimension: list = None,
        metrics: list = None,
        aggrules: list = None
    ) -> go.Line:
        """ Creates a time-series line-plot and returns a Plotly `go.Line` object.

        Parameters
        ----------
        df : `pd.DataFrame`
            Pandas dataframe object to plot.
        datetime : `list`
            Ordered list of the date-time columns in `df`.
        dimension : `list`
            Ordered list of categorical columns in `df` to group the records.
        metrics : `list`
            Ordered list of numeric columns in `df` to summarize by `aggrules`.
        aggrules : `list`
            Ordered list of aggregation rules that determine the aggregation of the `metrics`.
        """

        if dimension:
            line_plot = px.line(
                data_frame=self.agg_df(
                    df=df,
                    datetime=datetime,
                    dimension=dimension,
                    metrics=metrics,
                    aggrules=aggrules
                ),
                x=datetime[0],
                y=metrics,
                line_group=dimension[0],
                color=dimension[0]
            ).update_layout(
                height=400,
                margin={
                    't': 24,
                    'l': 0,
                    'b': 0,
                    'r': 8
                }
            )
        else:
            line_plot = px.line(
                data_frame=self.agg_df(
                    df=df,
                    datetime=datetime,
                    dimension=None,
                    metrics=metrics,
                    aggrules=aggrules
                ),
                x=datetime[0],
                y=metrics
            ).update_layout(
                height=400,
                margin={
                    't': 24,
                    'l': 0,
                    'b': 0,
                    'r': 8
                }
            )

        return line_plot

    def agg_df(
        self,
        df: pd.DataFrame,
        datetime: list = None,
        dimension: list = None,
        metrics: list = None,
        aggrules: list = None
    ) -> pd.DataFrame:
        """ Groups `df` by `dimensions` and/or `datetime` and aggregates `metrics` with `aggrules`
        returning a `pd.Dataframe`.

        Parameters
        ----------
        df : `pd.DataFrame`
            Pandas dataframe object to aggregate.
        datetime : `list`
            Ordered list of the date-time columns in `df`.
        dimension : `list`
            Ordered list of categorical columns in `df` to group the records.
        metrics : `list`
            Ordered list of numeric columns in `df` to summarize by `aggrules`.
        aggrules : `list`
            Ordered list of aggregation rules that determine the aggregation of the `metrics`.
        """

        # Build aggregation rules
        f = {
            key: val for (key, val) in zip(
                metrics,
                aggrules
            )
        }

        # Create a copy to aggregate
        summary_df = df.copy()

        # Aggregate
        if datetime:

            # Convert datetime dimension(s)
            for dt in self.datetime:
                summary_df[dt[0]] = (
                    pd.to_datetime(
                        summary_df[dt[0]],
                        format=dt[1]
                    )
                )

            if dimension:
                summary_df = summary_df.groupby(
                    dimension + datetime
                ).agg(f).reset_index(drop=False)
                summary_df = summary_df.sort_values(
                    by=dimension + datetime
                ).reset_index(drop=True)
            else:
                summary_df = summary_df.groupby(
                    datetime
                ).agg(f).reset_index(drop=False)
                summary_df = summary_df.sort_values(
                    by=datetime
                ).reset_index(drop=True)
        else:
            if dimension:
                summary_df = summary_df.groupby(
                    dimension
                ).agg(f).reset_index(drop=False)
                summary_df = summary_df.sort_values(
                    by=dimension
                ).reset_index(drop=True)
            else:
                summary_df['temp'] = 'X'
                summary_df = summary_df.groupby(
                    'temp'
                ).agg(f).reset_index(drop=False)
                summary_df = summary_df.drop(columns=['temp'])

        return summary_df

    def describe_df(
        self,
        df: pd.DataFrame,
        dimension: list = None,
        metrics: list = None,
        aggrules: list = None
    ) -> pd.DataFrame:
        """ Calculates descriptive statistics and returns a `pd.DataFrame'.

        Parameters
        ----------
        df : `pd.DataFrame`
            Pandas dataframe object to describe.
        dimension : `list`
            Ordered list of categorical columns in `df` to group the records.
        metrics : `list`
            Ordered list of numeric columns in `df` to summarize by `aggrules`.
        aggrules : `list`
            Ordered list of aggregation rules that determine the aggregation of the `metrics`.
        """

        # Create a copy to describe
        descriptives_df = df.copy()

        # Describe
        if dimension:

            # Create summary
            summary_df = self.agg_df(
                df=df,
                datetime=None,
                dimension=dimension,
                metrics=metrics,
                aggrules=aggrules
            )

            # Create descriptives
            descriptives_df = descriptives_df[
                dimension + metrics
            ]
            descriptives_df = descriptives_df.groupby(
                dimension
            ).describe().reset_index(drop=False)
            descriptives_df.columns = descriptives_df.columns.get_level_values(
                1
            )
            descriptives_df = descriptives_df.rename(
                columns={descriptives_df.columns[0]: dimension[0]}
            )

            # Join descriptives to summary
            descriptives_df = summary_df.merge(
                descriptives_df,
                how='left',
                left_on=dimension,
                right_on=dimension,
                validate='1:1',
                sort=True
            )
            descriptives_df = descriptives_df.rename(
                columns={
                    key: val for (key, val) in zip(
                        metrics,
                        aggrules
                    )
                }
            )

            # Retain only the last duplicate metric
            descriptives_df = descriptives_df.loc[
                :, ~descriptives_df.columns[::-1].duplicated()[::-1]
            ]

        else:

            # Create summary
            summary_df = self.agg_df(
                df=df,
                datetime=None,
                dimension=None,
                metrics=metrics,
                aggrules=aggrules
            )

            # Create descriptives
            descriptives_df = descriptives_df[
                metrics
            ]
            descriptives_df['XtempX'] = 'X'
            descriptives_df = descriptives_df.groupby(
                'XtempX'
            ).describe().reset_index(drop=False)
            descriptives_df.columns = descriptives_df.columns.get_level_values(
                1
            )
            descriptives_df = descriptives_df.rename(
                columns={descriptives_df.columns[0]: 'XtempX'}
            )
            descriptives_df = descriptives_df.drop(columns=['XtempX'])

            # Join descriptives to summary
            descriptives_df = summary_df.merge(
                descriptives_df,
                how='left',
                left_index=True,
                right_index=True,
                validate='1:1',
                sort=True
            )
            descriptives_df = descriptives_df.rename(
                columns={
                    key: val for (key, val) in zip(
                        metrics,
                        aggrules
                    )
                }
            )

            # Retain only the last duplicate metric
            descriptives_df = descriptives_df.loc[
                :, ~descriptives_df.columns[::-1].duplicated()[::-1]
            ]

        return descriptives_df


def parse_datetime_dimension(
    df: pd.DataFrame,
    regex_patterns: dict = {
        "%d/%m/%Y": '|'.join([
            r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d\d\d\d$',
            r'^([1-9]|[12][0-9]|3[01])/([1-9]|1[0-2])/\d\d\d\d$'
        ]),
        "%m/%d/%Y": '|'.join([
            r'^(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/\d\d\d\d$',
            r'^([1-9]|1[0-2])/([1-9]|[12][0-9]|3[01])/\d\d\d\d$'
        ]),
        "%Y-%m-%d": '|'.join([
            r'^\d\d\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'
            r'^\d\d\d\d-([1-9]|1[0-2])-([1-9]|[12][0-9]|3[01])$'
        ]),
        "%Y/%m/%d": '|'.join([
            r'^\d\d\d\d/(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])$'
            r'^\d\d\d\d/([1-9]|1[0-2])/([1-9]|[12][0-9]|3[01])$'
        ]),
        "%d %b %Y": '|'.join([
            ' '.join([
                r'^(0[1-9]|[12][0-9]|3[01])',
                r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
                r'\d\d\d\d$',
            ]),
            ' '.join([
                r'^([1-9]|[12][0-9]|3[01])',
                r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
                r'\d\d\d\d$'
            ])
        ]),
        "%d%b%Y": '|'.join([
            ''.join([
                r'^(0[1-9]|[12][0-9]|3[01])',
                r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
                r'\d\d\d\d$'
            ]),
            ''.join([
                r'^([1-9]|[12][0-9]|3[01])',
                r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
                r'\d\d\d\d$'
            ])
        ]),
        "%b %d, %Y": '|'.join([
            ' '.join([
                r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
                r'(0[1-9]|[12][0-9]|3[01]),',
                r'\d\d\d\d$'
            ]),
            ' '.join([
                r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
                r'([1-9]|[12][0-9]|3[01]),',
                r'\d\d\d\d$'
            ])
        ])
    }
) -> list:
    """ Parses `df` and returns a list of date-time columns and formats as a `list`.

    Parameters
    ----------
    df : `pd.DataFrame`
        Pandas dataframe object to describe.
    regex_patters : 'dict'
        Dictionary object of regex-patterns for date-time formats with the format string
            as the keys and the regex-patterns as the values.
    """

    date_dimensions = []

    # Retain column and datatype
    for col in df.columns:
        for pattern in regex_patterns.values():
            if all(df[col].astype(str).str.match(pattern, na=False)):
                date_dimensions.append(
                    (
                        col,
                        list(
                            regex_patterns.keys()
                        )[
                            list(
                                regex_patterns.values()
                            ).index(pattern)]
                    )
                )
                break

    return date_dimensions
