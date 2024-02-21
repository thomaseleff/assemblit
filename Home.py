"""
Information
---------------------------------------------------------------------
Name        : Home.py
Location    : ~/
Author      : Tom Eleff
Published   : 2024-02-21
Revised on  : .

Description
---------------------------------------------------------------------
Home-page of the getstreamy web-application
"""

import getstreamy.setup as setup
import getstreamy.pages.home as home

# Initialize the home-page content
Home = home.Content(
    header='Welcome to %s' % (setup.NAME),
    tagline='A streamlit-based web-application for showcasing analytics models hosted on Github.',
    content_url=(
        setup.GITHUB_CONTENT_URL
    ),
    content_file_name='README.md',
    content_info='For more information, visit the [Get-Streamy](%s) Github page.' % (
        setup.GITHUB_REPOSITORY_URL
    )
)

# Serve content
Home.serve()
