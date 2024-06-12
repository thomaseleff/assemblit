"""
Information
---------------------------------------------------------------------
Name        : syntax.py
Location    : ~/database

Description
---------------------------------------------------------------------
Database conflict-clause defaults for sqlite3-databases.
"""

from typing import Any
import datetime
from assemblit.database import adapters


class Conflict():

    rollback = 'ROLLBACK'
    abort = 'ABORT'
    fail = 'FAIL'
    ignore = 'IGNORE'
    replace = 'REPLACE'

    def nullable_clause():
        return 'ON CONFLICT %s' % (Conflict.abort)

    def unique_clause():
        return 'ON CONFLICT %s' % (Conflict.abort)

    def primary_key_clause():
        return 'ON CONFLICT %s' % (Conflict.abort)


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
