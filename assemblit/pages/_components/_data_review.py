""" Contains the components for data-review """

import hashlib
import json
import pandas as pd
import streamlit as st
from assemblit import setup
from assemblit.toolkit import aggregator, plotter
from assemblit.pages._components import _core, _selector
from assemblit._database import _generic, sessions, data
from assemblit._database._structures import Filter, Value

# --TODO Remove scope_db_name and scope_query_index from all function(s).
#       Scope for data is not dynamic, it can only be the sessions-db.


# Define core-component uploader function(s)
def display_data_review(
    db_name: str,
    table_name: str,
    query_index: str,
    scope_db_name: str,
    scope_query_index: str
):
    """ Displays the data-review.

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
    _, col2 = st.columns(setup.CONTENT_COLUMNS)

    # Display schema validation and data-preview
    with col2:

        # Display the data-review summary report container
        st.subheader('Review')
        st.write(
            """
                Select an uploaded datafile and review the summary report.
                - Click ```Finalize``` to set the selected datafile as final.
                - Click ```Save``` to update the default drop-down selections for the selected datafile.
                - Click ```Delete``` to delete the selected datafile.
            """
        )

        # Display the datafile-selector
        with st.container(border=True):

            # Retreive data drop-down selection options
            options = _selector.select_selector_dropdown_options(
                db_name=db_name,
                table_name=table_name,
                query_index=query_index,
                scope_db_name=scope_db_name,
                scope_query_index=scope_query_index
            )

            # Set data drop-down default query index
            index = _selector.select_selector_default_value(
                db_name=db_name,
                table_name=table_name,
                query_index=query_index,
                scope_db_name=scope_db_name,
                scope_query_index=scope_query_index,
                options=options
            )
            # try:

            #     # Select the 'Final' version of the session datafile
            #     index = options.index(
            #         Data.select_table_column_value(
            #             table_name=table_name,
            #             col=st.session_state[setup.NAME][db_name][table_name]['selector']['parameter'],
            #             filtr={
            #                 'col': 'final',
            #                 'val': True
            #             },
            #             return_dtype='str'
            #         )
            #     )

            # except db.NullReturnValue:

            #     # Select the most recent version of the session datafile
            #     try:
            #         index = options.index(
            #             db.as_type(
            #                 [
            #                     i[0] for i in Data.cursor.execute(
            #                         """
            #                             SELECT %s FROM %s
            #                                 WHERE %s IN (%s)
            #                                     ORDER BY %s DESC
            #                                         LIMIT 1;
            #                         """ % (
            #                             st.session_state[
            #                                 setup.NAME
            #                             ][
            #                                 db_name
            #                             ][
            #                                 table_name
            #                             ][
            #                                 'selector'
            #                             ][
            #                                 'parameter'
            #                             ],
            #                             table_name,
            #                             query_index,
            #                             ', '.join(["'%s'" % (i) for i in Sessions.select_table_column_value(
            #                                 table_name=table_name,
            #                                 col=query_index,
            #                                 filtr={
            #                                     'col': setup.SESSIONS_DB_QUERY_INDEX,
            #                                     'val': st.session_state[
            #                                         setup.NAME
            #                                     ][
            #                                         setup.SESSIONS_DB_NAME
            #                                     ][
            #                                         setup.SESSIONS_DB_QUERY_INDEX
            #                                     ]
            #                                 },
            #                                 multi=True,
            #                                 return_dtype='str'
            #                             )]),
            #                             'version'
            #                         )
            #                     ).fetchall()
            #                 ][0],
            #                 return_dtype='str'
            #             )
            #         )

            #     except IndexError:

            #         # Set the default index
            #         index = 0

            # except ValueError:

            #     # Set the default index
            #     index = 0

            # Set default data-ingestion form attributes
            if not options:
                st.session_state[setup.NAME][db_name][table_name]['set-up'] = True
            else:
                st.session_state[setup.NAME][db_name][table_name]['set-up'] = False

            # Display the datafile-selector
            display_dataset_selector(
                db_name=db_name,
                table_name=table_name,
                query_index=query_index,
                scope_db_name=scope_db_name,
                scope_query_index=scope_query_index,
                options=options,
                index=index
            )

        # Display the data-review summary report
        if not st.session_state[setup.NAME][db_name][table_name]['set-up']:
            display_data_review_summary(
                db_name=db_name,
                table_name=table_name,
                query_index=query_index,
                scope_db_name=scope_db_name,
                scope_query_index=scope_query_index
            )
        else:
            st.info(
                'Upload a datafile to review the summary report.',
                icon='ℹ️'
            )


