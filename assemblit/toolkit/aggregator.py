""" `pandas` based data aggregator """

import typing
import pandas

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


def agg_df(
    df: pandas.DataFrame,
    datetime: list | None = None,
    dimension: list | None = None,
    metrics: list | None = None,
    aggrules: list[typing.Literal[
        'Count', 'Sum', 'Min', 'Max', 'Mean', 'Median', 'Mode', 'Standard Deviation', 'Variance'
    ]] | None = None
) -> pandas.DataFrame:
    """ Groups `df` by `dimensions` and/or `datetime` and aggregates `metrics` with `aggrules`
    returning a `pandas.Dataframe`.

    Parameters
    ----------
    df : `pandas.DataFrame`
        Pandas dataframe object to aggregate.
    datetime : `list | None`
        Ordered list of the date-time columns in `df`.
    dimension : `list | None`
        Ordered list of categorical columns in `df` to group the records.
    metrics : `list | None`
        Ordered list of numeric columns in `df` to summarize by `aggrules`.
    aggrules : `list | None`
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
                pandas.to_datetime(
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
    df: pandas.DataFrame,
    dimension: list | None = None,
    metrics: list | None = None,
    aggrules: list[typing.Literal[
        'Count', 'Sum', 'Min', 'Max', 'Mean', 'Median', 'Mode', 'Standard Deviation', 'Variance'
    ]] | None = None
) -> pandas.DataFrame:
    """ Groups `df` by `dimensions` and/or `datetime` and calculates descriptive statistics
    returning a `pandas.DataFrame`.

    Parameters
    ----------
    df : `pandas.DataFrame`
        Pandas dataframe object to describe.
    dimension : `list | None`
        Ordered list of categorical columns in `df` to group the records.
    metrics : `list | None`
        Ordered list of numeric columns in `df` to summarize by `aggrules`.
    aggrules : `list | None`
        Ordered list of aggregation rules that determine the aggregation of the `metrics`.
    """

    # Create a copy to describe
    descriptives_df: pandas.DataFrame = df.copy()

    # Describe
    if dimension:

        # Create summary
        summary_df: pandas.DataFrame = agg_df(
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
        summary_df = agg_df(
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


# Define exception classes
class InvalidAggregationRule(Exception):
    pass
