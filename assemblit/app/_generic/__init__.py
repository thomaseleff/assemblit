""" Generic web-application """

import os
from typing import Union, Optional
from dataclasses import dataclass, field, fields, asdict
from assemblit.app.layer import MissingEnvironmentVariables


@dataclass
class _env():
    """ A `class` that represents the generic web-application environment variables.

    Attributes
    ----------
    ASSEMBLIT_ENV : `str`
        The environment name, typically "PROD" or "DEV".

    ASSEMBLIT_VERSION : `str`
        The version, like "v{major}.{minor}.{fix}" of the web-application.

    ASSEMBLIT_DEBUG : `bool`
        `True` or `False`, whether to print the contents of `streamlit.session_state` on
            each page re-load.

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
    """

    # [required]

    # Developer configuration settings
    ASSEMBLIT_ENV: str = field(default=None)
    ASSEMBLIT_VERSION: str = field(default=None)
    ASSEMBLIT_DEBUG: bool = field(default=None)

    # Web-app configuration settings
    ASSEMBLIT_NAME: str = field(default=None)
    ASSEMBLIT_HOME_PAGE_NAME:  str = field(default=None)
    ASSEMBLIT_GITHUB_REPOSITORY_URL: str = field(default=None)
    ASSEMBLIT_GITHUB_BRANCH_NAME: str = field(default=None)
    ASSEMBLIT_DIR: Union[str, os.PathLike] = field(default=None)

    # [optional]

    # Port configuration settings
    ASSEMBLIT_CLIENT_PORT: Optional[int] = field(default=8501)

    def __post_init__(self):
        """ Validates the environment variables. Raises a `MissingEnvironmentVariables` exception
        if environment variables are set to `None`. Raises a `ValueError` exception if the
        environment variable type is invalid.
        """

        # Validate environment variables
        missing_variables = [name for name, value in self.__dict__.items() if value is None]
        if missing_variables:
            raise MissingEnvironmentVariables

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

    def to_dict(self) -> dict:
        """ Returns the environment variables and values as a dictionary. """
        return asdict(self)

    def list_variables(self) -> list:
        """ Returns the environment variable names as a list. """
        return list(asdict(self).keys())

    def values(self) -> tuple:
        """ Returns the environment variable values as a tuple. """
        return tuple(asdict(self).values())
