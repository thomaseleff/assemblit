""" localhost:{ASSEMBLIT_CLIENT_PORT}

🚀 `linny` is an Analytics-as-a-service (AaaS) web-application for executing simple
linear-regression models and for evaluating the assumptions of linear-regression across different datasets.
"""

import assemblit.setup as setup
import assemblit.pages.home as home

# Initialize the home-page content
Home = home.Content(
    header="Welcome to '%s'" % (setup.NAME),
    tagline='🚀 `linny` is an Analytics-as-a-service (AaaS) web-application for executing simple linear-regression models and for evaluating the assumptions of linear-regression across different datasets.',
    content_file_path='./documentation/getting-started/README.md',
    content_info='For more information, visit the [assemblit](%s) Github page.' % (
        setup.GITHUB_REPOSITORY_URL
    )
)

# Serve content
Home.serve()
