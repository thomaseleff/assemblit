
"""
Information
---------------------------------------------------------------------
Name        : setup.py
Location    : ~/server

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
    SERVER_JOB_NAME,
    SERVER_JOB_ENTRYPOINT,
    SERVER_DEPLOYMENT_NAME,
    SERVER_DEPLOYMENT_VERSION
) = layer.load_orchestrator_environment(
    server_name=os.environ['NAME'],
    server_type=os.environ['SERVER_TYPE'],
    server_port=os.environ['SERVER_PORT'],
    client_port=os.environ['CLIENT_PORT'],
    job_name=os.environ['SERVER_JOB_NAME'],
    job_entrypoint=os.environ['SERVER_JOB_ENTRYPOINT'],
    deployment_name=os.environ['SERVER_DEPLOYMENT_NAME'],
    deployment_version=os.environ['VERSION'],
    root_dir=os.path.abspath(
        os.path.join(
            os.environ['DIR'],
            'db'
        )
    )
)
