""" Web content import utility """

import os
import re
import textwrap
from typing import Union


def clean_text(
    text: str
):
    """ Removes leading whitespace from each line of `text` and any extra
    whitespace from the start and end of `text` while preserving intentional
    return characters `\\n`.

    Parameters
    ----------
    text : `str`
        The text to clean.
    """

    # Dedent
    dedented = textwrap.dedent(str(text)).strip()

    # If '\n' appears once not in any sequence (e.g. an isolated, single-return)
    #   then replace '\n' with a single-space
    replaced = re.sub(r'(?<!\n)\n(?!\n)', ' ', dedented)

    # If '\n' appears in any sequence of multiple returns,
    #   then reduce the sequence of returns by one
    reduced = re.sub(r'\n{2,}', lambda m: '\n' * (len(m.group(0)) - 1), replaced)

    # Remove whitespace
    lines = [line.strip().replace('  ', ' ') for line in reduced.splitlines()]

    # Preserve intentional newlines
    return '\n'.join(lines)


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
        file.write(textwrap.dedent(content))
