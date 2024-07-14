"""
Information
---------------------------------------------------------------------
Name        : _data_uploader.py
Location    : ~/pages/_components

Description
---------------------------------------------------------------------
Contains the components for a data-uploader.
"""

import os
import hashlib
import json
import datetime as dt
import pandas as pd
import pandera as pa
from pandera.engines import pandas_engine
import streamlit as st
from assemblit import data_toolkit, setup
from assemblit.database import sessions, data, generic
from assemblit.database.structures import Filter, Validate, Row

# --TODO Remove scope_db_name and scope_query_index from all function(s).
#       Scope for data is not dynamic, it can only be the sessions-db.


# Define core-component uploader function(s)
def display_data_contract(
    data_dictionary: pd.DataFrame,
    data_example: pd.DataFrame
):
    """ Displays the data dictionary as a table and the data example download button with an expander container.

    Parameters
    ----------
    data_dictionary : `pd.DataFrame`
        An optional data dictionary that describes the structure and format of the
            expected datafile.
    data_example : `pd.DataFrame`
        An optional dataframe that provides a reference for a valid datafile.
    """

    # Layout columns
    _, col2, _ = st.columns(setup.CONTENT_COLUMNS)

    # Display the data-contract expander
    with col2:
        if (
            (not data_dictionary.empty) or (not data_example.empty)
        ):

            # Display the header
            st.subheader('Data contract')
            st.write('The `data contract` defines the structure and format of the data.')

            # Display the expander
            with st.expander(
                label='📝 Expand for details on the `data contract`.',
                expanded=False
            ):

                # Display the data dictionary
                if not data_dictionary.empty:
                    st.write('#### Dictionary')
                    st.write('The data dictionary describes the `data contract` of the data.')
                    st.dataframe(
                        data=data_dictionary,
                        hide_index=True,
                        use_container_width=True
                    )

                # Display the data example
                if not data_example.empty:
                    st.write('#### Example')
                    st.write('Click `Download` to download a reference datafile in the `data contract`.')
                    st.download_button(
                        label='Download',
                        data=data_example.to_csv(
                            sep=',',
                            index=False
                        ).encode('utf8'),
                        file_name='data_example.csv',
                        mime='text/csv',
                        type='primary'
                    )


def display_data_uploader(
    db_name: str,
    table_name: str
):
    """ Displays the data-uploader as a form

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the datafile
    table_name : 'str'
        Name of the table within `db_name` to store the datafile metadata.
    """

    # Layout columns
    _, col2, col3 = st.columns(setup.CONTENT_COLUMNS)

    # Display the data uploader
    with col2:
        st.subheader('Upload')
        st.write(
            'Upload a datafile in `.csv` or `.parquet` format. Click `Upload` to save the datafile.'
        )

        with st.form(
            key=generate_form_key(
                db_name=db_name,
                table_name=table_name
            ),
            border=True,
            clear_on_submit=True
        ):

            # Display the data-ingestion file uploader
            st.file_uploader(
                label=('Upload a datafile in `.csv` or `.parquet` format.'),
                key='FormSubmitter:%s' % (
                    generate_form_key(
                        db_name=db_name,
                        table_name=table_name
                    )
                ),
                type=['csv', 'parquet'],
                label_visibility='collapsed'
            )

            # Layout form columns
            col1, col2, col3 = st.columns([.6, .2, .2])

            # Display the 'Clear' button
            col2.write('')
            col2.form_submit_button(
                label='Clear',
                type='secondary',
                use_container_width=True
            )

            # Display the 'Upload' button
            col3.write('')
            col3.form_submit_button(
                label='Upload',
                type='primary',
                use_container_width=True
            )


