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
import datetime
import pandera
import numpy as np


class DATATYPE():

    kinds: list[str] = []
    built_in: type = None
    sqlite: str = 'NULL'

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


class BLOB(DATATYPE):

    kinds: list[str] = [
        'V',    # Void
    ]
    built_in: type = None
    sqlite: str = 'BLOB'

    def check(kind: str):
        return True if kind in __class__.kinds else False


class INTEGER(DATATYPE):

    kinds: list[str] = [
        'i',    # Integer
        'u'     # Unsigned integer
    ]
    built_in: type = int
    sqlite: str = 'INTEGER'

    def check(kind: str):
        return True if kind in __class__.kinds else False


class REAL(DATATYPE):

    kinds: list[str] = [
        'f',     # Float
        'c',     # Complex float
    ]
    built_in: type = float
    sqlite: str = 'FLOAT'

    def check(kind: str):
        return True if kind in __class__.kinds else False


class TEXT(DATATYPE):

    kinds: list[str] = [
        'b',    # Boolean
        'O',    # Object
        'S',    # String
        'U',    # Unicode string
    ]
    built_in: type = str
    sqlite: str = 'TEXT'

    def check(kind: str):
        return True if kind in __class__.kinds else False


class DATETIME(DATATYPE):

    kinds: list[str] = [
        'M'     # Datetime
    ]
    built_in: type = datetime.datetime
    sqlite: str = 'DATETIME'

    def check(kind: str):
        return True if kind in __class__.kinds else False


class TIMEDELTA(DATATYPE):

    kinds: list[str] = [
        'm'     # Timedelta
    ]
    built_in: type = datetime.timedelta
    sqlite: str = 'TIMEDELTA'

    def check(kind: str):
        return True if kind in __class__.kinds else False


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