def display_dataset_selector(
    db_name: str,
    table_name: str,
    query_index: str,
    scope_db_name: str,
    scope_query_index: str,
    options: list,
    index: int
):
    """ Displays the database table drop-down options and default value as a selector.

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
    options: `list`
        The list containing the the drop-down options.
    index : `int`
        The index position of the value to be displayed as the default selection.
    """

    # Layout selector columns
    col1, col2, col3 = st.columns([.6, .2, .2])

    # Display the data-selector drop-down
    if not st.session_state[setup.NAME][db_name][table_name]['set-up']:
        with col1:
            _selector.display_selector(
                db_name=db_name,
                table_name=table_name,
                query_index=query_index,
                scope_db_name=scope_db_name,
                scope_query_index=scope_query_index,
                options=options,
                index=index,
                disabled=False
            )
        with col2:
            display_dataset_delete_button(
                db_name=db_name,
                table_name=table_name,
                query_index=query_index,
                disabled=False
            )
        with col3:
            display_dataset_finalize_button(
                db_name=db_name,
                table_name=table_name,
                query_index=query_index,
                disabled=False
            )
    else:
        with col1:
            _selector.display_selector(
                db_name=db_name,
                table_name=table_name,
                query_index=query_index,
                scope_db_name=scope_db_name,
                scope_query_index=scope_query_index,
                options=options,
                index=index,
                disabled=True
            )
        with col2:
            display_dataset_delete_button(
                db_name=db_name,
                table_name=table_name,
                query_index=query_index,
                disabled=True
            )
        with col3:
            display_dataset_finalize_button(
                db_name=db_name,
                table_name=table_name,
                query_index=query_index,
                disabled=True
            )


def display_dataset_finalize_button(
    db_name: str,
    table_name: str,
    query_index: str,
    disabled: bool
):
    """ Displays the button to finalize the selected dataset.

    Parameters
    ----------
    db_name : `str`
        Name of the database.
    table_name : `str`
        Name of the table within `db_name` to store the datafile metadata.
    query_index : `str`
        Name of the index within `db_name` & `table_name`. May only be one column.
    disabled : `int`
        `True` or `False`, whether the button is displayed disabled or not.
    """

    # Display the 'Finalize' button
    st.button(
        label='Finalize',
        key='Button:%s' % _selector.generate_selector_key(
            db_name=db_name,
            table_name=table_name,
            parameter='Finalize'
        ),
        type='primary',
        disabled=disabled,
        on_click=finalize_dataset,
        kwargs={
            'db_name': db_name,
            'table_name': table_name,
            'query_index': query_index,
            'dataset_id': st.session_state[setup.NAME][db_name][query_index]
        },
        use_container_width=True
    )


