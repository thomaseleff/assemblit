""" assemblit.org

Assemblit is helping data analysts and scientists rapidly scale notebooks into analytics-as-a-service (AaaS) web-applications.
"""

import assemblit.setup as setup
import assemblit.pages.home as home

# Initialize the home-page content
Welcome = home.Content(
    header='Welcome',
    tagline="""
        Assemblit is helping data analysts and scientists rapidly scale notebooks into
         analytics-as-a-service (AaaS) web-applications.
    """,
    content_file_path='./README.md',
    content_info='For more information, visit the [assemblit](%s) GitHub page.' % (
        setup.GITHUB_REPOSITORY_URL
    )
)

# Serve content
Welcome.serve()
