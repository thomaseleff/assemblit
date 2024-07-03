"""
Information
---------------------------------------------------------------------
Name        : Welcome.py
Location    : ~/

Description
---------------------------------------------------------------------
Home-page of `assemblit`.
"""

import assemblit.setup as setup
import assemblit.pages.home as home


# Initialize the home-page content
Welcome = home.Content(
    header="Welcome to '%s'" % (setup.NAME),
    tagline='Shortening the roadmap to your first analytics customer.',
    content_url=setup.GITHUB_CONTENT_URL,
    content_file_name='README.md',
    content_info='For more information, visit the [assemblit](%s) GitHub page.' % (
        setup.GITHUB_REPOSITORY_URL
    )
)

# Serve content
Welcome.serve()