def display_dataset_review_button(
    db_name: str,
    table_name: str,
    query_index: str,
    disabled: bool
):
    """ Displays the button to save the settings of the selected dataset.

    Parameters
    ----------
    db_name : `str`
        Name of the database.
    table_name : `str`
        Name of the table within `db_name` to store the datafile metadata.
    query_index : `str`
        Name of the index within `db_name` & `table_name`. May only be one column.
    disabled : `int`
        `True` or `False`, whether the button is displayed disabled or not.
    """

    # Parse selector values
    selected_values = parse_selector_values(
        db_name=db_name,
        table_name=table_name
    )

    # Display the 'Review' button
    st.button(
        label='Review',
        key='Button:%s' % _selector.generate_selector_key(
            db_name=db_name,
            table_name=table_name,
            parameter='Review'
        ),
        type='primary',
        disabled=disabled,
        on_click=save_dataset,
        kwargs={
            'db_name': db_name,
            'table_name': table_name,
            'query_index': query_index,
            'selected_datetime': selected_values['Datetimes'],
            'selected_dimensions': selected_values['Dimensions'],
            'selected_metrics': selected_values['Metrics'],
            'selected_aggrules': selected_values['Aggrules'],
            'dataset_id': st.session_state[setup.NAME][db_name][query_index]
        },
        use_container_width=True
    )


def display_dataset_clear_button(
    db_name: str,
    table_name: str,
    query_index: str,
    disabled: bool
):
    """ Displays the button to clear the settings of the selected dataset.

    Parameters
    ----------
    db_name : `str`
        Name of the database.
    table_name : `str`
        Name of the table within `db_name` to store the datafile metadata.
    query_index : `str`
        Name of the index within `db_name` & `table_name`. May only be one column.
    disabled : `int`
        `True` or `False`, whether the button is displayed disabled or not.
    """

    # Display the 'Clear' button
    st.button(
        label='Clear',
        key='Button:%s' % _selector.generate_selector_key(
            db_name=db_name,
            table_name=table_name,
            parameter='Clear'
        ),
        type='secondary',
        disabled=disabled,
        on_click=save_dataset,
        kwargs={
            'db_name': db_name,
            'table_name': table_name,
            'query_index': query_index,
            'selected_datetime': [],
            'selected_dimensions': [],
            'selected_metrics': [],
            'selected_aggrules': [],
            'dataset_id': st.session_state[setup.NAME][db_name][query_index]
        },
        use_container_width=True
    )


def display_dataset_delete_button(
    db_name: str,
    table_name: str,
    query_index: str,
    disabled: bool
):
    """ Displays the button to delete the selected dataset.

    Parameters
    ----------
    db_name : `str`
        Name of the database.
    table_name : `str`
        Name of the table within `db_name` to store the datafile metadata.
    query_index : `str`
        Name of the index within `db_name` & `table_name`. May only be one column.
    disabled : `int`
        `True` or `False`, whether the button is displayed disabled or not.
    """

    # Display the 'Delete' button
    st.button(
        label='Delete',
        key='Button:%s' % _selector.generate_selector_key(
            db_name=db_name,
            table_name=table_name,
            parameter='Delete'
        ),
        type='secondary',
        disabled=disabled,
        on_click=delete_dataset,
        kwargs={
            'dataset_id': st.session_state[setup.NAME][db_name][query_index]
        },
        use_container_width=True,
    )


