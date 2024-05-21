"""
Information
---------------------------------------------------------------------
Name        : commands.py
Location    : ~/server/cli
Author      : Tom Eleff
Published   : 2024-04-04
Revised on  : .

Description
---------------------------------------------------------------------
The commands available via the `orchestrator` CLI application.
"""

from assemblit.server import layer


# Define server sub-command function(s)
def start(
    server_name: str,
    server_type: str,
    server_port: str,
    root_dir: str,
    workflow_entrypoint: str
):
    """ Starts the orchestration server.

    Parameters
    ----------
    server_name : `str`
        The name of the web-application.
    server_type : `str`
        The type of orchestration server.
    server_port : `str`
        The registered port address of the orchestration server.
    root_dir : `str`
        Local directory path of the orchestration server.
    workflow_entrypoint : `str`
        The `python` program containing the workflow definition and deploy proceedure.
    """

    # Start the orchestration server
    layer.start(
        server_name=server_name,
        server_type=server_type,
        server_port=server_port,
        root_dir=root_dir,
        workflow_entrypoint=workflow_entrypoint
    )
