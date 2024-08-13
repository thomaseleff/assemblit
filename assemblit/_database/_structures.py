""" Data objects for database queries """

from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar


# Define database management system options
@dataclass
class DBMS():
    """ A `class` that contains the default database management system options.

    Attributes
    ----------
    OPTIONS : `list[str]`
        The list of possible database management systems,
            `[
                'db',
                'sdb',
                'sqlite',
                'db3',
                's3db',
                'sqlite3',
                'sl3'
            ]`
    DEFAULT : `str`
        The default database management system, `db`.
    """

    OPTIONS: ClassVar[list[str]] = [
        'db',
        'sdb',
        'sqlite',
        'db3',
        's3db',
        'sqlite3',
        'sl3'
    ]
    DEFAULT: ClassVar[str] = 'db'


# Define database operators
@dataclass
class Filter():
    """ A `class` that represents database query filter parameters.

    Attributes
    ----------
    col : `str | list[str]`
        The column(s) of the database table to filter.
    val : `str | list[str]`
        The value(s) of the database table to filter.
    """

    col: str | list[str] | None = None
    val: str | list[str] | None = None


@dataclass
class Validate(Filter):
    """ A `class` that represents database query validation parameters.

    Attributes
    ----------
    col : `str | list[str]`
        The column(s) of the database table to validate.
    val : `str | list[str]`
        The value(s) of the database table to validate.
    """
    pass


# Define database structures
@dataclass
class Value(Filter):
    """ A `class` that represents database query value parameters.

    Attributes
    ----------
    col : `str | list[str]`
        The column of the database table.
    val : `str | list[str]`
        The value of the database table.
    """
    pass


@dataclass
class Row():
    """ A `class` that contains a database table row.

    Attributes
    ----------
    cols : `list[str]`
        The columns of the database table row.
    vals : `list[str]`
        The values of the database table row.
    """

    cols: list[str] | None = None
    vals: list[str] | None = None


@dataclass
class Table():
    """ A `class` that represents a database table view.

    Attributes
    ----------
    table_name : `str`
        The name of the database table.
    filtr : `assemblit.database._structures.Filter`
        The database table filter to produce the database table view.
    """

    table_name: str | None = None
    filtr: Filter | None = None
