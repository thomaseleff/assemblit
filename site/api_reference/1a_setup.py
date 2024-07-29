""" assemblit.org/api_reference/assemblit/setup

Environment variables.
"""

import assemblit
from assemblit import setup
from assemblit.pages import code_documentation


# Initialize the pages code documentation-page content
Documentation = code_documentation.Content(
    package=assemblit,
    package_or_module=setup
)

# Serve content󠀭󠀭󠀭󠀭
Documentation.serve()
