""" assemblit.org/api_reference/assemblit/pages

Webpage builders.
"""

import assemblit
from assemblit import pages
from assemblit.pages import code_documentation


# Initialize the pages code documentation-page content
Documentation = code_documentation.Content(
    package=assemblit,
    package_or_module=pages
)

# Serve conten
Documentation.serve()
