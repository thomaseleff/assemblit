""" assemblit.org/api_reference/assemblit

**alpha-release** coming soon!
"""

import assemblit
from assemblit.pages import code_documentation


# Initialize the pages code documentation-page content
Documentation = code_documentation.Content(
    package=assemblit,
    package_or_module=assemblit
)

# Serve content󠀭󠀭󠀭󠀭
Documentation.serve()
