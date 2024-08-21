""" Generic web-application """

import os
from typing import Type, Union, Optional, Any, get_type_hints
from dataclasses import dataclass, field, fields, asdict
from assemblit.toolkit import _exceptions


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

    ASSEMBLIT_CLIENT_PORT : `Optional[int]` = 8501
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
            raise _exceptions.MissingEnvironmentVariables

        # Validate types
        # for variable in fields(self):
        #     if variable.name not in ['ASSEMBLIT_DIR']:
        #         value = getattr(self, variable.name)
        #         if not isinstance(value, variable.type):
        #             raise ValueError(
        #                 'Invalid dtype {%s} for {%s}. Expected {%s}.' % (
        #                     type(value).__name__,
        #                     variable.name,
        #                     (variable.type).__name__
        #                 )
        #             )

        #     # Convert relative directory paths to absoluate paths
        #     if variable.name in ['ASSEMBLIT_DIR']:
        #         setattr(self, variable.name, os.path.abspath(getattr(self, variable.name)))

        # Validate types v2
        type_hints = _env.get_all_type_hints(dataclass_object=type(self))

        # Check the type of field
        for variable in fields(self):
            value = getattr(self, variable.name)
            if not _env.check_type(expected_type=type_hints[variable.name], value=value):
                raise ValueError(
                    'Invalid dtype {%s} for {%s}. Expected {%s}.' % (
                        type(value).__name__,
                        variable.name,
                        (variable.type).__name__
                    )
                )

            # Convert relative directory paths to absoluate paths
            if variable.name in ['ASSEMBLIT_DIR']:
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

    def check_type(expected_type: Type, value: Any) -> bool:
        """ Recursively check if a value matches the expected type. This function is
        compatible with basic types, Union, and Optional.

        Parameters
        ----------
        expected_type : `Type`
            The expected type assigned to the dataclass field.
        value : `Any`
            The value to type check.
        """
        if hasattr(expected_type, '__origin__'):

            # Handle Optional[Type] which is equivalent to Union[Type, None]
            if expected_type.__origin__ is Union:
                return any(_env.check_type(arg, value) for arg in expected_type.__args__)

        # For Optional, allow NoneType
        if isinstance(value, expected_type) or value is None and expected_type is Optional:
            return True

        return isinstance(value, expected_type)

    def get_all_type_hints(dataclass_object: object) -> dict:
        """ Get all type hints from the dataclass and all subclasses.

        Parameters
        ----------
        dataclass_object : `object`
            The dataclass object.
        """
        hints = {}
        for base in dataclass_object.__mro__:
            if base is object:
                continue
            hints.update(get_type_hints(base))
        return hints
