""" Assemblit commands """

import os
from typing import Union
from assemblit.app import layer


# Define assemblit sub-command function(s)
def run(
    script: Union[str, os.PathLike]
):
    """ Runs a Python script.

    Parameters
    ----------
    script : `str | os.PathLike`
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
