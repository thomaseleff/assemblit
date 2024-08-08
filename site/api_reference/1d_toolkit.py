""" assemblit.org/api_reference/assemblit/toolkit

Data toolkit.
"""

import assemblit
from assemblit import toolkit
from assemblit.pages import code_documentation


# Initialize the pages code documentation-page content
Documentation = code_documentation.Content(
    package=assemblit,
    package_or_module=toolkit
)

# Serve conten
Documentation.serve()