def display_data_review_summary(
    db_name: str,
    table_name: str,
    query_index: str,
    scope_db_name: str,
    scope_query_index: str
):
    """ Displays the data review content.

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

    # Retrieve data from the database
    (
        df,
        datetime,
        selected_datetime,
        dimensions,
        selected_dimensions,
        metrics,
        selected_metrics,
        selected_aggrules
    ) = retrieve_data_from_database(
        db_name=db_name,
        table_name=table_name,
        query_index=query_index,
        scope_db_name=scope_db_name,
        scope_query_index=scope_query_index
    )

    # Display the data-review summary report
    if not df.empty:

        # Format selector options
        datetime.sort()
        dimensions.sort()
        metrics.sort()

        # Display selectors
        with st.container(border=True):

            if datetime:

                # Layout columns when (a) datetime dimension(s) exist(s)
                col1, col2, col3, col4 = st.columns([.25, .25, .25, .25])

                with col1:
                    st.multiselect(
                        key='MultiSelect:%s' % _selector.generate_selector_key(
                            db_name=db_name,
                            table_name=table_name,
                            parameter='Datetimes'
                        ),
                        label='Timeseries name',
                        options=[date_object[0] for date_object in datetime],
                        default=selected_datetime,
                        max_selections=1,
                        placeholder="""
                            Select the datetime dimension
                        """
                    )
                with col2:
                    st.multiselect(
                        key='MultiSelect:%s' % _selector.generate_selector_key(
                            db_name=db_name,
                            table_name=table_name,
                            parameter='Dimensions'
                        ),
                        label='Dimension name',
                        options=dimensions,
                        default=selected_dimensions,
                        max_selections=1,
                        placeholder="""
                            Select a summary dimension
                        """
                    )
                with col3:
                    st.multiselect(
                        key='MultiSelect:%s' % _selector.generate_selector_key(
                            db_name=db_name,
                            table_name=table_name,
                            parameter='Metrics'
                        ),
                        label='Metric name',
                        options=metrics,
                        default=selected_metrics,
                        max_selections=1,
                        placeholder="""
                            Select a summary metric
                        """
                    )
                with col4:
                    st.multiselect(
                        key='MultiSelect:%s' % _selector.generate_selector_key(
                            db_name=db_name,
                            table_name=table_name,
                            parameter='Aggrules'
                        ),
                        label='Metric agg. rule',
                        options=aggregator.AGGRULES.keys(),
                        default=selected_aggrules,
                        max_selections=1,
                        placeholder="""
                            Select a metric aggregation rule
                        """
                    )

            else:

                # Layout columns when no datetime dimension exists
                col1, col2, col3 = st.columns([.333, .333, .333])

                with col1:
                    st.multiselect(
                        key='MultiSelect:%s' % _selector.generate_selector_key(
                            db_name=db_name,
                            table_name=table_name,
                            parameter='Dimensions'
                        ),
                        label='Dimension name',
                        options=dimensions,
                        default=selected_dimensions,
                        max_selections=1,
                        placeholder="""
                            Select a summary dimension
                        """
                    )
                with col2:
                    st.multiselect(
                        key='MultiSelect:%s' % _selector.generate_selector_key(
                            db_name=db_name,
                            table_name=table_name,
                            parameter='Metrics'
                        ),
                        label='Metric name',
                        options=metrics,
                        default=selected_metrics,
                        max_selections=1,
                        placeholder="""
                            Select a summary metric
                        """
                    )
                with col3:
                    st.multiselect(
                        key='MultiSelect:%s' % _selector.generate_selector_key(
                            db_name=db_name,
                            table_name=table_name,
                            parameter='Aggrules'
                        ),
                        label='Metric aggregation rule',
                        options=aggregator.AGGRULES.keys(),
                        default=selected_aggrules,
                        max_selections=1,
                        placeholder="""
                            Select a metric aggregation rule
                        """
                    )

            # Layout columns
            _, col2, col3 = st.columns([.6, .2, .2])

            # Display the 'Clear' button
            with col2:
                display_dataset_clear_button(
                    db_name=db_name,
                    table_name=table_name,
                    query_index=query_index,
                    disabled=False
                )

            # Display the 'Review' button
            with col3:
                display_dataset_review_button(
                    db_name=db_name,
                    table_name=table_name,
                    query_index=query_index,
                    disabled=False
                )

        # Display plots
        if (
            (selected_metrics) and (selected_aggrules)
        ):

            # Plot timeseries
            if selected_datetime:
                with st.container(border=True):

                    # Display subheader
                    st.write('#### Timeseries plot')
                    st.write(
                        """
                            Review the trends of the data over-time. Use the 📷 icon
                             in the upper-right corner of the plot to download a ```.png``` screenshot.
                        """
                    )

                    # Parse datetime object
                    selected_datetime_object = [
                        i for i in datetime if i[0] == selected_datetime[0]
                    ]

                    # Display plotly plot
                    st.plotly_chart(
                        figure_or_data=plotter.timeseries_line_plot(
                            df=df,
                            datetime=selected_datetime_object,
                            dimension=selected_dimensions,
                            metrics=selected_metrics,
                            aggrules=selected_aggrules
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

                # Display plotly table
                st.plotly_chart(
                    figure_or_data=plotter.descriptives_table(
                        df=df,
                        dimension=selected_dimensions,
                        metrics=selected_metrics,
                        aggrules=selected_aggrules
                    ),
                    theme='streamlit',
                    use_container_width=True
                )

        else:

            # Display information
            st.info(
                'Select a metric and aggregation rule to produce the data-review summary report.',
                icon='ℹ️'
            )
    else:

        # Display information
        st.info(
            'Upload a datafile to review the data-review summary report.',
            icon='ℹ️'
        )


def parse_selector_values(
    db_name: str,
    table_name: str,
) -> dict:
    """ Parses the selector values and returns the values as
    a dictionary.

    Parameters
    ----------
    db_name : 'str'
        Name of the database to store the selector values
    table_name : 'str'
        Name of the table within `db_name` to store the selector values.
    """

    # Initialize responses
    responses = {}

    # Parse the selector values into a dictionary
    for parameter in ['Datetimes', 'Dimensions', 'Metrics', 'Aggrules']:
        if 'MultiSelect:%s' % _selector.generate_selector_key(
            db_name=db_name,
            table_name=table_name,
            parameter=parameter
        ) in st.session_state:

            # Add selector value to responses
            responses[parameter] = st.session_state[
                'MultiSelect:%s' % _selector.generate_selector_key(
                    db_name=db_name,
                    table_name=table_name,
                    parameter=parameter
                )
            ]

            # Reset session state variables
            del st.session_state[
                'MultiSelect:%s' % _selector.generate_selector_key(
                    db_name=db_name,
                    table_name=table_name,
                    parameter=parameter
                )
            ]

        else:

            # Add default selector-value to responses
            responses[parameter] = None

    return responses


# Define function(s) for standard uploader database queries
def retrieve_data_from_database(
    db_name: str,
    table_name: str,
    query_index: str,
    scope_db_name: str,
    scope_query_index: str
) -> tuple[pd.DataFrame, list, list, list, list, list, list, list]:
    """ Retrieves a database table and its data-review settings and returns the dataset as a `pd.DataFrame`
    and its settings a series of lists.

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
    """

    # Initialize the connection to the sessions database
    Sessions = sessions.Connection()

    # Initialize connection to the data-ingestion database
    Data = data.Connection()

    # Retrieve the selected datafile
    if st.session_state[setup.NAME][db_name]['name']:

        # Create an id from the session name and file name
        string_to_hash = ''.join(
            [str(st.session_state[setup.NAME][scope_db_name][scope_query_index])]
            + [str(st.session_state[setup.NAME][db_name]['name'])]
        )

        # Generate id
        dataset_id = hashlib.md5(
            string_to_hash.lower().encode('utf-8')
        ).hexdigest()

        # Check if the id already exists
        try:
            ids = Sessions.select_table_column_value(
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

        if dataset_id in ids:

            # Import the datafile
            df = pd.read_sql(
                sql="""
                    SELECT * FROM '%s';
                """ % dataset_id,
                con=Data.connection()
            )

            # Set selector options
            datetime = Data.select_generic_query(
                query="""
                    SELECT datetime FROM %s
                        WHERE %s = '%s';
                """ % (
                    table_name,
                    query_index,
                    dataset_id
                ),
                return_dtype='list'
            )
            dimensions = Data.select_generic_query(
                query="""
                    SELECT dimensions FROM %s
                        WHERE %s = '%s';
                """ % (
                    table_name,
                    query_index,
                    dataset_id
                ),
                return_dtype='list'
            )
            metrics = Data.select_generic_query(
                query="""
                    SELECT metrics FROM %s
                        WHERE %s = '%s';
                """ % (
                    table_name,
                    query_index,
                    dataset_id
                ),
                return_dtype='list'
            )

            # Set selector defaults
            try:
                selected_datetime = Data.select_generic_query(
                    query="""
                        SELECT selected_datetime FROM %s
                            WHERE %s = '%s';
                    """ % (
                        table_name,
                        query_index,
                        dataset_id
                    ),
                    return_dtype='list'
                )
            except _generic.NullReturnValue:
                selected_datetime = []
            selected_dimensions = Data.select_generic_query(
                query="""
                    SELECT selected_dimensions FROM %s
                        WHERE %s = '%s';
                """ % (
                    table_name,
                    query_index,
                    dataset_id
                ),
                return_dtype='list'
            )
            selected_metrics = Data.select_generic_query(
                query="""
                    SELECT selected_metrics FROM %s
                        WHERE %s = '%s';
                """ % (
                    table_name,
                    query_index,
                    dataset_id
                ),
                return_dtype='list'
            )
            selected_aggrules = Data.select_generic_query(
                query="""
                    SELECT selected_aggrules FROM %s
                        WHERE %s = '%s';
                """ % (
                    table_name,
                    query_index,
                    dataset_id
                ),
                return_dtype='list'
            )

            # Check that the datafile hash matches
            if not hashlib.sha256(
                df.to_string().encode('utf8')
            ).hexdigest() == Data.select_generic_query(
                query="""
                    SELECT sha256 FROM %s
                        WHERE %s = '%s';
                """ % (
                    table_name,
                    query_index,
                    dataset_id
                ),
                return_dtype='str'
            ):
                st.warning("""
                        Modified content. The hash of the most recently uploaded datafile ```%s```
                            does not match the hash of the original data. There may be un-expected
                            changes to the data as a result.
                    """ % (
                        st.session_state[setup.NAME][db_name]['name']
                    ),
                    icon='⚠️'
                )

        else:

            # Set empty dataframe
            df = pd.DataFrame()

            # Log errors
            st.session_state[setup.NAME][db_name]['errors'] = (
                st.session_state[setup.NAME][db_name]['errors']
                + [''.join([
                    """
                        Missing datafile. The selected data file ```%s``` does not exist.
                            Please upload a new datafile.
                    """ % (
                        st.session_state[setup.NAME][db_name]['name']
                    )
                ])]
            )

    return df, datetime, selected_datetime, dimensions, selected_dimensions, metrics, selected_metrics, selected_aggrules


# Define function(s) for managing uploader database setting(s)
def finalize_dataset(
    db_name: str,
    table_name: str,
    query_index: str,
    dataset_id: str
):
    """ Finalizes the selected datafile within the data-ingestion database table.

    Parameters
    ----------
    db_name : `str`
        Name of the database.
    table_name : `str`
        Name of the table within `db_name` to store the finalization option.
    query_index : `str`
        Name of the index within `db_name` & `table_name`. May only be one column.
    dataset_id : `str`
        Dataset ID of the selected dataset
    """

    # Initialize connection to the sessions database
    Sessions = sessions.Connection()

    # Initialize connection to the data-ingestion database
    Data = data.Connection()

    # Reset all datasets
    Data.reset_table_column_value(
        table_name=table_name,
        value=Value(
            col='final',
            val=False
        ),
        filtr=Filter(
            col=query_index,
            val=Sessions.select_table_column_value(
                table_name=table_name,
                col=query_index,
                filtr=Filter(
                    col=setup.SESSIONS_DB_QUERY_INDEX,
                    val=st.session_state[setup.NAME][setup.SESSIONS_DB_NAME][setup.SESSIONS_DB_QUERY_INDEX]
                ),
                multi=True
            )
        )
    )

    # Set the selected datafile as final
    Data.update(
        table_name=table_name,
        value=Value(
            col='final',
            val=True
        ),
        filtr=Filter(
            col=query_index,
            val=dataset_id
        )
    )


def save_dataset(
    db_name: str,
    table_name: str,
    query_index: str,
    selected_datetime: list,
    selected_dimensions: list,
    selected_metrics: list,
    selected_aggrules: list,
    dataset_id: str
):
    """ Updates the drop-down selection defaults stored within the data-ingestion database table for the selected datafile.

    Parameters
    ----------
    db_name : `str`
        Name of the database.
    table_name : `str`
        Name of the table within `db_name` to store the finalization option.
    query_index : `str`
        Name of the index within `db_name` & `table_name`. May only be one column.
    selected_datetime : `list`
        Ordered list of the selected date-time columns in `df`.
    selected_dimension : `list`
        Ordered list of the selected categorical column in `df` to group the records.
    selected_metrics : `list`
        Ordered list of the selected numeric column in `df` to summarize by `aggrules`.
    selected_aggrules : `list`
        Ordered list of the selected aggregation rule that determines the aggregation of the `selected_metrics`.
    dataset_id : `str`
        Dataset ID of the selected dataset
    """

    # Initialize connection to the data-ingestion database
    Data = data.Connection()

    # Update the database with the latest selected values
    Data.update(
        table_name=table_name,
        value=Value(
            col='selected_datetime',
            val=json.dumps(selected_datetime)
        ),
        filtr=Filter(
            col=query_index,
            val=dataset_id
        )
    )
    Data.update(
        table_name=table_name,
        value=Value(
            col='selected_dimensions',
            val=json.dumps(selected_dimensions)
        ),
        filtr=Filter(
            col=query_index,
            val=dataset_id
        )
    )
    Data.update(
        table_name=table_name,
        value=Value(
            col='selected_metrics',
            val=json.dumps(selected_metrics)
        ),
        filtr=Filter(
            col=query_index,
            val=dataset_id
        )
    )
    Data.update(
        table_name=table_name,
        value=Value(
            col='selected_aggrules',
            val=json.dumps(selected_aggrules)
        ),
        filtr=Filter(
            col=query_index,
            val=dataset_id
        )
    )


def delete_dataset(
    dataset_id: str
):
    """ Deletes the database table information associated with the selected dataset.

    Parameters
    ----------
    dataset_id : `str`
        Dataset ID of the selected dataset
    """

    # Initialize connection to the sessions database
    Sessions = sessions.Connection()

    # Initialize connection to the data-ingestion database
    Data = data.Connection()

    # Build database table objects to remove datasets from the sessions database
    sessions_db_query_index_objects_to_delete = Sessions.build_database_table_objects_to_delete(
        table_names=Sessions.select_all_tables_with_column_name(
            col=setup.DATA_DB_QUERY_INDEX
        ),
        query_index=setup.DATA_DB_QUERY_INDEX,
        query_index_values=[dataset_id]
    )

    # Build database table objects to remove datasets from the data-ingestion database
    data_db_query_index_objects_to_delete = Data.build_database_table_objects_to_delete(
        table_names=Data.select_all_tables_with_column_name(
            col=setup.DATA_DB_QUERY_INDEX
        ),
        query_index=setup.DATA_DB_QUERY_INDEX,
        query_index_values=[dataset_id]
    )

    # Drop all data-ingestion database tables
    Data.drop_table(
        table_name=dataset_id
    )

    # Delete all data-ingestion database table values
    Data.delete(
        tables=data_db_query_index_objects_to_delete
    )

    # Delete all sessions database table values
    Sessions.delete(
        tables=sessions_db_query_index_objects_to_delete
    )

    # Reset session state
    _core.initialize_session_state_database_defaults(
        db_name=setup.DATA_DB_NAME,
        defaults=setup.DATA_DEFAULTS
    )
