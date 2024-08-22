""" Data objects for database queries """

from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, List, Union


# Define database management system options
@dataclass
class DBMS():
    """ A `class` that contains the default database management system options.

    Attributes
    ----------
    OPTIONS : `List[str]`
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

    OPTIONS: ClassVar[List[str]] = [
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
    col : `Union[str, List[str], None]`
        The column(s) of the database table to filter.
    val : `Union[str, List[str], None]`
        The value(s) of the database table to filter.
    """

    col: Union[str, List[str], None] = None
    val: Union[str, List[str], None] = None


@dataclass
class Validate(Filter):
    """ A `class` that represents database query validation parameters.

    Attributes
    ----------
    col : `Union[str, List[str], None]`
        The column(s) of the database table to validate.
    val : `Union[str, List[str], None]`
        The value(s) of the database table to validate.
    """
    pass


# Define database structures
@dataclass
class Value(Filter):
    """ A `class` that represents database query value parameters.

    Attributes
    ----------
    col : `Union[str, List[str], None]`
        The column of the database table.
    val : `Union[str, List[str], None]`
        The value of the database table.
    """
    pass


@dataclass
class Row():
    """ A `class` that contains a database table row.

    Attributes
    ----------
    cols : `Union[List[str], None]`
        The columns of the database table row.
    vals : `Union[List[str], None]`
        The values of the database table row.
    """

    cols: Union[List[str], None] = None
    vals: Union[List[str], None] = None


@dataclass
class Table():
    """ A `class` that represents a database table view.

    Attributes
    ----------
    table_name : `Union[str, None]`
        The name of the database table.
    filtr : `Union[assemblit.database._structures.Filter, None]`
        The database table filter to produce the database table view.
    """

    table_name: Union[str, None] = None
    filtr: Union[Filter, None] = None
