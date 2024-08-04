""" Essential orchestration server settings """

import os
from assemblit.app import layer
from assemblit.server import layer as server_layer

# Orchestration server configuration settings
if 'ASSEMBLIT_APP_TYPE' not in os.environ:
    raise layer.MissingEnvironmentVariables(
        ''.join([
            "Missing environment variables.",
            " `assemblit` requires environment variables to be provided within '/.assemblit/config.yaml'.",
            " In order to load the environment variables, run `assemblit run {app}.py`."
            " See https://www.assemblit.org/api/assemblit/setup."
        ])
    )

if os.environ['ASSEMBLIT_APP_TYPE'].strip().lower() in ['aaas']:
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
    ) = server_layer.load_orchestrator_environment(
        server_name=os.environ['ASSEMBLIT_NAME'],
        server_type=os.environ.get('ASSEMBLIT_SERVER_TYPE', 'prefect'),
        server_port=os.environ.get('ASSEMBLIT_SERVER_PORT', '4200'),
        client_port=os.environ['ASSEMBLIT_CLIENT_PORT'],
        job_name=os.environ['ASSEMBLIT_SERVER_JOB_NAME'],
        job_entrypoint=os.environ['ASSEMBLIT_SERVER_JOB_ENTRYPOINT'],
        deployment_name=os.environ['ASSEMBLIT_SERVER_DEPLOYMENT_NAME'],
        deployment_version=os.environ['ASSEMBLIT_VERSION'],
        root_dir=os.path.abspath(
            os.path.join(
                os.environ['ASSEMBLIT_DIR'],
                'db'
            )
        )
    )
