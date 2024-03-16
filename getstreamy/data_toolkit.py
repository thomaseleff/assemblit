"""
Information
---------------------------------------------------------------------
Name        : data_toolkit.py
Location    : ~/
Author      : Tom Eleff
Published   : 2024-03-16
Revised on  : .

Description
---------------------------------------------------------------------
Contains the `Classes` for generic data parsing, aggregating and
plotting.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Define static variables
AGGRULES = {
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


class Parser():

    def datetime_dimension(
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


class Aggregator():

    def agg_df(
        df: pd.DataFrame,
        datetime: list | None = None,
        dimension: list | None = None,
        metrics: list | None = None,
        aggrules: list | None = None
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

        # Parse aggregation rules
        try:
            aggrules = [AGGRULES[r] for r in aggrules]
        except KeyError:
            raise InvalidAggregationRule(
                "Invalid agg. rule(s) {%s}. Acceptable agg. rules are [%s]." % (
                    aggrules[0],
                    ', '.join(list(AGGRULES.keys()))
                )
            )

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
            for date_object in datetime:
                summary_df[date_object[0]] = (
                    pd.to_datetime(
                        summary_df[date_object[0]],
                        format=date_object[1]
                    )
                )

            if dimension:
                summary_df = summary_df.groupby(
                    dimension + [datetime[0][0]]
                ).agg(f).reset_index(drop=False)
                summary_df = summary_df.sort_values(
                    by=dimension + [datetime[0][0]]
                ).reset_index(drop=True)
            else:
                summary_df = summary_df.groupby(
                    [datetime[0][0]]
                ).agg(f).reset_index(drop=False)
                summary_df = summary_df.sort_values(
                    by=[datetime[0][0]]
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
        df: pd.DataFrame,
        dimension: list | None = None,
        metrics: list | None = None,
        aggrules: list | None = None
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
            summary_df = Aggregator.agg_df(
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
            summary_df = Aggregator.agg_df(
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


class Plotter():

    def timeseries_line_plot(
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
            return px.line(
                data_frame=Aggregator.agg_df(
                    df=df,
                    datetime=datetime,
                    dimension=dimension,
                    metrics=metrics,
                    aggrules=aggrules
                ),
                x=datetime[0][0],
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
            return px.line(
                data_frame=Aggregator.agg_df(
                    df=df,
                    datetime=datetime,
                    dimension=None,
                    metrics=metrics,
                    aggrules=aggrules
                ),
                x=datetime[0][0],
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

    def descriptives_table(
        df: pd.DataFrame,
        dimension: list = None,
        metrics: list = None,
        aggrules: list = None
    ) -> go.Line:
        """ Creates a descriptive summary table-figure and returns a Plotly `go.Table` object.

        Parameters
        ----------
        df : `pd.DataFrame`
            Pandas dataframe object to plot.
        dimension : `list`
            Ordered list of categorical columns in `df` to group the records.
        metrics : `list`
            Ordered list of numeric columns in `df` to summarize by `aggrules`.
        aggrules : `list`
            Ordered list of aggregation rules that determine the aggregation of the `metrics`.
        """

        if dimension:
            descriptives_df = Aggregator.describe_df(
                df=df,
                dimension=dimension,
                metrics=metrics,
                aggrules=aggrules
            )
        else:
            descriptives_df = Aggregator.describe_df(
                df=df,
                dimension=None,
                metrics=metrics,
                aggrules=aggrules
            )

        # Apply formatting
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

        return go.Figure(
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
        )


# Define exception classes
class InvalidAggregationRule(Exception):
    pass
