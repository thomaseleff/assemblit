""" Assemblit CLI-tool commands """

import os
from typing import Union, Literal
from assemblit.app import layer


# Define assemblit sub-command function(s)
def run(
    app_type: Literal['aaas', 'wiki'],
    file_path: Union[str, os.PathLike]
):
    """ Runs a Python script.

    Parameters
    ----------
    app_type : `Literal['aaas', 'wiki']
        The type of `assemblit` web-application, either
            - `aaas` for an analytics-as-a-service web-application
            - 'wiki' for a python documentation web-application
    file_path : `str | os.PathLike`
        The relative or absolute path to a local Python script.
    """
    layer.run(
        app_type=app_type,
        file_path=file_path
    )
