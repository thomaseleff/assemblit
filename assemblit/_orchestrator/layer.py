""" Workflow orchestration server """

import os
import requests
from typing import List, Tuple, Union
from pytensils import utils
from assemblit import _orchestrator
from assemblit.toolkit import _yaml


# Define abstracted orchestration server function(s)
def load_orchestrator_environment(
    server_type: str,
    server_port: str,
    job_name: str,
    job_entrypoint: str,
    deployment_name: str,
    root_dir: Union[str, os.PathLike]
) -> Tuple[
        str,
        str,
        str,
        int,
        str,
        str,
        str,
        str,
        str,
        str,
        Union[str, os.PathLike]
]:
    """ Loads and validates the orchestration server environment variables and returns the values in the following order,

    - `SERVER_NAME`
    - `SERVER_TYPE`
    - `SERVER_HOST`
    - `SERVER_PORT`
    - `SERVER_API_URL`
    - `SERVER_API_DOCS`
    - `SERVER_JOB_NAME`
    - `SERVER_JOB_ENTRYPOINT`
    - `SERVER_DEPLOYMENT_NAME`
    - `SERVER_DIR`

    Parameters
    ----------
    server_type : `str`
        The type of orchestration server.
    server_port : `str`
        The registered port address of the orchestration server.
    job_name : `str`
        The name of the job.
    job_entrypoint : `str`
        The Python entrypoint of the job.
    deployment_name: `str`
        The name of the job-deployment.
    root_dir : `str | os.PathLike`
        Local directory path of the orchestration server.
    """

    # Validate the orchestration server type
    server_type = _yaml.validate_type(env='orchestrator', type_=server_type, supported_types=_orchestrator.__all__)

    # Validate the orchestration server port
    server_port = _yaml.validate_port(env='orchestrator', port=server_port)

    if server_type == 'prefect':

        # Initialize the `prefect` orchestration server
        server = _orchestrator.prefect.env(
            ASSEMBLIT_SERVER_JOB_NAME=job_name,
            ASSEMBLIT_SERVER_JOB_ENTRYPOINT=os.path.abspath(job_entrypoint),
            ASSEMBLIT_SERVER_DEPLOYMENT_NAME=deployment_name,
            ASSEMBLIT_SERVER_DIR=os.path.abspath(root_dir),
            ASSEMBLIT_SERVER_PORT=utils.as_type(server_port, return_dtype='int')
        )

        return (
            server.ASSEMBLIT_SERVER_NAME,
            server.ASSEMBLIT_SERVER_TYPE,
            server.ASSEMBLIT_SERVER_HOST,
            server.ASSEMBLIT_SERVER_PORT,
            server.api_endpoint(),
            server.docs_endpoint(),
            server.ASSEMBLIT_SERVER_JOB_NAME,
            server.ASSEMBLIT_SERVER_JOB_ENTRYPOINT,
            server.ASSEMBLIT_SERVER_DEPLOYMENT_NAME,
            server.ASSEMBLIT_SERVER_DIR
        )


def create_orchestrator(
    config: dict
):
    """ Creates the orchestration server environment.

    Parameters
    ----------
    config : `dict`
        The `assemblit` configuration.
    """

    # Load the orchestration server type
    server_type = _yaml.load_type(config=config, env='orchestrator', supported_types=_orchestrator.__all__)

    # Load the orchestration server environment variables
    server_environment_dict_object = _yaml.load_environment(config=config, env='orchestrator')

    if server_type == 'prefect':

        # Initialize the `prefect` orchestration server
        server = _orchestrator.prefect.env(**server_environment_dict_object)

    # Create the environment variables
    _yaml.create_environment(dict_object={'ASSEMBLIT_SERVER_TYPE': server_type, **server.to_dict()})

    return server


def start(
    path: Union[str, os.PathLike]
):
    """ Starts the orchestration server.

    Parameters
    ----------
    path : `str | os.PathLike`
        The relative or absolute path to the current work-directory.
    """

    # Load the orchestration server configuration
    config = _yaml.load_configuration(path=os.path.abspath(path))

    # Create the orchestration server environment
    server = create_orchestrator(config=config)

    # Configure the `prefect` server
    server.configure()

    # Start the `prefect` server
    server.start()

    # Deploy the `prefect` server job
    server.deploy(job_entrypoint=os.path.abspath(server.ASSEMBLIT_SERVER_JOB_ENTRYPOINT))


def health_check(
    server_type: str,
    server_port: str,
    job_name: str,
    job_entrypoint: str,
    deployment_name: str,
    root_dir: Union[str, os.PathLike]
) -> requests.Response | bool:
    """ Checks the health of the orchestration server and returns `True` when
    the server is available.

    Parameters
    ----------
    server_type : `str`
        The type of orchestration server.
    server_port : `str`
        The registered port address of the orchestration server.
    job_name : `str`
        The name of the job.
    job_entrypoint : `str`
        The Python entrypoint of the job.
    deployment_name: `str`
        The name of the job-deployment.
    root_dir : `str | os.PathLike`
        Local directory path of the orchestration server.
    """

    # Validate the orchestration server type
    server_type = _yaml.validate_type(env='orchestrator', type_=server_type, supported_types=_orchestrator.__all__)

    if server_type == 'prefect':

        # Initialize the `prefect` orchestration server
        server = _orchestrator.prefect.env(
            ASSEMBLIT_SERVER_JOB_NAME=job_name,
            ASSEMBLIT_SERVER_JOB_ENTRYPOINT=os.path.abspath(job_entrypoint),
            ASSEMBLIT_SERVER_DEPLOYMENT_NAME=deployment_name,
            ASSEMBLIT_SERVER_DIR=os.path.abspath(root_dir),
            ASSEMBLIT_SERVER_PORT=utils.as_type(server_port, return_dtype='int')
        )

    return server.health_check()


