"""
Information
---------------------------------------------------------------------
Name        : datatypes.py
Location    : ~/database

Description
---------------------------------------------------------------------
Database datatypes and methods for parsing datatypes from schema-objects
for sqlite3-databases.

Supported dataframe schema-objects,
    - `pandera.DataFrameSchema`
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar
import datetime
import pandera
import numpy as np


@dataclass
class DATATYPE():

    kinds: ClassVar[list[str]] = []
    built_in: ClassVar[type] = None
    sqlite: ClassVar[str] = 'NULL'

    def __repr__(self) -> str:
        if self.built_in:
            return '%s' % (self.built_in.__name__)
        else:
            return 'None'

    def __name__(self) -> str:
        return '%s' % (self.sqlite)

    def to_sqlite(self) -> str:
        return '%s' % (self.__name__())

    def to_built_in(self) -> str:
        return self.built_in


@dataclass
class BLOB(DATATYPE):

    kinds: ClassVar[list[str]] = [
        'V',    # Void
    ]
    built_in: ClassVar[type] = None
    sqlite: ClassVar[str] = 'BLOB'

    def check(kind: str):
        return True if kind in BLOB.kinds else False


@dataclass
class INTEGER(DATATYPE):

    kinds: ClassVar[list[str]] = [
        'i',    # Integer
        'u'     # Unsigned integer
    ]
    built_in: ClassVar[type] = int
    sqlite: ClassVar[str] = 'INTEGER'

    def check(kind: str):
        return True if kind in INTEGER.kinds else False


@dataclass
class REAL(DATATYPE):

    kinds: ClassVar[list[str]] = [
        'f',     # Float
        'c',     # Complex float
    ]
    built_in: ClassVar[type] = float
    sqlite: ClassVar[str] = 'FLOAT'

    def check(kind: str):
        return True if kind in REAL.kinds else False


@dataclass
class TEXT(DATATYPE):

    kinds: ClassVar[list[str]] = [
        'b',    # Boolean
        'O',    # Object
        'S',    # String
        'U',    # Unicode string
    ]
    built_in: ClassVar[type] = str
    sqlite: ClassVar[str] = 'TEXT'

    def check(kind: str):
        return True if kind in TEXT.kinds else False


@dataclass
class DATETIME(DATATYPE):

    kinds: ClassVar[list[str]] = [
        'M'     # Datetime
    ]
    built_in: ClassVar[type] = datetime.datetime
    sqlite: ClassVar[str] = 'DATETIME'

    def check(kind: str):
        return True if kind in DATETIME.kinds else False


@dataclass
class TIMEDELTA(DATATYPE):

    kinds: ClassVar[list[str]] = [
        'm'     # Timedelta
    ]
    built_in: ClassVar[type] = datetime.timedelta
    sqlite: ClassVar[str] = 'TIMEDELTA'

    def check(kind: str):
        return True if kind in TIMEDELTA.kinds else False


def from_pandera(datatype: pandera.DataType) -> DATATYPE:
    if BLOB.check(np.dtype(datatype.type).kind):
        return BLOB()
    elif INTEGER.check(np.dtype(datatype.type).kind):
        return INTEGER()
    elif REAL.check(np.dtype(datatype.type).kind):
        return REAL()
    elif TEXT.check(np.dtype(datatype.type).kind):
        return TEXT()
    elif DATETIME.check(np.dtype(datatype.type).kind):
        return DATETIME()
    elif TIMEDELTA.check(np.dtype(datatype.type).kind):
        return TIMEDELTA()
    else:
        raise UnsupportedTypeError(
            "Datatype {kind: '%s', dtype: '%s'} is not recognized." % (
                np.dtype(datatype.type).kind,
                np.dtype(datatype.type)
            )
        )


# Define exceptions
class UnsupportedTypeError(Exception):
    pass
