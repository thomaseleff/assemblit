"""
Information
---------------------------------------------------------------------
Name        : orchestrators.py
Location    : ~/server
Author      : Tom Eleff
Published   : 2024-05-01
Revised on  : .

Description
---------------------------------------------------------------------
The `class` orchestration server options.
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
        building, observing & reacting to data pipelines efficiently

        The `prefect` orchestrator runs a local server and control panel and automatically
        generates a deployment from the provided `flow` workflow, which is exposed via the
        server API to allow for running, polling and listing `flow` runs. `flow` runs are
        executed via the local server as subprocesses.

        Environment variable options
        ----------------------------

        - `SERVER_TYPE` : `str` = 'prefect' Indicates to use the `prefect` orchestrator.
        - `SERVER_PORT` : `str`             The registered port address of the orchestration server.
                                                Default = '4200'
        - `SERVER_FLOW_ENTRYPOINT` : `str`  The filename of the python executable that contains the definition
                                                of the `prefect` `flow`.
        - `SERVER_FLOW_NAME` : `str`        The name of the `prefect` `flow`.
        - `SERVER_DEPLOYMENT_NAME` : `str`  The name of the `prefect` `deployment`.

        Not implemented,
        - `SERVER_CONCURRENCY` : `int`      The number of `flow` runs that are allowed to execute concurrently.

        Parameters
        ----------
        server_name : `str`
            The name of the web-application.
        server_port : `str`
            The registered port address of the orchestration server.
        root_dir : `str`
            Local directory path of the orchestration server data.
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
    def api_endpoint(self):
        """ Returns the `prefect` server REST API endpoint.
        """
        return 'http://%s:%s/%s' % (
            self.SERVER_HOST,
            self.SERVER_PORT,
            self.SERVER_API_ROUTE
        )

    def docs_endpoint(self):
        """ Returns the `prefect` server REST API documentation endpoint.
        """
        return 'http://%s:%s/%s' % (
            self.SERVER_HOST,
            self.SERVER_PORT,
            self.SERVER_API_DOCS
        )

    def health_endpoint(self):
        """ Returns the `prefect` server health-check REST API endpoint.
        """
        return '/'.join([self.api_endpoint(), 'health'])

    def token_endpoint(self):
        """ Returns the `prefect` server csrf-token REST API endpoint.
        """
        return '/'.join([self.api_endpoint(), 'csrf-token'])

    def deployment_id_endpoint(self, flow_name: str, deployment_name: str):
        """ Returns the `prefect` server deployment-id REST API endpoint.
        """
        print('/'.join([self.api_endpoint(), 'deployments', 'name', flow_name, deployment_name]))
        return '/'.join([self.api_endpoint(), 'deployments', 'name', flow_name, deployment_name])

    def run_workflow_endpoint(self, deployment_id: str):
        """ Returns the `prefect` server run-flow REST API endpoint.
        """
        return '/'.join([self.api_endpoint(), 'deployments', deployment_id, 'create_flow_run'])

    def poll_workflow_endpoint(self, run_id: str):
        """ Returns the `prefect` server flow-status REST API endpoint.
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
        (output, err) = configure.communicate()

        # Status
        start_status = configure.wait()

        return start_status

    # Define class method(s) for executing commands
    def start(self) -> str:
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

    def deploy(self, workflow_entrypoint: str) -> str:
        """ Deploys the `prefect` orchestration server workflow.
        """
        return subprocess.Popen(
            '"%s" "%s"' % (sys.executable, workflow_entrypoint),
            shell=True
        )

    def health_check(self) -> str:
        """ Checks the health of the `prefect` orchestration server.
        """
        try:
            return requests.get(self.health_endpoint())
        except requests.exceptions.ConnectionError:
            return False

    def set_token(self) -> dict:
        """ Returns the `prefect` orchestration server csrf-token.
        """
        return requests.get(
            self.token_endpoint(),
            params={'client': self.SERVER_NAME}
        ).json()

    def set_deployment_id(self, flow_name: str, deployment_name: str) -> str:
        """ Returns the `prefect` orchestration server id of the requested deployment.
        """
        return requests.get(
            self.deployment_id_endpoint(
                flow_name=flow_name,
                deployment_name=deployment_name
            )
        ).json()['id']

    def run_workflow(self, workflow_id: str, deployment_id: str, deployment_version: str, **kwargs: dict) -> dict:
        """ Creates a `prefect` orchestration server flow-run from a deployment.

        Parameters
        ----------
        workflow_id : `str`
            The id of the workflow run.
        deployment_id : `str`
            The id of the deployment.
        """
        return requests.post(
            self.run_workflow_endpoint(deployment_id=deployment_id),
            json={
                'name': workflow_id,
                'tags': [self.SERVER_NAME, deployment_version],
                'parameters': kwargs
            },
            headers={
                'prefect-csrf-token': self.set_token()['token'],
                'prefect-csrf-client': self.SERVER_NAME,
            }
        ).json()

    def poll_workflow(self, run_id: str) -> dict:
        """ Polls the status of a `prefect` orchestration server flow-run.

        Parameters
        ----------
        run_id : `str`
            The id of the flow-run.
        """
        return requests.get(self.poll_workflow_endpoint(run_id=run_id)).json()
