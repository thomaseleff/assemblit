""" Essential orchestration server settings """

import os
from assemblit.app import exceptions
from assemblit.orchestrator import layer as server_layer

# Validate web-application type
if 'ASSEMBLIT_APP_TYPE' not in os.environ:
    raise exceptions.MissingEnvironmentVariables(
        ''.join([
            "Missing environment variables.",
            " `assemblit` requires environment variables to be provided within '/.assemblit/config.yaml'.",
            " In order to load the environment variables, run `assemblit run {app}.py`."
            " See https://www.assemblit.org/api/assemblit/setup."
        ])
    )

# Orchestration server configuration settings
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
        SERVER_DIR
    ) = server_layer.load_orchestrator_environment(

        # [required]
        server_type=os.environ['ASSEMBLIT_SERVER_TYPE'],
        server_port=os.environ['ASSEMBLIT_SERVER_PORT'],
        job_name=os.environ['ASSEMBLIT_SERVER_JOB_NAME'],
        job_entrypoint=os.environ['ASSEMBLIT_SERVER_JOB_ENTRYPOINT'],
        deployment_name=os.environ['ASSEMBLIT_SERVER_DEPLOYMENT_NAME'],
        root_dir=os.path.abspath(os.environ['ASSEMBLIT_SERVER_DIR'])
    )
