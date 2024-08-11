""" Demo assemblit web-application

Assemblit is helping data analysts and scientists rapidly scale notebooks into analytics-as-a-service (AaaS) web-applications.
"""

import streamlit as st
from assemblit import setup
from assemblit.pages import home

# Setup
# The `assemblit.setup` module contains global-settings that can be set for each web-page
#   as well as environment variable options configured within `./.assemblit/config.yaml`
setup.LAYOUT = 'centered'
setup.INITIAL_SIDEBAR_STATE = 'collapsed'

# Initialize the home-page content
Welcome = home.Content(
    header='🎉 Success!',
    tagline="""
        Assemblit is helping data analysts and scientists rapidly scale notebooks into
         analytics-as-a-service (AaaS) web-applications.
    """,
    content_file_path='./README.md',
    content_info=None
)

# Serve content
# `assemblit` page content must be served first in the Python script
#   since `assemblit` pages configure st.set_page_config()
Welcome.serve()

# Celebrate
# Other `streamlit` based components can be served after the `assemblit` content
st.balloons()
