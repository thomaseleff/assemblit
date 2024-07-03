"""
Information
---------------------------------------------------------------------
Name        : Home.py
Location    : ~/
Author      : Tom Eleff
Published   : 2024-04-05
Revised on  : .

Description
---------------------------------------------------------------------
Home-page of the linear-regression web-application.
"""

import streamlit as st
import assemblit.setup as setup
import assemblit.pages.home as home


# Initialize the home-page content
Welcome = home.Content(
    header="Welcome to '%s'" % (setup.NAME),
    tagling='Shortening the roadmap to your first analytics customer.',
    # content_url=(setup.GITHUB_CONTENT_URL),
    # content_file_name='README.md',
    content_info='For more information, visit the [assemblit](%s) Github page.' % (
        setup.GITHUB_REPOSITORY_URL
    )
)

# Serve content
Welcome.serve()

# Static content
_, col2, _ = st.columns(setup.CONTENT_COLUMNS)

with col2:
    st.markdown(
        """
            🦄 `assemblit` is a Python package that provides a suite of streamlit-based web-components for quickly assembling
            end-to-end web analytics-as-a-service (AaaS) applications. `assemblit` comes with user-authentication, a
            lightweight sqlite3-database backend, and workflow orchestration via `prefect`.

            alpha-release coming soon!
        """
    )
