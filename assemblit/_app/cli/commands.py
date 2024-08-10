""" Assemblit commands """

import os
from typing import Union, Literal
from assemblit._app import layer


# Define assemblit sub-command function(s)
def run(
    script: Union[str, os.PathLike]
):
    """ Runs a Python script.

    Parameters
    ----------
    script : `str` | `os.PathLike`
        The relative or absolute path to a local Python script.

    Help
    ----
    usage: assemblit run [-h] script

    positional arguments:
    script      The relative or absolute path to a local Python script.

    options:
    -h, --help  show this help message and exit

    Execute `assemblit run --help` for help.

    Examples
    --------
    ``` console
    assemblit run app.py
    ```

    """
    layer.run(script=script)


def build(
    app_type: Literal['demo']
):
    """ Builds a new project.

    Parameters
    ----------
    app_type : `Literal['demo']`
        The type of web-application.

    Help
    ----
    usage: assemblit build [-h] {demo}

    positional arguments:
    app_type {demo}      The type of web-application.

    options:
    -h, --help  show this help message and exit

    Execute `assemblit build --help` for help.

    Examples
    --------
    ``` console
    assemblit build demo
    ```
    """
    layer.build(app_type=app_type)
