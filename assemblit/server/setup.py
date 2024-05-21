
"""
Information
---------------------------------------------------------------------
Name        : setup.py
Location    : ~/server
Author      : Tom Eleff
Published   : 2024-05-07
Revised on  : .

Description
---------------------------------------------------------------------
Initializes the orchestration server abstraction layer for
starting, managing and interacting with the orchestration server.

Contains the static variables essential to the orchestration server.
"""

import os
from assemblit.server import layer

# Orchestration server configuration settings
(
    SERVER_NAME,
    SERVER_TYPE,
    SERVER_HOST,
    SERVER_PORT,
    SERVER_API_URL,
    SERVER_API_DOCS,
    SERVER_DEPLOYMENT_ID,
    SERVER_DEPLOYMENT_VERSION
) = layer.load_environment(
    server_name=os.environ['NAME'],
    server_type=os.environ['SERVER_TYPE'],
    server_port=os.environ['SERVER_PORT'],
    client_port=os.environ['CLIENT_PORT'],
    flow_name=os.environ['SERVER_WORKFLOW_NAME'],
    flow_entrypoint=os.environ['SERVER_WORKFLOW_ENTRYPOINT'],
    deployment_name=os.environ['SERVER_DEPLOYMENT_NAME'],
    deployment_version=os.environ['VERSION'],
    root_dir=os.path.abspath(
        os.path.join(
            os.environ['DIR'],
            'db'
        )
    )
)
