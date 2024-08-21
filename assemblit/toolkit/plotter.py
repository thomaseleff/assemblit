""" `plotly` based plotting """

from typing import Literal, List
import pandas
import plotly.express
import plotly.graph_objects
from assemblit.toolkit import aggregator


def timeseries_line_plot(
    df: pandas.DataFrame,
    datetime: list | None = None,
    dimension: list | None = None,
    metrics: list | None = None,
    aggrules: List[Literal[
        'Count', 'Sum', 'Min', 'Max', 'Mean', 'Median', 'Mode', 'Standard Deviation', 'Variance'
    ]] | None = None
) -> plotly.graph_objects.Figure:
    """ Aggregates `df` with `aggregator.agg_df` and returns a Plotly `plotly.graph_objects.Line` object.

    Parameters
    ----------
    df : `pandas.DataFrame`
        Pandas dataframe object to plot.
    datetime : `list | None`
        Ordered list of the date-time columns in `df`.
    dimension : `list | None`
        Ordered list of categorical columns in `df` to group the records.
    metrics : `list | None`
        Ordered list of numeric columns in `df` to summarize by `aggrules`.
    aggrules : `list | None`
        Ordered list of aggregation rules that determine the aggregation of the `metrics`.
    """

    if dimension:
        return plotly.express.line(
            data_frame=aggregator.agg_df(
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
        return plotly.express.line(
            data_frame=aggregator.agg_df(
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
    df: pandas.DataFrame,
    dimension: list | None = None,
    metrics: list | None = None,
    aggrules: List[Literal[
        'Count', 'Sum', 'Min', 'Max', 'Mean', 'Median', 'Mode', 'Standard Deviation', 'Variance'
    ]] | None = None
) -> plotly.graph_objects.Figure:
    """ Aggregates `df` with `aggregator.describe_df` then returns a Plotly `plotly.graph_objects.Table` object.

    Parameters
    ----------
    df : `pandas.DataFrame`
        Pandas dataframe object to plot.
    dimension : `list | None`
        Ordered list of categorical columns in `df` to group the records.
    metrics : `list | None`
        Ordered list of numeric columns in `df` to summarize by `aggrules`.
    aggrules : `list | None`
        Ordered list of aggregation rules that determine the aggregation of the `metrics`.
    """

    if dimension:
        descriptives_df: pandas.DataFrame = aggregator.describe_df(
            df=df,
            dimension=dimension,
            metrics=metrics,
            aggrules=aggrules
        )
    else:
        descriptives_df: pandas.DataFrame = aggregator.describe_df(
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

    return plotly.graph_objects.Figure(
        data=[
            plotly.graph_objects.Table(
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
