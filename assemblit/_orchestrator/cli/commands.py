""" Workflow orchestration commands """

import os
from typing import Union
from assemblit._orchestrator import layer


# Define server sub-command function(s)
def start(
    path: Union[str, os.PathLike]
):
    """ Starts the orchestration server.

    Parameters
    ----------
    path : `str | os.PathLike`
        The relative or absolute path to the current work-directory.

    Help
    ----
    usage: orchestrator start [-h] path

    positional arguments:
    path        The relative or absolute path to the
                current work-directory.

    options:
    -h, --help  show this help message and exit

    Execute `orchestrator start --help` for help.

    Examples
    --------
    ``` console
    orchestrator start .
    ```

    """

    # Start the orchestration server
    layer.start(path=path)
