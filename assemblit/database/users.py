"""
Information
---------------------------------------------------------------------
Name        : users.py
Location    : ~/database

Description
---------------------------------------------------------------------
Database schema and connection `class` objects for retrieving
information from the `users` sqlite3-database.
"""

from dataclasses import dataclass
import pandera
from assemblit import setup
from assemblit.database import generic


# Define the `users` database table schemas
@dataclass
class Schemas():

    # The `credentials` table Schema.
    credentials: generic.Schema = generic.Schema(
        name='credentials',
        columns={
            setup.USERS_DB_QUERY_INDEX: pandera.Column(
                str,
                nullable=False,
                unique=True,
                metadata={'primary_key': True}
            ),
            'username': pandera.Column(
                str,
                nullable=False,
                unique=True
            ),
            'password': pandera.Column(
                str,
                nullable=False,
                unique=True
            ),
            'first_name': pandera.Column(
                str,
                nullable=False,
                unique=False
            )
        }
    )

    # The `sessions` table Schema
    sessions: generic.Schema = generic.Schema(
        name=setup.SESSIONS_DB_NAME,
        columns={
            setup.USERS_DB_QUERY_INDEX: pandera.Column(
                str,
                nullable=False,
                unique=False,
                metadata={'primary_key': True}
            ),
            setup.SESSIONS_DB_QUERY_INDEX: pandera.Column(
                str,
                nullable=False,
                unique=False,
                metadata={'primary_key': True}
            )
        }
    )


# Define the `users` database connection
class Connection(generic.Connection):

    def __init__(
        self
    ):
        """ The `users` sqlite3-database Connection.
        """
        super().__init__(
            db_name=setup.USERS_DB_NAME,
            dir_name=setup.DB_DIR
        )
