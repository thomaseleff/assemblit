""" assemblit.org/documentation/getting-started

Getting started with assemblit
"""

import assemblit.pages.home as home

# Initialize the getting-started content
GettingStarted = home.Content(
    header='Getting started',
    tagline="""
        The following guide showcases example `assemblit` web-applications,
         explains how to install `assemblit`
         and how to create your own `assemblit` app.
    """,
    content_file_path='./documentation/getting-started/README.md',
    content_info=None
)

# Serve content
GettingStarted.serve()
