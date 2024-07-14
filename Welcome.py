"""
Information
---------------------------------------------------------------------
Name        : Welcome.py
Location    : ~/

Description
---------------------------------------------------------------------
Home-page of `assemblit`.
"""

import streamlit as st
import assemblit.setup as setup
import assemblit.pages.home as home


# Initialize the home-page content
Welcome = home.Content(
    header='Welcome',
    tagline="""
        `assemblit` is helping data analysts and scientists rapidly scale notebooks
        into analytics-as-a-service (AaaS) web-applications.
    """,
    # content_url=setup.GITHUB_CONTENT_URL,
    # content_file_name='README.md',
    # content_info='For more information, visit the [assemblit](%s) GitHub page.' % (
    #     setup.GITHUB_REPOSITORY_URL
    # )
    content_url=None,
    content_file_name=None,
    content_info=None
)

# Serve content
Welcome.serve()

# Temporary static content
_, col2, _ = st.columns(setup.CONTENT_COLUMNS)

col2.write('')
col2.markdown(
    """
        🦄 `assemblit` is a Python package that provides a framework of [streamlit](https://streamlit.io/) based
        web-components for quickly assembling end-to-end analytics-as-a-service
        (AaaS) web-applications. `assemblit` comes with user-authentication, a lightweight
        sqlite3-database backend, and workflow orchestration via [prefect](https://www.prefect.io).

        `alpha-release` coming soon!
    """
)
col2.subheader('')
col2.info(
    'For more information, visit the [assemblit](%s) GitHub page.' % (
        setup.GITHUB_REPOSITORY_URL
    ),
    icon='ℹ️'
)
