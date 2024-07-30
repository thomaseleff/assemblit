""" Assemblit Web-application options """

from __future__ import annotations
import os
from typing import Union, ClassVar
from dataclasses import dataclass, asdict


@dataclass
class AAAS():
    """ A `class` that represents an analytics-as-service (AaaS) web-application.

    Attributes
    ----------
    ASSEMBLIT.ENV : `str`
        The environment, typically "PROD" or "DEV".

    ASSEMBLIT.VERSION : `str`
        The version, like "v{major}.{minor}.{fix}" of the web-application.

    ASSEMBLIT.DEBUG : `bool`
        `True` or `False`, whether to print the contents of `streamlit.session_state` on
            each page re-load.

    ASSEMBLIT.REQUIRE_AUTHENTICATION : `bool`
        `True` or `False`, whether to require user-authentication in order to
            access the web-application.

    ASSEMBLIT.NAME : `str`
        The name of the web-application. All `streamlit.session_state` parameters created
            within the scope of the web-application will be contained within a key named
            after this environment variable.

    ASSEMBLIT.HOME_PAGE_NAME : `str`
        The filename of the Python script that represents the home-page.

    ASSEMBLIT.GITHUB_REPOSITORY_URL : `str`
        The Github URL of the repository to deploy as the web-application.

    ASSEMBLIT.GITHUB_BRANCH_NAME : `str`
        The Github branch name to deploy.

    ASSEMBLIT.DIR : `Union[str, os.PathLike]`
        The local filesystem folder to mount to the docker container.

    ASSEMBLIT.CLIENT_PORT : `int` = 8501
        The client port of the `assemblit` web-application within the docker container.

    ASSEMBLIT.SERVER_PORT : `int` = 4200
        The server port of the orchestration server within the docker container.

    ASSEMBLIT.SERVER_TYPE : ClassVar[`str`] = "prefect"
        Indicates to use the `prefect` orchestrator.

    ASSEMBLIT.SERVER_JOB_NAME : `str`
        The name of the job.

    ASSEMBLIT.SERVER_JOB_ENTRYPOINT : `str`
        The Python entrypoint of the job.

    ASSEMBLIT.SERVER_DEPLOYMENT_NAME : `str`
        The name of the job-deployment.

    ASSEMBLIT.USERS_DB_NAME : `str` = "users"
        The name of the users-database.

    ASSEMBLIT.USERS_DB_QUERY_INDEX : `str` = "user_id"
        The name of the query-index of the users-database.

    ASSEMBLIT.SESSIONS_DB_NAME : `str` = "sessions"
        The name of the sessions-database.

    ASSEMBLIT.SESSIONS_DB_QUERY_INDEX : `str` = "session_id"
        The name of the query-index of the sessions-database.

    ASSEMBLIT.DATA_DB_NAME : `str` = "data"
        The name of the data-database.

    ASSEMBLIT.DATA_DB_QUERY_INDEX : `str` = "dataset_id"
        The name of the query-index of the data-database.

    ASSEMBLIT.ANALYSIS_DB_NAME : `str` = "analysis"
        The name of the analysis-database.

    ASSEMBLIT.ANALYSIS_DB_QUERY_INDEX : `str` = "run_id"
        The name of the query-index of the analysis-database.

    """

    # Developer configuration settings
    ENV: str
    VERSION: str
    DEBUG: bool

    # Web-app configuration settings
    NAME: str
    HOME_PAGE_NAME:  str
    GITHUB_REPOSITORY_URL: str
    GITHUB_BRANCH_NAME: str
    DIR: Union[str, os.PathLike]

    # Authentication settings
    REQUIRE_AUTHENTICATION: bool

    # Orchestration server configuration settings
    SERVER_TYPE: ClassVar[str] = "prefect"
    SERVER_JOB_NAME: str
    SERVER_JOB_ENTRYPOINT: str
    SERVER_DEPLOYMENT_NAME: str

    # Port configuration settings
    CLIENT_PORT: int = 8501
    SERVER_PORT: int = 4200

    # Users db settings
    USERS_DB_NAME: ClassVar[str] = "users"
    USERS_DB_QUERY_INDEX: ClassVar[str] = "user_id"

    # Sessions db settings
    SESSIONS_DB_NAME: ClassVar[str] = "sessions"
    SESSIONS_DB_QUERY_INDEX: ClassVar[str] = "session_id"

    # Data db settings
    DATA_DB_NAME: ClassVar[str] = "data"
    DATA_DB_QUERY_INDEX: ClassVar[str] = "dataset_id"

    # Analysis db settings
    ANALYSIS_DB_NAME: ClassVar[str] = "analysis"
    ANALYSIS_DB_QUERY_INDEX: ClassVar[str] = "run_id"

    def to_dict(self) -> dict:
        """ Returns the `class` attributes as a dictionary. """
        return asdict(self)
