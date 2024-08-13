""" assemblit.org/api_reference/assemblit/setup

Environment variables.
"""

import inspect
import streamlit as st
import assemblit
from assemblit import setup
from assemblit._app import wiki, aaas
from assemblit.pages import code_documentation


# Initialize the pages code documentation-page content
Documentation = code_documentation.Content(
    package=assemblit,
    package_or_module=setup
)

# Serve content󠀭󠀭󠀭󠀭
Documentation.serve()

# Serve add'l documentation content
_, col1, _ = st.columns(setup.CONTENT_COLUMNS)
col1.markdown(
    """
    ## Table of contents
    `assemblit` currently supports the following app-types,
    <li>
        <span style="font-weight: bold;">Wiki</span>
    </li>
    <li>
        <span style="font-weight: bold;">(AaaS) Analytics-as-a-Service (AaaS)</span>
    </li>

    ## Wiki ― Python package documentation
    The following `./assemblit/config.yaml` web-application settings are available for the `wiki` type app.
    """,
    unsafe_allow_html=True
)
with col1.container(border=True):
    st.code(
        '%s' % (inspect.getdoc(wiki.env)),
        language='markdown'
    )
col1.markdown(
    """
    ## AaaS ― Analytics-as-a-service
    The following `./assemblit/config.yaml` web-application settings are available for the `aaas` type app.
    """,
    unsafe_allow_html=True
)
with col1.container(border=True):
    st.code(
        '%s' % (inspect.getdoc(aaas.env)),
        language='markdown'
    )
