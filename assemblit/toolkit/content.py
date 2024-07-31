""" Web content import utility """

import os
from typing import Union


def from_markdown(
    file_path: Union[str, os.PathLike]
):
    """ Reads the contents of `file_path` and returns the contents as a `str`.

    Parameters
    ----------
    file_path : `str | os.PathLike`
        The relative or absolute path to a markdown document.
    """
    return _from_text_content(file_path)


# def from_html(
#     file_path: Union[str, os.PathLike]
# ):
#     """ Reads the contents of `file_path` and returns the contents as a `str`.

#     Parameters
#     ----------
#     file_path : `str | os.PathLike`
#         The relative or absolute path to an html document.
#     """
#     return _from_text_content(file_path)


def _from_text_content(
    file_path: Union[str, os.PathLike]
):
    """ Reads the contents of `file_path` and returns the contents as a `str`.

    Parameters
    ----------
    file_path : `str | os.PathLike`
        The relative or absolute path to a text document.
    """
    if not os.path.isfile(os.path.abspath(file_path)):
        raise FileNotFoundError('{%s} does not exist.' % os.path.abspath(file_path))

    with open(os.path.abspath(file_path), 'r', encoding='utf-8') as text_content:
        return text_content.read()
