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

import assemblit.setup as setup
import assemblit.pages.home as home

# Initialize the home-page content
Home = home.Content(
    header="Welcome to '%s'" % (setup.NAME),
    tagline='An example `assemblit` web-application for executing simple linear-regression models.',
    # content_url=(setup.GITHUB_CONTENT_URL),
    # content_file_name='README.md',
    content_info='For more information, visit the [assemblit](%s) Github page.' % (
        setup.GITHUB_REPOSITORY_URL
    )
)

# Serve content
Home.serve()
