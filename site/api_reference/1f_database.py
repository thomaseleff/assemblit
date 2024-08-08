""" assemblit.org/api_reference/assemblit/database

Database management.
"""

import assemblit
from assemblit import database
from assemblit.pages import code_documentation


# Initialize the pages code documentation-page content
Documentation = code_documentation.Content(
    package=assemblit,
    package_or_module=database
)

# Serve content
Documentation.serve()
