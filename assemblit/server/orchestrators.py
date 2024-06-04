"""
Information
---------------------------------------------------------------------
Name        : orchestrators.py
Location    : ~/server
Author      : Tom Eleff
Published   : 2024-06-02
Revised on  : .

Description
---------------------------------------------------------------------
The orchestration server `class` options.
"""

import os
import sys
import time
import subprocess
import requests


class Prefect():

    def __init__(
        self,
        server_name: str,
        server_port: str,
        root_dir: str
    ):
        """ [Prefect](https://www.prefect.io/) offers modern workflow orchestration tools for
        building, observing & reacting to data pipelines efficiently.

        The `prefect` orchestrator runs a local server and control panel and automatically
        generates a deployment from the provided `flow` workflow, which is exposed via the
        server API to allow for running, polling and listing `flow` runs. `flow` runs are
        executed via the local server as subprocesses.

        Environment variable options
        ----------------------------

        - `SERVER_TYPE` : `str` = 'prefect' Indicates to use the `prefect` orchestrator.
        - `SERVER_PORT` : `str`             The registered port address of the orchestration server.
                                                Default = '4200'
        - `SERVER_JOB_NAME` : `str`         The name of the `prefect` `flow`.
        - `SERVER_JOB_ENTRYPOINT` : `str`   The filename of the python executable that contains the definition
                                                of the `prefect` `flow`.
        - `SERVER_DEPLOYMENT_NAME` : `str`  The name of the `prefect` `deployment`.

        Not implemented,
        - `SERVER_CONCURRENCY` : `int`      The number of `flow` runs that are allowed to execute concurrently.

        Parameters
        ----------
        server_name : `str`
            The name of the web-application.
        server_port : `str`
            The registered port address of the `prefect` orchestration server.
        root_dir : `str`
            Local directory path of the `prefect` orchestration server data.
        """

        # Define static variable(s)
        self.SERVER_HOST: str = '127.0.0.1'
        self.SERVER_API_ROUTE: str = 'api'
        self.SERVER_API_DOCS: str = 'docs'

        # Assign class variable(s)
        self.SERVER_NAME: str = server_name
        self.SERVER_PORT: str = server_port
        self.SERVER_ROOT_DIR: str = root_dir

    # Define class method(s) for generating API-endpoints
    def api_endpoint(self) -> str:
        """ Returns the `prefect` server REST API endpoint.
        """
        return 'http://%s:%s/%s' % (
            self.SERVER_HOST,
            self.SERVER_PORT,
            self.SERVER_API_ROUTE
        )

    def docs_endpoint(self) -> str:
        """ Returns the `prefect` server REST API documentation endpoint.
        """
        return 'http://%s:%s/%s' % (
            self.SERVER_HOST,
            self.SERVER_PORT,
            self.SERVER_API_DOCS
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
        if not os.path.exists(self.SERVER_ROOT_DIR):
            os.mkdir(self.SERVER_ROOT_DIR)

        # Set environment variables that cannot be configured via the CLI
        os.environ['PREFECT_HOME'] = self.SERVER_ROOT_DIR

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
        subprocess.Popen(
            'prefect server start --host="%s" --port="%s"' % (
                self.SERVER_HOST,
                self.SERVER_PORT
            ),
            shell=True
        )

        # Wait for healthy response
        while not self.health_check():
            time.sleep(1)

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

    def health_check(self) -> requests.Response | bool:
        """ Checks the health of the `prefect` orchestration server.
        Returns `True` when the `prefect` orchestration server is available.
        """
        try:
            return requests.get(self.health_endpoint())
        except requests.exceptions.ConnectionError:
            return False

    def get_token(self) -> requests.Response | None:
        """ Returns a `prefect` orchestration server csrf-token.
        """
        try:
            return requests.get(
                self.token_endpoint(),
                params={'client': self.SERVER_NAME}
            ).json()['token']
        except requests.exceptions.ConnectionError:
            return None

    def get_deployment_id(
        self,
        job_name: str,
        deployment_name: str
    ) -> requests.Response | None:
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
        deployment_version: str,
        **kwargs: dict
    ) -> dict | None:
        """ Creates a `prefect` orchestration server `flow` run from a `deployment`.

        Parameters
        ----------
        name : `str`
            The name of the `prefect` `flow` run.
        job_name : `str`
            The name of the `prefect` `flow`.
        deployment_name : `str`
            The name of the `prefect` `deployment`.
        deployment_version : `str`
            The version of the `prefect` `deployment`.
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
                    'tags': [self.SERVER_NAME, deployment_version],
                    'parameters': kwargs
                },
                headers={
                    'prefect-csrf-token': self.get_token(),
                    'prefect-csrf-client': self.SERVER_NAME,
                }
            ).json()

            return {
                'id': flow_run['id'],
                'state': flow_run['state']['name'],
                'start_time': flow_run['start_time'],
                'end_time': flow_run['end_time'],
                'run_time': flow_run['total_run_time'],
                'parameters': flow_run['parameters'],
                'tags': flow_run['tags'],
                'url': 'http://%s:%s/flow-runs/flow-run/%s' % (
                    self.SERVER_HOST,
                    self.SERVER_PORT,
                    flow_run['id']
                )
            }
        except requests.exceptions.ConnectionError:
            return None

    def poll_job_run(
        self,
        run_id: str
    ) -> dict | None:
        """ Polls the status of a `prefect` orchestration server flow-run.

        Parameters
        ----------
        run_id : `str`
            The id of a `prefect` `flow` run.
        """
        try:
            flow_run = requests.get(self.poll_job_run_endpoint(run_id=run_id)).json()

            return {
                'state': flow_run['state']['name'],
                'end_time': flow_run['end_time'],
                'run_time': flow_run['total_run_time']
            }
        except requests.exceptions.ConnectionError:
            return None
