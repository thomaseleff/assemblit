""" assemblit.org/api_reference/assemblit/server

Orchestration server management.
"""

import assemblit
from assemblit import server
from assemblit.pages import code_documentation


# Initialize the pages code documentation-page content
Documentation = code_documentation.Content(
    package=assemblit,
    package_or_module=server
)

# Serve content
Documentation.serve()
