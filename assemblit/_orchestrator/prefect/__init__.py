""" Workflow orchestration server """

import os
import sys
import time
import subprocess
import requests
from typing import List, Union, Optional
from dataclasses import dataclass, field, fields, asdict
from assemblit.toolkit import _exceptions
from assemblit._orchestrator import status


# Job-run state settings
STATES: dict = {
    'SCHEDULED': status.SCHEDULED,
    'LATE': status.LATE,
    'AWAITINGRETRY': status.RETRYING,
    'PENDING': status.PENDING,
    'RUNNING': status.RUNNING,
    'RETRYING': status.RETRYING,
    'PAUSED': status.PAUSED,
    'CANCELLING': status.CANCELLED,
    'CANCELLED': status.CANCELLED,
    'COMPLETED': status.SUCCEEDED,
    'FAILED': status.FAILED,
    'CRASHED': status.CRASHED
}
TERMINAL_STATES: List[str] = ['CANCELLED', 'COMPLETED', 'FAILED', 'CRASHED']


@dataclass
class env():
    """ [Prefect](https://www.prefect.io/) offers modern workflow orchestration tools for
    building, observing & reacting to data pipelines efficiently.

    The `prefect` orchestrator runs a local server and control panel and automatically
    generates a deployment from the provided `flow` workflow, which is exposed via the
    server API to allow for running, polling and listing `flow` runs. `flow` runs are
    executed via the local server as subprocesses.

    Attributes
    ----------
    ASSEMBLIT_SERVER_JOB_NAME : `str`
        The name of the `prefect` `flow`.
    ASSEMBLIT_SERVER_JOB_ENTRYPOINT : `str`
        The absolute or relative path of the local Python script that contains the definition of the `prefect` `flow`.
    ASSEMBLIT_SERVER_DEPLOYMENT_NAME : `str`
        The name of the `prefect` `deployment`.
    ASSEMBLIT_SERVER_PORT : `str` = '4200'
        The registered port address of the orchestration server.

    Not implemented
    ---------------
    ASSEMBLIT_SERVER_JOB_RUN_CONCURRENCY : `int`
        The number of `flow` runs that are allowed to execute concurrently.
    """

    # Host and route settings
    ASSEMBLIT_SERVER_HOST: str = field(default='127.0.0.1', init=False)
    ASSEMBLIT_SERVER_API_ROUTE: str = field(default='api', init=False)
    ASSEMBLIT_SERVER_API_DOCS: str = field(default='docs', init=False)

    # [required]

    # Orchestration server configuration settings
    ASSEMBLIT_SERVER_NAME: str = field(default='assemblit', init=False)
    ASSEMBLIT_SERVER_JOB_NAME: str = field(default=None)
    ASSEMBLIT_SERVER_JOB_ENTRYPOINT: Union[str, os.PathLike] = field(default=None)
    ASSEMBLIT_SERVER_DEPLOYMENT_NAME: str = field(default=None)
    ASSEMBLIT_SERVER_DIR: Union[str, os.PathLike] = field(default=None)

    # [optional]

    # Add'l orchestration server configuration settings
    ASSEMBLIT_SERVER_TYPE: Optional[str] = field(default="prefect", init=False)

    # Add'l port configuration settings
    ASSEMBLIT_SERVER_PORT: Optional[int] = field(default=4200)

    # Define dataclass method(s)
    def __post_init__(self):
        """ Validates the environment variables. Raises a `MissingEnvironmentVariables` exception
        if environment variables are set to `None`. Raises a `ValueError` exception if the
        environment variable type is invalid.
        """

        # Validate environment variables
        missing_variables = [name for name, value in self.__dict__.items() if value is None]
        if missing_variables:
            raise _exceptions.MissingEnvironmentVariables

        # Validate types
        for variable in fields(self):
            value = getattr(self, variable.name)
            if not isinstance(value, variable.type):
                raise ValueError(
                    'Invalid dtype {%s} for {%s}. Expected {%s}.' % (
                        type(value).__name__,
                        variable.name,
                        (variable.type).__name__
                    )
                )

            # Convert relative directory paths to absoluate paths
            if variable.name in ['ASSEMBLIT_SERVER_JOB_ENTRYPOINT', 'ASSEMBLIT_SERVER_DIR']:
                setattr(self, variable.name, os.path.abspath(getattr(self, variable.name)))

    def to_dict(self) -> dict:
        """ Returns the environment variables and values as a dictionary. """
        return asdict(self)

    def list_variables(self) -> list:
        """ Returns the environment variable names as a list. """
        return list(asdict(self).keys())

    def values(self) -> tuple:
        """ Returns the environment variable values as a tuple. """
        return tuple(asdict(self).values())

    # Define class method(s) for generating API-endpoints
    def api_endpoint(self) -> str:
        """ Returns the `prefect` server REST API endpoint.
        """
        return 'http://%s:%s/%s' % (
            self.ASSEMBLIT_SERVER_HOST,
            self.ASSEMBLIT_SERVER_PORT,
            self.ASSEMBLIT_SERVER_API_ROUTE
        )

    def docs_endpoint(self) -> str:
        """ Returns the `prefect` server REST API documentation endpoint.
        """
        return 'http://%s:%s/%s' % (
            self.ASSEMBLIT_SERVER_HOST,
            self.ASSEMBLIT_SERVER_PORT,
            self.ASSEMBLIT_SERVER_API_DOCS
        )

    def health_endpoint(self) -> str:
        """ Returns the `prefect` server health-check REST API endpoint.
        """
        return '/'.join([self.api_endpoint(), 'health'])

    def token_endpoint(self) -> str:
        """ Returns the `prefect` server csrf-token REST API endpoint.
        """
        return '/'.join([self.api_endpoint(), 'csrf-token'])

    def deployment_id_endpoint(
        self,
        job_name: str,
        deployment_name: str
    ) -> str:
        """ Returns the `prefect` server deployment-id REST API endpoint.

        Parameters
        ----------
        job_name : `str`
            The name of the `prefect` `flow`.
        deployment_name : `str`
            The name of the `prefect` `deployment`.
        """
        return '/'.join([self.api_endpoint(), 'deployments', 'name', job_name, deployment_name])

    def run_job_endpoint(
        self,
        deployment_id: str
    ) -> str:
        """ Returns the `prefect` server run-flow REST API endpoint.

        Parameters
        ----------
        deployment_id : `str`
            The id of the `prefect` `deployment`.
        """
        return '/'.join([self.api_endpoint(), 'deployments', deployment_id, 'create_flow_run'])

    def poll_job_run_endpoint(
        self,
        run_id: str
    ) -> str:
        """ Returns the `prefect` server flow-status REST API endpoint.

        Parameters
        ----------
        run_id : `str`
            The id of a recent `prefect` `flow` run.
        """
        return '/'.join([self.api_endpoint(), 'flow_runs', run_id])

    # Define class method(s) for configuring the orchestration server
    def configure(self) -> str:
        """ Configures the `prefect` orchestration server.
        """

        # Create the database directory if it does not exist
        if not os.path.exists(self.ASSEMBLIT_SERVER_DIR):
            os.mkdir(self.ASSEMBLIT_SERVER_DIR)

        # Set environment variables that cannot be configured via the CLI
        os.environ['PREFECT_HOME'] = self.ASSEMBLIT_SERVER_DIR

        # Return the configuration command(s)
        configure = subprocess.Popen(
            ' && '.join([
                'prefect config set PREFECT_API_URL="%s"' % (self.api_endpoint()),
                'prefect config set PREFECT_CLI_WRAP_LINES="false"'
            ]),
            shell=True
        )

        # Communicate
        _, _ = configure.communicate()

        # Status
        start_status = configure.wait()

        return start_status

    # Define class method(s) for executing commands
    def start(self):
        """ Starts the `prefect` orchestration server.
        """
        orchestrator = subprocess.Popen(
            'prefect server start --host="%s" --port="%s"' % (
                self.ASSEMBLIT_SERVER_HOST,
                self.ASSEMBLIT_SERVER_PORT
            ),
            shell=True
        )

        # Wait for healthy response
        while not self.health_check():
            time.sleep(1)

        return orchestrator

    def deploy(
        self,
        job_entrypoint: str
    ):
        """ Deploys a `prefect` orchestration server `flow`.

        Parameters
        ----------
        job_entrypoint : `str`
            The filename of the python executable that contains the definition
                of the `prefect` `flow`.
        """
        return subprocess.Popen(
            '"%s" "%s"' % (sys.executable, job_entrypoint),
            shell=True
        )

    def health_check(self) -> Union[requests.Response, bool]:
        """ Checks the health of the `prefect` orchestration server.
        Returns `True` when the `prefect` orchestration server is available.
        """
        try:
            return requests.get(self.health_endpoint())
        except requests.exceptions.ConnectionError:
            return False

    def get_token(self) -> Union[requests.Response, None]:
        """ Returns a `prefect` orchestration server csrf-token.
        """
        try:
            return requests.get(
                self.token_endpoint(),
                params={'client': self.ASSEMBLIT_SERVER_NAME}
            ).json()['token']
        except requests.exceptions.ConnectionError:
            return None

    def get_deployment_id(
        self,
        job_name: str,
        deployment_name: str
    ) -> Union[requests.Response, None]:
        """ Returns a `prefect` orchestration server `deployment` id.

        Parameters
        ----------
        job_name : `str`
            The name of the `prefect` `flow`.
        deployment_name : `str`
            The name of the `prefect` `deployment`.
        """
        try:
            return requests.get(
                self.deployment_id_endpoint(
                    job_name=job_name,
                    deployment_name=deployment_name
                )
            ).json()['id']
        except requests.exceptions.ConnectionError:
            return None

    def run_job(
        self,
        name: str,
        job_name: str,
        deployment_name: str,
        **kwargs: dict
    ) -> Union[dict, None]:
        """ Creates a `prefect` orchestration server `flow` run from a `deployment`.

        Parameters
        ----------
        name : `str`
            The name of the `prefect` `flow` run.
        job_name : `str`
            The name of the `prefect` `flow`.
        deployment_name : `str`
            The name of the `prefect` `deployment`.
        **kwargs : `dict`
            The `flow` run parameters.
        """
        try:
            flow_run = requests.post(
                self.run_job_endpoint(
                    deployment_id=self.get_deployment_id(
                        job_name=job_name,
                        deployment_name=deployment_name
                    )
                ),
                json={
                    'name': name,
                    'tags': [self.ASSEMBLIT_SERVER_NAME],
                    'parameters': kwargs
                },
                headers={
                    'prefect-csrf-token': self.get_token(),
                    'prefect-csrf-client': self.ASSEMBLIT_SERVER_NAME,
                }
            ).json()

            return {
                'id': flow_run['id'],
                'state': str(flow_run['state']['name']).upper(),
                'start_time': flow_run['start_time'],
                'end_time': flow_run['end_time'],
                'run_time': flow_run['total_run_time'],
                'parameters': flow_run['parameters'],
                'tags': flow_run['tags'],
                'url': 'http://%s:%s/flow-runs/flow-run/%s' % (
                    self.ASSEMBLIT_SERVER_HOST,
                    self.ASSEMBLIT_SERVER_PORT,
                    flow_run['id']
                )
            }
        except requests.exceptions.ConnectionError:
            return None

    def poll_job_run(
        self,
        run_id: str
    ) -> Union[dict, None]:
        """ Polls the status of a `prefect` orchestration server flow-run.

        Parameters
        ----------
        run_id : `str`
            The id of a `prefect` `flow` run.
        """
        try:
            flow_run = requests.get(self.poll_job_run_endpoint(run_id=run_id)).json()

            return {
                'state': str(flow_run['state']['name']).upper(),
                'start_time': flow_run['start_time'],
                'end_time': flow_run['end_time'],
                'run_time': flow_run['total_run_time']
            }
        except requests.exceptions.ConnectionError:
            return None
