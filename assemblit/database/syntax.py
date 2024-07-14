"""
Information
---------------------------------------------------------------------
Name        : syntax.py
Location    : ~/database

Description
---------------------------------------------------------------------
Database conflict-clause defaults for sqlite3-databases.
"""

from dataclasses import dataclass
from typing import Any, ClassVar
import datetime
from assemblit.database import adapters


@dataclass
class Conflict():

    rollback: ClassVar[str] = 'ROLLBACK'
    abort: ClassVar[str] = 'ABORT'
    fail: ClassVar[str] = 'FAIL'
    ignore: ClassVar[str] = 'IGNORE'
    replace: ClassVar[str] = 'REPLACE'

    def nullable_clause():
        return 'ON CONFLICT %s' % (Conflict.abort)

    def unique_clause():
        return 'ON CONFLICT %s' % (Conflict.abort)

    def primary_key_clause():
        return 'ON CONFLICT %s' % (Conflict.abort)


@dataclass
class Literal():

    def value(value: Any) -> str:
        if value is None:
            return "'NULL'"
        elif isinstance(value, bool):
            if value:
                return "'TRUE'"
            else:
                return "'FALSE'"
        elif isinstance(value, datetime.datetime):
            return "'%s'" % (adapters.Sqlite.adapt_datetime(value))
        elif isinstance(value, datetime.timedelta):
            return "'%s'" % (adapters.Sqlite.adapt_timedelta(value))
        else:
            return "'%s'" % (value)
