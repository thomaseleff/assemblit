""" assemblit.org/api_reference/assemblit/orchestrator/cli

Orchestration server management cli-tool.
"""

import assemblit
from assemblit._orchestrator import cli
from assemblit.pages import code_documentation


# Initialize the pages code documentation-page content
Documentation = code_documentation.Content(
    package=assemblit,
    package_or_module=cli
)

# Serve content
Documentation.serve()
