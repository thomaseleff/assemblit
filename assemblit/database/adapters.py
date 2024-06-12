"""
Information
---------------------------------------------------------------------
Name        : adapters.py
Location    : ~/database

Description
---------------------------------------------------------------------
Database datatype adapters and converters for sqlite3-databases.
"""

import sqlite3
import datetime


# Define sqlite datatype adapter(s) and converter(s)
class Sqlite():

    # Datetime
    def adapt_datetime(dt: datetime.datetime):
        """ Adapts `datetime.datetime` as a `str`.

        Parameters
        ----------
        dt : `datetime.datetime`
            Datetime object.
        """
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def convert_datetime(object: bytes):
        """ Converts a sqlite value stored as `str` to 'datetime.datetime`.

        Parameters
        ----------
        object : `bytes`
            Represents a bytes encoded `str`.
        """
        return datetime.datetime.strptime(object.decode(), "%Y-%m-%d %H:%M:%S")

    # Timedelta
    def adapt_timedelta(td: datetime.timedelta):
        """ Adapts `datetime.timedelta` as a `str`.

        Parameters
        ----------
        td : `datetime.timedelta`
            Timedelta object.
        """
        return td.total_seconds()

    def convert_timedelta(object: bytes):
        """ Converts a sqlite value stored as `str` to 'datetime.timedelta`.

        Parameters
        ----------
        object : `bytes`
            Represents a bytes encoded `str`.
        """
        return datetime.timedelta(seconds=float(object.decode()))

    def register():
        """ Registers all object adapters and converters.
        """

        # Register datetime
        sqlite3.register_adapter(datetime.datetime, Sqlite.adapt_datetime)
        sqlite3.register_converter('DATETIME', Sqlite.convert_datetime)

        # Register timedelta
        sqlite3.register_adapter(datetime.timedelta, Sqlite.adapt_timedelta)
        sqlite3.register_converter('TIMEDELTA', Sqlite.convert_timedelta)
