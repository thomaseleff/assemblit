""" Tests the `assemblit.toolkit` subpackage """

import os
import pytest
import textwrap
import pandas as pd
import plotly.graph_objects
from assemblit import toolkit
from assemblit.toolkit._exceptions import InvalidAggregationRule


PATH = os.path.join(
    os.path.dirname(__file__),
    'resources'
)


@pytest.fixture
def DF() -> pd.DataFrame:
    return pd.read_csv(
        os.path.join(PATH, 'weekly.csv'),
        sep=','
    )


def test_aggregator_agg_df_w_dimension_success(DF: pd.DataFrame):
    total = toolkit.aggregator.agg_df(
        df=DF,
        datetime=None,
        dimension=['product'],
        metrics=['y'],
        aggrules=['Sum']
    ).at[0, 'y']
    assert round(total, 3) == 9263.803


def test_aggregator_agg_df_wo_dimension_success(DF: pd.DataFrame):
    total = toolkit.aggregator.agg_df(
        df=DF,
        datetime=None,
        dimension=None,
        metrics=['y'],
        aggrules=['Sum']
    ).at[0, 'y']
    assert round(total, 3) == 9263.803


def test_aggregator_agg_df_invalidaggregationrule(DF: pd.DataFrame):
    with pytest.raises(InvalidAggregationRule):
        toolkit.aggregator.agg_df(
            df=DF,
            datetime=None,
            dimension=None,
            metrics=['y'],
            aggrules=['Not-an-aggregation-rule']
        )


def test_aggregator_describe_df_w_dimension_success(DF: pd.DataFrame):
    average = toolkit.aggregator.describe_df(
        df=DF,
        dimension=['product'],
        metrics=['y'],
        aggrules=['Mean']
    ).at[0, 'mean']
    assert round(average, 3) == 44.538


def test_aggregator_describe_df_wo_dimension_success(DF: pd.DataFrame):
    average = toolkit.aggregator.describe_df(
        df=DF,
        dimension=None,
        metrics=['y'],
        aggrules=['Mean']
    ).at[0, 'mean']
    assert round(average, 3) == 44.538


def test_aggregator_describe_df_invalidaggregationrule(DF: pd.DataFrame):
    with pytest.raises(InvalidAggregationRule):
        toolkit.aggregator.describe_df(
            df=DF,
            dimension=None,
            metrics=['y'],
            aggrules=['Not-an-aggregation-rule']
        )


def test_plotter_timeseries_line_plot_w_dimension_success(DF: pd.DataFrame):
    plot = toolkit.plotter.timeseries_line_plot(
        df=DF,
        datetime=[('week', '%Y-%m-%d')],
        dimension=['product'],
        metrics=['y'],
        aggrules=['Sum']
    )
    assert isinstance(plot, plotly.graph_objects.Figure)


def test_plotter_timeseries_line_plot_wo_dimension_success(DF: pd.DataFrame):
    plot = toolkit.plotter.timeseries_line_plot(
        df=DF,
        datetime=[('week', '%Y-%m-%d')],
        dimension=None,
        metrics=['y'],
        aggrules=['Sum']
    )
    assert isinstance(plot, plotly.graph_objects.Figure)


def test_plotter_descriptives_table_w_dimension_success(DF: pd.DataFrame):
    table = toolkit.plotter.descriptives_table(
        df=DF,
        dimension=['product'],
        metrics=['y'],
        aggrules=['Sum']
    )
    assert isinstance(table, plotly.graph_objects.Figure)


def test_plotter_descriptives_table_wo_dimension_success(DF: pd.DataFrame):
    table = toolkit.plotter.descriptives_table(
        df=DF,
        dimension=None,
        metrics=['y'],
        aggrules=['Sum']
    )
    assert isinstance(table, plotly.graph_objects.Figure)


def test_content_from_markdown_success():
    assert toolkit.content.from_markdown(
        file_path=os.path.join(PATH, 'README.md')
    ) == textwrap.dedent('# Tests\nMarkdown content read as a part of unit-tests.')


def test_content_from_markdown_filenotfounderror():
    with pytest.raises(FileNotFoundError):
        toolkit.content.from_markdown(
            file_path=os.path.join(PATH, 'file-not-found-error.md')
        )


def test_content_to_markdown_success():

    # Remove existing file if present
    if os.path.isfile(os.path.join(PATH, 'TEST.md')):
        os.system('rm %s' % (os.path.join(PATH, 'TEST.md')))

    toolkit.content.to_markdown(
        file_path=os.path.join(PATH, 'TEST.md'),
        content='# Tests\nMarkdown content generated as a part of unit-tests.'
    )
    assert os.path.isfile(os.path.join(PATH, 'TEST.md'))
    assert toolkit.content.from_markdown(
        file_path=os.path.join(PATH, 'TEST.md')
    ) == textwrap.dedent('# Tests\nMarkdown content generated as a part of unit-tests.')


def test_clean_text_success():
    text = """
        Assemblit is helping data analysts and scientists rapidly scale notebooks into
        analytics-as-a-service (AaaS) web-applications.
    """
    assert toolkit.content.clean_text(text=text) == 'Assemblit is helping data analysts and scientists rapidly scale notebooks into analytics-as-a-service (AaaS) web-applications.'
