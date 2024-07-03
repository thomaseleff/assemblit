"""
Information
---------------------------------------------------------------------
Name        : structures.py
Location    : ~/database

Description
---------------------------------------------------------------------
Data object structures for retrieving information from
sqlite3-databases.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar


# Define database management system options
@dataclass
class DBMS():
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
    col: str | list[str] | None = None
    val: str | list[str] | None = None


@dataclass
class Validate(Filter):
    pass


# Define database structures
@dataclass
class Values(Filter):
    pass


@dataclass
class Table():
    table_name: str | None = None
    filtr: Filter | None = None
