"""
Information
---------------------------------------------------------------------
Name        : layer.py
Location    : ~/server
Author      : Tom Eleff
Published   : 2024-06-02
Revised on  : .

Description
---------------------------------------------------------------------
The orchestration server abstraction layer for starting, managing
and interacting with the orchestration server.
"""

import requests
from typing import List, Tuple
from pytensils import utils
from assemblit.server import orchestrators

# Assign private variable(s)
_SERVER_TYPES: List[str] = [
    'prefect'
]


# Define parsing function(s)
def parse_server_type(
    server_type: str
) -> str:
    """ Validates the orchestration server type. Returns the server type as a `str`
    if a valid server type is provided, otherwise raises a `NotImplementedError`.

    Parameters
    ----------
    server_type : `str`
        The type of orchestration server.
    """

    # Ensure that the server-type is a valid supported orchestration tool
    if server_type.strip().lower() in [i.strip().lower() for i in _SERVER_TYPES]:
        return server_type.strip().lower()
    else:
        raise NotImplementedError(
            ''.join([
                'Invalid server-type argument value {%s}.' % server_type,
                ' Currently, `assemblit` supports the following orchestration server types, [%s].' % (
                    ', '.join(["'%s'" % (i.strip().lower()) for i in _SERVER_TYPES])
                )
            ])
        )


def parse_server_port(
    server_port: str,
    client_port: str
) -> str:
    """ Validates the orchestration server port. Returns the server port as a `str`
    if a valid server port is provided, otherwise raises a `ValueError` when the
    same port has been configured as both the `streamlit` client-port as well as the
    orchestration server-port and raises a `TypeError` when the port is not an
    integer as a string.

    Parameters
    ----------
    server_port : `str`
        The registered port address of the orchestration server.
    client_port : `str`
        The registered port address of the `streamlit` client server.
    """

    # Ensure the server-port is an integer as a string
    try:
        server_port_int = utils.as_type(value=server_port, return_dtype='int')
    except TypeError:
        raise TypeError(
            'Invalid server-port argument value {%s}. The server-port value must be an integer as a string.' % (
                server_port
            )
        )

    # Ensure the server-port is a valid port address number
    if (
        (server_port_int < 0)
        or (server_port_int > 65535)
    ):
        raise ValueError(
            ''.join([
                'Invalid server-port argument value {%s}.' % (server_port),
                ' The server-port value must be between 0 and 65535.'
            ])
        )

    # Ensure the server-port is unique and does not conflict with the `assemblit` streamlit port
    if server_port_int == utils.as_type(value=str(client_port), return_dtype='int'):
        raise ValueError(
            ''.join([
                'Invalid server-port argument value {%s}.' % (server_port),
                ' The server-port value cannot be the same as the `streamlit` web-application port.'
            ])
        )

    return str(server_port_int).strip().lower()


# Define abstracted orchestration server function(s)
def load_orchestrator_environment(
    server_name: str,
    server_type: str,
    server_port: str,
    client_port: str,
    job_name: str,
    job_entrypoint: str,
    deployment_name: str,
    deployment_version: str,
    root_dir: str
) -> Tuple[str, str, str, str]:
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
           - `SERVER_DEPLOYMENT_VERSION`

    Parameters
    ----------
    server_name : `str`
        The name of the web-application.
    server_type : `str`
        The type of orchestration server.
    server_port : `str`
        The registered port address of the orchestration server.
    client_port : `str`
        The registered port address of the `streamlit` client server.
    job_name : `str`
        The name of the job.
    job_entrypoint : `str`
        The Python entrypoint of the job.
    deployment_name: `str`
        The name of the job-deployment.
    deployment_version : `str`
        The version of job-deployment.
    root_dir : `str`
        Local directory path of the orchestration server.
    """

    # Parse
    server_type = parse_server_type(server_type=server_type)
    server_port = parse_server_port(server_port=server_port, client_port=client_port)

    if server_type == 'prefect':

        # Initialize the `prefect` orchestration server
        Prefect = orchestrators.Prefect(
            server_name=server_name,
            server_port=server_port,
            root_dir=root_dir
        )

        # Return environment parameters
        return (
            server_name,
            server_type,
            Prefect.SERVER_HOST,
            server_port,
            Prefect.api_endpoint(),
            Prefect.docs_endpoint(),
            job_name,
            job_entrypoint,
            deployment_name,
            deployment_version
        )

    else:
        raise NotImplementedError(
            ''.join([
                'Invalid orchestration server type {%s}.' % server_type,
                ' Currently, `assemblit` supports the following orchestration server types, [%s].' % (
                    ', '.join(["'%s'" % (i.strip().lower()) for i in _SERVER_TYPES])
                )
            ])
        )


def start(
    server_name: str,
    server_type: str,
    server_port: str,
    root_dir: str,
    job_entrypoint: str
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
    job_entrypoint : `str`
        The `python` program containing the job definition and deploy proceedure.
    """

    # Parse
    server_type = parse_server_type(server_type=server_type)

    if server_type == 'prefect':

        # Initialize the `prefect` orchestration server
        Prefect = orchestrators.Prefect(
            server_name=server_name,
            server_port=server_port,
            root_dir=root_dir
        )

        # Configure the `prefect` server
        Prefect.configure()

        # Start the `prefect` server
        Prefect.start()

        # Deploy the `prefect` server job
        Prefect.deploy(job_entrypoint=job_entrypoint)

    else:
        raise NotImplementedError(
            ''.join([
                'Invalid orchestration server type {%s}.' % server_type,
                ' Currently, `assemblit` supports the following orchestration server types, [%s].' % (
                    ', '.join(["'%s'" % (i.strip().lower()) for i in _SERVER_TYPES])
                )
            ])
        )