def run_job(
    server_type: str,
    server_port: str,
    root_dir: Union[str, os.PathLike],
    name: str,
    job_name: str,
    job_entrypoint: str,
    deployment_name: str,
    **kwargs: dict
) -> dict | None:
    """ Runs the analysis-job.

    Parameters
    ----------
    server_type : `str`
        The type of orchestration server.
    server_port : `str`
        The registered port address of the orchestration server.
    root_dir : `str | os.PathLike`
        Local directory path of the orchestration server.
    name : `str`
        The name of the job-run.
    job_name : `str`
        The name of the job.
    job_entrypoint : `str`
        The Python entrypoint of the job.
    deployment_name : `str`
        The name of the deployment.
    **kwargs : `dict`
        The job-run parameters.
    """

    # Validate the orchestration server type
    server_type = _yaml.validate_type(env='orchestrator', type_=server_type, supported_types=_orchestrator.__all__)

    if server_type == 'prefect':

        # Initialize the `prefect` orchestration server
        server = _orchestrator.prefect.env(
            ASSEMBLIT_SERVER_JOB_NAME=job_name,
            ASSEMBLIT_SERVER_JOB_ENTRYPOINT=os.path.abspath(job_entrypoint),
            ASSEMBLIT_SERVER_DEPLOYMENT_NAME=deployment_name,
            ASSEMBLIT_SERVER_DIR=os.path.abspath(root_dir),
            ASSEMBLIT_SERVER_PORT=utils.as_type(server_port, return_dtype='int')
        )

    return server.run_job(
        name=name,
        job_name=job_name,
        deployment_name=deployment_name,
        **kwargs
    )


def poll_job_run(
    server_type: str,
    server_port: str,
    job_name: str,
    job_entrypoint: str,
    deployment_name: str,
    root_dir: Union[str, os.PathLike],
    run_id: str
) -> dict | None:
    """ Polls the attributes of an analysis-job run.

    Parameters
    ----------
    server_type : `str`
        The type of orchestration server.
    server_port : `str`
        The registered port address of the orchestration server.
    job_name : `str`
        The name of the job.
    job_entrypoint : `str`
        The Python entrypoint of the job.
    deployment_name: `str`
        The name of the job-deployment.
    root_dir : `str | os.PathLike`
        Local directory path of the orchestration server.
    run_id : `str`
        The id of a job run.
    """

    # Validate the orchestration server type
    server_type = _yaml.validate_type(env='orchestrator', type_=server_type, supported_types=_orchestrator.__all__)

    if server_type == 'prefect':

        # Initialize the `prefect` orchestration server
        server = _orchestrator.prefect.env(
            ASSEMBLIT_SERVER_JOB_NAME=job_name,
            ASSEMBLIT_SERVER_JOB_ENTRYPOINT=os.path.abspath(job_entrypoint),
            ASSEMBLIT_SERVER_DEPLOYMENT_NAME=deployment_name,
            ASSEMBLIT_SERVER_DIR=os.path.abspath(root_dir),
            ASSEMBLIT_SERVER_PORT=utils.as_type(server_port, return_dtype='int')
        )

    return server.poll_job_run(run_id=run_id)


def all_job_states(
    server_type: str
) -> List[str]:
    """ Returns all orchestration job-run states as a `list`.

    Parameters
    ----------
    server_type : `str`
        The type of orchestration server.
    """

    # Validate the orchestration server type
    server_type = _yaml.validate_type(env='orchestrator', type_=server_type, supported_types=_orchestrator.__all__)

    if server_type == 'prefect':
        return [str(state).upper() for state in list(_orchestrator.prefect.STATES.keys())]


def all_job_statuses(
    server_type: str
) -> List[str]:
    """ Returns all orchestration job-run statuses as a `list`.

    Parameters
    ----------
    server_type : `str`
        The type of orchestration server.
    """

    # Validate the orchestration server type
    server_type = _yaml.validate_type(env='orchestrator', type_=server_type, supported_types=_orchestrator.__all__)

    if server_type == 'prefect':
        return [str(status) for status in list(_orchestrator.prefect.STATES.values())]


def terminal_job_states(
    server_type: str
) -> List[str]:
    """ Returns the terminal orchestration job-run states as a `list`.

    Parameters
    ----------
    server_type : `str`
        The type of orchestration server.
    """

    # Validate the orchestration server type
    server_type = _yaml.validate_type(env='orchestrator', type_=server_type, supported_types=_orchestrator.__all__)

    if server_type == 'prefect':
        return [str(state) for state in _orchestrator.prefect.TERMINAL_STATES]
