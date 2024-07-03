"""
Information
---------------------------------------------------------------------
Name        : data.py
Location    : ~/database

Description
---------------------------------------------------------------------
Database schema and connection `class` objects for retrieving
information from the `data` sqlite3-database.
"""

from dataclasses import dataclass
import pandera
import datetime
from assemblit import setup
from assemblit.database import generic


# Define the `data` database table schemas
@dataclass
class Schemas():

    # The `data` table Schema.
    data: generic.Schema = generic.Schema(
        name=setup.DATA_DB_NAME,
        columns={
            setup.DATA_DB_QUERY_INDEX: pandera.Column(
                str,
                nullable=False,
                unique=True,
                metadata={'primary_key': True}
            ),
            'uploaded_by': pandera.Column(
                str,
                nullable=False,
                unique=False
            ),
            'created_on': pandera.Column(
                datetime.datetime,
                nullable=False,
                unique=False
            ),
            'final': pandera.Column(
                bool,
                nullable=False,
                unique=False
            ),
            'version': pandera.Column(
                int,
                nullable=False,
                unique=False
            ),
            'file_name': pandera.Column(
                str,
                nullable=False,
                unique=False
            ),
            'dbms': pandera.Column(
                str,
                nullable=False,
                unique=False
            ),
            'datetime': pandera.Column(
                str,
                nullable=False,
                unique=False
            ),
            'dimensions': pandera.Column(
                str,
                nullable=False,
                unique=False
            ),
            'metrics': pandera.Column(
                str,
                nullable=False,
                unique=False
            ),
            'selected_datetime': pandera.Column(
                str,
                nullable=False,
                unique=False
            ),
            'selected_dimensions': pandera.Column(
                str,
                nullable=False,
                unique=False
            ),
            'selected_metrics': pandera.Column(
                str,
                nullable=False,
                unique=False
            ),
            'selected_aggrules': pandera.Column(
                str,
                nullable=False,
                unique=False
            ),
            'size_mb': pandera.Column(
                float,
                nullable=False,
                unique=False
            ),
            'sha256': pandera.Column(
                str,
                nullable=False,
                unique=False
            )
        }
    )


# Define the `data` database connection
class Connection(generic.Connection):

    def __init__(
        self
    ):
        """ The `data` sqlite3-database Connection.
        """
        super().__init__(
            db_name=setup.DATA_DB_NAME,
            dir_name=setup.DB_DIR
        )
