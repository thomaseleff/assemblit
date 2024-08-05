""" Workflow orchestration commands """

import os
from typing import Union
from assemblit.server import layer


# Define server sub-command function(s)
def start(
    path: Union[str, os.PathLike]
):
    """ Starts the orchestration server.

    Parameters
    ----------
    path : `str | os.PathLike`
        The relative or absolute path to the current work-directory.
    """

    # Start the orchestration server
    layer.start(path=path)
