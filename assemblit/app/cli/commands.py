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
    """
    layer.run(script=script)
