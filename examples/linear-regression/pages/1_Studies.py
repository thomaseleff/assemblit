"""
Information
---------------------------------------------------------------------
Name        : 1_Studies.py
Location    : ~/pages
Author      : Tom Eleff
Published   : 2024-02-21
Revised on  : .

Description
---------------------------------------------------------------------
Studies-page of the 'linny' web-application.
"""

from assemblit.pages import sessions_selector

# Initialize the session-selector page content
Sessions = sessions_selector.Content(
    header='Studies',
    tagline='Select a study for the session.',
    selector={
        "sort": 0,
        "type": "selectbox",
        "dtype": "str",
        "parameter": "study_name",
        "name": "Study Name",
        "value": "",
        "kwargs": None,
        "description": "Select a study."
    },
    settings=[
        {
            "sort": 0,
            "type": "text-input",
            "dtype": "str",
            "parameter": "study_name",
            "name": "Study Name",
            "value": "",
            "kwargs": None,
            "description": "Input the name of a new study."
        },
        {
            "sort": 1,
            "type": "text-input",
            "dtype": "str",
            "parameter": "country",
            "name": "Country Name",
            "value": "",
            "kwargs": None,
            "description": "Input the name of the corresponding country."
        }
    ],
)

# Serve content
Sessions.serve()
