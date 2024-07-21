""" Home-page of `assemblit.org`.

Assemblit is helping data analysts and scientists rapidly scale notebooks into analytics-as-a-service (AaaS) web-applications.
"""

import streamlit as st
import assemblit
import assemblit.setup as setup
import assemblit.pages.home as home
import inspect


# Initialize the home-page content
Welcome = home.Content(
    header='Welcome',
    tagline="""
        Assemblit is helping data analysts and scientists rapidly scale notebooks
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
col2.markdown(inspect.getdoc(assemblit))
col2.subheader('')
col2.info(
    'For more information, visit the [assemblit](%s) GitHub page.' % (
        setup.GITHUB_REPOSITORY_URL
    ),
    icon='ℹ️'
)
