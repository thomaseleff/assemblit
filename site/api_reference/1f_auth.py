""" assemblit.org/api_reference/assemblit/auth

User authentication.
"""

import assemblit
from assemblit import auth
from assemblit.pages import code_documentation


# Initialize the pages code documentation-page content
Documentation = code_documentation.Content(
    package=assemblit,
    package_or_module=auth
)

# Serve content
Documentation.serve()
