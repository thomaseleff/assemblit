""" assemblit.org/api_reference/assemblit/app

Assemblit app deployment.
"""

import assemblit
from assemblit.app import layer
from assemblit.pages import code_documentation


# Initialize the pages code documentation-page content
Documentation = code_documentation.Content(
    package=assemblit,
    package_or_module=layer
)

# Serve content
Documentation.serve()