def health_check(
    server_name: str,
    server_type: str,
    server_port: str,
    root_dir: str
) -> requests.Response | bool:
    """ Checks the health of the orchestration server and returns `True` when
    the orchestration server is available.

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
    """

    # Parse
    server_type = parse_server_type(server_type=server_type)

    if server_type == 'prefect':

        # Initialize the `prefect` orchestration server
        Prefect = orchestrators.Prefect(
            server_name=server_name,
            server_port=server_port,
            root_dir=root_dir
        )

        return Prefect.health_check()

    else:
        raise NotImplementedError(
            ''.join([
                'Invalid orchestration server type {%s}.' % server_type,
                ' Currently, `assemblit` supports the following orchestration server types, [%s].' % (
                    ', '.join(["'%s'" % (i.strip().lower()) for i in _SERVER_TYPES])
                )
            ])
        )


def run_job(
    server_name: str,
    server_type: str,
    server_port: str,
    root_dir: str,
    name: str,
    job_name: str,
    deployment_name: str,
    deployment_version: str,
    **kwargs: dict
) -> dict | None:
    """ Runs the analysis-job.

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
    name : `str`
        The name of the job-run.
    job_name : `str`
        The name of the job.
    deployment_name : `str`
        The name of the deployment.
    deployment_version : `str`
        The version of the deployment.
    **kwargs : `dict`
        The job-run parameters.
    """

    # Parse
    server_type = parse_server_type(server_type=server_type)

    if server_type == 'prefect':

        # Initialize the `prefect` orchestration server
        Prefect = orchestrators.Prefect(
            server_name=server_name,
            server_port=server_port,
            root_dir=root_dir
        )

        return Prefect.run_job(
            name=name,
            job_name=job_name,
            deployment_name=deployment_name,
            deployment_version=deployment_version,
            **kwargs
        )

    else:
        raise NotImplementedError(
            ''.join([
                'Invalid orchestration server type {%s}.' % server_type,
                ' Currently, `assemblit` supports the following orchestration server types, [%s].' % (
                    ', '.join(["'%s'" % (i.strip().lower()) for i in _SERVER_TYPES])
                )
            ])
        )


def poll_job_run(
    server_name: str,
    server_type: str,
    server_port: str,
    root_dir: str,
    run_id: str
) -> dict | None:
    """ Polls the attributes of an analysis-job run.

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
    run_id : `str`
        The id of a job run.
    """

    # Parse
    server_type = parse_server_type(server_type=server_type)

    if server_type == 'prefect':

        # Initialize the `prefect` orchestration server
        Prefect = orchestrators.Prefect(
            server_name=server_name,
            server_port=server_port,
            root_dir=root_dir
        )

        return Prefect.poll_job_run(run_id=run_id)

    else:
        raise NotImplementedError(
            ''.join([
                'Invalid orchestration server type {%s}.' % server_type,
                ' Currently, `assemblit` supports the following orchestration server types, [%s].' % (
                    ', '.join(["'%s'" % (i.strip().lower()) for i in _SERVER_TYPES])
                )
            ])
        )


def all_job_states(
    server_type: str
) -> List[str]:
    """ Returns all orchestration job-run states as a `list`.

    Parameters
    ----------
    server_type : `str`
        The type of orchestration server.
    """

    # Parse
    server_type = parse_server_type(server_type=server_type)

    if server_type == 'prefect':
        return [str(state).upper() for state in list(orchestrators.Prefect.STATES.keys())]

    else:
        raise NotImplementedError(
            ''.join([
                'Invalid orchestration server type {%s}.' % server_type,
                ' Currently, `assemblit` supports the following orchestration server types, [%s].' % (
                    ', '.join(["'%s'" % (i.strip().lower()) for i in _SERVER_TYPES])
                )
            ])
        )


def all_job_statuses(
    server_type: str
) -> List[str]:
    """ Returns all orchestration job-run statuses as a `list`.

    Parameters
    ----------
    server_type : `str`
        The type of orchestration server.
    """

    # Parse
    server_type = parse_server_type(server_type=server_type)

    if server_type == 'prefect':
        return [str(status) for status in list(orchestrators.Prefect.STATES.values())]

    else:
        raise NotImplementedError(
            ''.join([
                'Invalid orchestration server type {%s}.' % server_type,
                ' Currently, `assemblit` supports the following orchestration server types, [%s].' % (
                    ', '.join(["'%s'" % (i.strip().lower()) for i in _SERVER_TYPES])
                )
            ])
        )


def terminal_job_states(
    server_type: str
) -> List[str]:
    """ Returns the terminal orchestration job-run states as a `list`.

    Parameters
    ----------
    server_type : `str`
        The type of orchestration server.
    """

    # Parse
    server_type = parse_server_type(server_type=server_type)

    if server_type == 'prefect':
        return [str(state) for state in orchestrators.Prefect.TERMINAL_STATES]

    else:
        raise NotImplementedError(
            ''.join([
                'Invalid orchestration server type {%s}.' % server_type,
                ' Currently, `assemblit` supports the following orchestration server types, [%s].' % (
                    ', '.join(["'%s'" % (i.strip().lower()) for i in _SERVER_TYPES])
                )
            ])
        )
