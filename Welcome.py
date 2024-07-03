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
    header="Welcome to '%s'" % (setup.NAME),
    tagline='Shortening the roadmap to your first analytics customer.',
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

col2.markdown(
    """
        🦄 `assemblit` is a Python package that provides a suite of streamlit-based
        web-components for quickly assembling end-to-end web analytics-as-a-service
        (AaaS) applications. `assemblit` comes with user-authentication, a lightweight
        sqlite3-database backend, and workflow orchestration via `prefect`.

        `alpha-release` coming soon!
    """
)
col2.info(
    'For more information, visit the [assemblit](%s) GitHub page.' % (
        setup.GITHUB_REPOSITORY_URL
    ),
    icon='ℹ️'
)
