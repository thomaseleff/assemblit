"""
Information
---------------------------------------------------------------------
Name        : sessions.py
Location    : ~/database

Description
---------------------------------------------------------------------
Database schema and connection `class` objects for retrieving
information from the `sessions` sqlite3-database.
"""

from dataclasses import dataclass
import pandera
from assemblit import setup
from assemblit.database import generic


# Define the `sessions` database table schemas
@dataclass
class Schemas():

    # The `data` table Schema
    data: generic.Schema = generic.Schema(
        name=setup.DATA_DB_NAME,
        columns={
            setup.SESSIONS_DB_QUERY_INDEX: pandera.Column(
                str,
                nullable=False,
                unique=False,
                metadata={'primary_key': True}
            ),
            setup.DATA_DB_QUERY_INDEX: pandera.Column(
                str,
                nullable=False,
                unique=False,
                metadata={'primary_key': True}
            )
        }
    )

    # The `analysis` table Schema
    analysis: generic.Schema = generic.Schema(
        name=setup.ANALYSIS_DB_NAME,
        columns={
            setup.SESSIONS_DB_QUERY_INDEX: pandera.Column(
                str,
                nullable=False,
                unique=False,
                metadata={'primary_key': True}
            ),
            setup.ANALYSIS_DB_QUERY_INDEX: pandera.Column(
                str,
                nullable=False,
                unique=False,
                metadata={'primary_key': True}
            )
        }
    )


# Define the `sessions` database connection
class Connection(generic.Connection):

    def __init__(
        self
    ):
        """ The `sessions` sqlite3-database Connection.
        """
        super().__init__(
            db_name=setup.SESSIONS_DB_NAME,
            dir_name=setup.DB_DIR
        )