def display_data_preview(
    db_name: str,
    table_name: str,
    query_index: str,
    scope_db_name: str,
    scope_query_index: str
):
    """ Displays the data-preview

    Parameters
    ----------
    db_name : `str`
        Name of the database.
    table_name : `str`
        Name of the table within `db_name` to store the datafile metadata.
    query_index : `str`
        Name of the index within `db_name` & `table_name`. May only be one column.
    scope_db_name : `str`
        Name of the database that contains the associated scope for the selector
    scope_query_index : `str`
        Name of the index within `scope_db_name` & `table_name`. May only be one column.
    """

    # Layout columns
    _, col2, _ = st.columns(setup.CONTENT_COLUMNS)

    # Display the schema validation result and the data-preview table
    with col2:

        # Display schema validation and data-preview
        if st.session_state['FormSubmitter:%s-%s' % (
                generate_form_key(
                    db_name=db_name,
                    table_name=table_name
                ),
                'Upload'
        )] and st.session_state['FormSubmitter:%s' % (
                generate_form_key(
                    db_name=db_name,
                    table_name=table_name
                )
        )] is not None:

            # Check the datafile format
            dbms = str(
                os.path.splitext(
                    st.session_state['FormSubmitter:%s' % (
                        generate_form_key(
                            db_name=db_name,
                            table_name=table_name
                        )
                    )].name
                )[1]
            ).strip().upper()

            # Read the datafile
            if dbms in ['.CSV', '.PARQUET']:
                if dbms == '.CSV':

                    # Read '.csv'
                    df = pd.read_csv(
                        st.session_state['FormSubmitter:%s' % (
                            generate_form_key(
                                db_name=db_name,
                                table_name=table_name
                            )
                        )],
                        sep=','
                    )

                if dbms == '.PARQUET':

                    # Read '.parquet'
                    df = pd.read_parquet(
                        st.session_state['FormSubmitter:%s' % (
                            generate_form_key(
                                db_name=db_name,
                                table_name=table_name
                            )
                        )],
                        engine='pyarrow'
                    )

                # Normalize column names
                df.columns = [c.lower() for c in df.columns]

                # Identify and format the datetime dimension
                datetime = data_toolkit.Parser.datetime_dimension(df=df)

                # Identify categorical dimensions
                #   If the datatype is a(n),
                #       <b> boolean
                #       <O> object
                #       <S> (byte-)string
                #       <U> unicode
                #
                #   > Then the column is a dimension
                dimensions = [
                    dim for dim in set(df.columns) if (
                        (df[dim].dtype.kind in 'bOSU')
                        and (dim not in [date_object[0] for date_object in datetime])
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
                metrics = [
                    dim for dim in set(df.columns) if (
                        (df[dim].dtype.kind in 'iufc')
                    )
                ]

                # Compile schema validation rules
                rules = {}

                # Add datetime rules
                for date_object in datetime:
                    rules[date_object[0]] = pa.Column(
                        pandas_engine.DateTime(
                            to_datetime_kwargs={
                                "format": date_object[1]
                            }
                        )
                    )

                # Add dimension rules
                for col in dimensions:
                    rules[col] = pa.Column(
                        str,
                        nullable=False
                    )

                # Add metric rules
                for col in metrics:
                    rules[col] = pa.Column(
                        float,
                        nullable=True
                    )

                # Create unique dimensions
                if datetime:
                    unique_dimensions = (
                        [d[0] for d in datetime] + dimensions
                    )
                else:
                    unique_dimensions = dimensions

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
                            `data contract`.
                    """
                )

                # Apply schema
                try:
                    df = schema.validate(df, lazy=True)

                    # Apply datetime formatting
                    for date_object in datetime:
                        df[date_object[0]] = df[date_object[0]].dt.strftime(date_object[1])

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
                    promote_data_to_database(
                        db_name=db_name,
                        table_name=table_name,
                        query_index=query_index,
                        scope_db_name=scope_db_name,
                        scope_query_index=scope_query_index,
                        datetime=datetime,
                        selected_datetime=[],
                        dimensions=dimensions,
                        selected_dimensions=[],
                        metrics=metrics,
                        selected_metrics=[],
                        selected_aggrules=[],
                        df=df.copy(),
                        dbms=dbms,
                        file_name=st.session_state['FormSubmitter:%s' % (
                            generate_form_key(
                                db_name=db_name,
                                table_name=table_name
                            )
                        )].name,
                        file_size=st.session_state['FormSubmitter:%s' % (
                            generate_form_key(
                                db_name=db_name,
                                table_name=table_name
                            )
                        )].size
                    )

                # Raise schema errors
                except pa.errors.SchemaErrors as e:
                    st.error(
                        body="""
                            Schema validation failed. The dataframe structure does not
                             comply with the `data contract` requirements. See the dataframe
                             output below for more information. Please re-upload the datafile.
                        """,
                        icon='⛔'
                    )
                    col1, col2 = st.columns([0.25, 6.75])
                    col2.dataframe(
                        e.failure_cases,
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
                st.session_state[setup.NAME][db_name]['errors'] = (
                    st.session_state[setup.NAME][db_name]['errors']
                    + [''.join([
                        'Invalid file format. The data uploader expects either a comma-separated',
                        ' `.csv` or a `.parquet` file. Please re-upload the datafile in a',
                        ' supported format.'
                    ])]
                )

            # Reset the data-uploader variables
            del st.session_state['FormSubmitter:%s' % (
                generate_form_key(
                    db_name=db_name,
                    table_name=table_name
                )
            )]
            del st.session_state['FormSubmitter:%s-%s' % (
                generate_form_key(
                    db_name=db_name,
                    table_name=table_name
                ),
                'Upload'
            )]


# Define function(s) for creating uploaders
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


# Define function(s) for standard uploader database queries
def promote_data_to_database(
    db_name: str,
    table_name: str,
    query_index: str,
    scope_db_name: str,
    scope_query_index: str,
    datetime: list,
    selected_datetime: list,
    dimensions: list,
    selected_dimensions: list,
    metrics: list,
    selected_metrics: list,
    selected_aggrules: list,
    df: pd.DataFrame,
    dbms: str,
    file_name: str,
    file_size: float
):
    """ Promotes an uploaded datafile to the database.

    Parameters
    ----------
    db_name : `str`
        Name of the database.
    table_name : `str`
        Name of the table within `db_name` to store the finalization option.
    query_index : `str`
        Name of the index within `db_name` & `table_name`. May only be one column.
    scope_db_name : `str`
        Name of the database that contains the associated scope for the selector
    scope_query_index : `str`
        Name of the index within `scope_db_name` & `table_name`. May only be one column.
    datetime : `list`
        Ordered list of the date-time columns in `df`.
    selected_datetime : `list`
        Ordered list of the selected date-time columns in `df`.
    dimension : `list`
        Ordered list of categorical columns in `df` to group the records.
    selected_dimension : `list`
        Ordered list of the selected categorical column in `df` to group the records.
    metrics : `list`
        Ordered list of numeric columns in `df` to summarize by `aggrules`.
    selected_metrics : `list`
        Ordered list of the selected numeric column in `df` to summarize by `aggrules`.
    aggrules : `list`
        Ordered list of aggregation rules that determine the aggregation of the `metrics`.
    selected_aggrules : `list`
        Ordered list of the selected aggregation rule that determines the aggregation of the `selected_metrics`.
    df : `pd.DataFrame`
        Pandas dataframe object to promote to the database.
    dbms : `str`
        Data management system name of the data to promote ('csv', 'parquet').
    file_name : `str`
        Name of the datafile.
    file_size : `str`
        Size of the datafile.
    """

    # Initialize the connection to the scope database
    Sessions = sessions.Connection()

    # Initialize connection to the data-ingestion database
    Data = data.Connection()

    # Retrieve the latest data version number
    try:
        version = int(
            Data.select_generic_query(
                query="""
                    SELECT MAX(version) FROM %s
                        WHERE %s in (%s);
                """ % (
                    table_name,
                    query_index,
                    ', '.join(["'%s'" % (i) for i in Sessions.select_table_column_value(
                        table_name=table_name,
                        col=query_index,
                        filtr=Filter(
                            col=scope_query_index,
                            val=st.session_state[setup.NAME][scope_db_name][scope_query_index]
                        ),
                        multi=True
                    )])
                ),
                return_dtype='int'
            ) + 1
        )

    except (TypeError, generic.NullReturnValue):
        version = 1

    # Create an id from the session name and file name
    string_to_hash = ''.join(
        [str(st.session_state[setup.NAME][scope_db_name][scope_query_index])]
        + [str(file_name)]
    )

    # Generate id
    id = hashlib.md5(
        string_to_hash.lower().encode('utf-8')
    ).hexdigest()

    # Check if the file name already exists
    if not Data.table_exists(table_name=id):

        # Update the scope database
        Sessions.insert(
            table_name=table_name,
            row=Row(
                cols=sessions.Schemas.data.cols(),
                vals=[
                    st.session_state[setup.NAME][scope_db_name][scope_query_index],
                    id
                ]
            )
        )

        # Update the data ingestion database
        Data.insert(
            table_name=table_name,
            row=Row(
                cols=data.Schemas.data.cols(),
                vals=[
                    id,
                    st.session_state[setup.NAME][setup.USERS_DB_NAME]['name'],
                    dt.datetime.now(),
                    False,
                    version,
                    file_name,
                    dbms,
                    json.dumps(datetime),
                    json.dumps(dimensions),
                    json.dumps(metrics),
                    json.dumps(selected_datetime),
                    json.dumps(selected_dimensions),
                    json.dumps(selected_metrics),
                    json.dumps(selected_aggrules),
                    round(file_size / 1024, 6),
                    hashlib.sha256(df.to_string().encode('utf8')).hexdigest()
                ]
            ),
            validate=Validate(
                col=query_index,
                val=id
            )
        )

        # Promote the datafile to the data-ingestion database as a table
        df.to_sql(
            name=id,
            con=Data.connection(),
            index=False
        )

        # Set the session state
        st.session_state[setup.NAME][db_name]['name'] = file_name
        st.session_state[setup.NAME][db_name][query_index] = id

        # Log successes
        st.success(
            body="""
                The file `%s` was uploaded successfully.
            """ % (file_name),
            icon='✅'
        )

    else:

        # ADD CONDITION TO "UPDATE" A PREVIOUSLY UPLOADED FILE

        # Log successes
        st.success(
            body="""
                The file `%s` was uploaded successfully.
            """ % (file_name),
            icon='✅'
        )
