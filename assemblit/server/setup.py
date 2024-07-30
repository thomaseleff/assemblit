""" Essential orchestration server settings """

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
    server_name=os.environ['ASSEMBLIT_NAME'],
    server_type=os.environ.get('ASSEMBLIT_SERVER_TYPE', 'prefect'),
    server_port=os.environ.get('ASSEMBLIT_SERVER_PORT', '4200'),
    client_port=os.environ['ASSEMBLIT_CLIENT_PORT'],
    job_name=os.environ.get('ASSEMBLIT_SERVER_JOB_NAME', ''),
    job_entrypoint=os.environ.get('ASSEMBLIT_SERVER_JOB_ENTRYPOINT', ''),
    deployment_name=os.environ.get('ASSEMBLIT_SERVER_DEPLOYMENT_NAME', ''),
    deployment_version=os.environ['ASSEMBLIT_VERSION'],
    root_dir=os.path.abspath(
        os.path.join(
            os.environ['ASSEMBLIT_DIR'],
            'db'
        )
    )
)
