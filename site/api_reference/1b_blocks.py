""" assemblit.org/api_reference/assemblit/app

Basic building blocks.
"""

import assemblit
from assemblit import blocks
from assemblit.pages import code_documentation


# Initialize the pages code documentation-page content
Documentation = code_documentation.Content(
    package=assemblit,
    package_or_module=blocks
)

# Serve content󠀭󠀭󠀭󠀭
Documentation.serve()
