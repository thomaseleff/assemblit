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
    return _from_text_content(file_path=file_path)


def to_markdown(
    file_path: Union[str, os.PathLike],
    content: str
):
    """ Writes content to `file_path`.

    Parameters
    ----------
    file_path : `str | os.PathLike`
        The relative or absolute path to a markdown document.
    content : `str`
        The markdown text content.
    """
    return _to_text_content(file_path=file_path, content=content)


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

    with open(os.path.abspath(file_path), 'r', encoding='utf-8') as file:
        return file.read()


def _to_text_content(
    file_path: Union[str, os.PathLike],
    content: str
):
    """ Writes content to `file_path`.

    Parameters
    ----------
    file_path : `str | os.PathLike`
        The relative or absolute path to a text document.
    content : `str`
        The markdown text content.
    """
    with open(os.path.abspath(file_path), 'w', encoding='utf-8') as file:
        file.write(content)
