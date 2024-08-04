""" Analytics-as-a-service web-application """

from typing import Optional
from dataclasses import dataclass, field
from assemblit.app import _generic


@dataclass
class env(_generic._env):
    """ A `class` that represents the analytics-as-service (AaaS) web-application environment variables.

    Attributes
    ----------
    ASSEMBLIT_ENV : `str`
        The environment name, typically "PROD" or "DEV".

    ASSEMBLIT_VERSION : `str`
        The version, like "v{major}.{minor}.{fix}" of the web-application.

    ASSEMBLIT_DEBUG : `bool`
        `True` or `False`, whether to print the contents of `streamlit.session_state` on
            each page re-load.

    ASSEMBLIT_REQUIRE_AUTHENTICATION : `bool`
        `True` or `False`, whether to require user-authentication in order to
            access the web-application.

    ASSEMBLIT_NAME : `str`
        The name of the web-application. All `streamlit.session_state` parameters created
            within the scope of the web-application will be contained within a key named
            after this environment variable.

    ASSEMBLIT_HOME_PAGE_NAME : `str`
        The filename of the Python script that represents the home-page.

    ASSEMBLIT_GITHUB_REPOSITORY_URL : `str`
        The Github URL of the repository to deploy as the web-application.

    ASSEMBLIT_GITHUB_BRANCH_NAME : `str`
        The Github branch name to deploy.

    ASSEMBLIT_DIR : `Union[str, os.PathLike]`
        The local filesystem folder to mount to the docker container.

    ASSEMBLIT_CLIENT_PORT : Optional[`int`] = 8501
        The client port of the `assemblit` web-application within the docker container.

    ASSEMBLIT_SERVER_PORT : Optional[`int`] = 4200
        The server port of the orchestration server within the docker container.

    ASSEMBLIT_SERVER_JOB_NAME : `str`
        The name of the job.

    ASSEMBLIT_SERVER_JOB_ENTRYPOINT : `str`
        The Python entrypoint of the job.

    ASSEMBLIT_SERVER_DEPLOYMENT_NAME : `str`
        The name of the job-deployment.

    ASSEMBLIT_USERS_DB_NAME : Optional[`str`] = "users"
        The name of the users-database.

    ASSEMBLIT_USERS_DB_QUERY_INDEX : Optional[`str`] = "user_id"
        The name of the query-index of the users-database.

    ASSEMBLIT_SESSIONS_DB_NAME : Optional[`str`] = "sessions"
        The name of the sessions-database.

    ASSEMBLIT_SESSIONS_DB_QUERY_INDEX : Optional[`str`] = "session_id"
        The name of the query-index of the sessions-database.

    ASSEMBLIT_DATA_DB_NAME : Optional[`str`] = "data"
        The name of the data-database.

    ASSEMBLIT_DATA_DB_QUERY_INDEX : Optional[`str`] = "dataset_id"
        The name of the query-index of the data-database.

    ASSEMBLIT_ANALYSIS_DB_NAME : Optional[`str`] = "analysis"
        The name of the analysis-database.

    ASSEMBLIT_ANALYSIS_DB_QUERY_INDEX : Optional[`str`] = "run_id"
        The name of the query-index of the analysis-database.
    """

    # [required]

    # Authentication settings
    ASSEMBLIT_REQUIRE_AUTHENTICATION: bool = field(default=None)

    # Orchestration server configuration settings
    ASSEMBLIT_SERVER_JOB_NAME: str = field(default=None)
    ASSEMBLIT_SERVER_JOB_ENTRYPOINT: str = field(default=None)
    ASSEMBLIT_SERVER_DEPLOYMENT_NAME: str = field(default=None)

    # [optional]

    # Orchestration server configuration settings
    ASSEMBLIT_SERVER_TYPE: Optional[str] = field(default="prefect", init=False)

    # Add'l Port configuration settings
    ASSEMBLIT_SERVER_PORT: Optional[int] = field(default=4200)

    # Users db settings
    ASSEMBLIT_USERS_DB_NAME: Optional[str] = field(default="users")
    ASSEMBLIT_USERS_DB_QUERY_INDEX: Optional[str] = field(default="user_id")

    # Sessions db settings
    ASSEMBLIT_SESSIONS_DB_NAME: Optional[str] = field(default="sessions")
    ASSEMBLIT_SESSIONS_DB_QUERY_INDEX: Optional[str] = field(default="session_id")

    # Data db settings
    ASSEMBLIT_DATA_DB_NAME: Optional[str] = field(default="data")
    ASSEMBLIT_DATA_DB_QUERY_INDEX: Optional[str] = field(default="dataset_id")

    # Analysis db settings
    ASSEMBLIT_ANALYSIS_DB_NAME: Optional[str] = field(default="analysis")
    ASSEMBLIT_ANALYSIS_DB_QUERY_INDEX: Optional[str] = field(default="run_id")
