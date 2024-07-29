""" Database table """

from dataclasses import dataclass
import pandera
import datetime
from assemblit import setup
from assemblit.database import _generic


# Define the `analysis` database table schemas
@dataclass
class Schemas():
    """ A `class` that represents the `analysis` database schemas.

    Attributes
    ----------
    analysis : `assemblit.database._generic.Schema`
        The `analysis.analysis` database table schema.
    """

    # The `analysis` table Schema
    analysis: _generic.Schema = _generic.Schema(
        name=setup.ANALYSIS_DB_NAME,
        columns={
            setup.ANALYSIS_DB_QUERY_INDEX: pandera.Column(
                str,
                nullable=False,
                unique=True,
                metadata={'primary_key': True}
            ),
            'name': pandera.Column(
                str,
                nullable=False,
                unique=True
            ),
            'server_type': pandera.Column(
                str,
                nullable=False,
                unique=False
            ),
            'submitted_by': pandera.Column(
                str,
                nullable=False,
                unique=False
            ),
            'created_on': pandera.Column(
                datetime.datetime,
                nullable=False,
                unique=False
            ),
            'state': pandera.Column(
                str,
                nullable=True,
                unique=False
            ),
            'start_time': pandera.Column(
                datetime.datetime,
                nullable=False,
                unique=False
            ),
            'end_time': pandera.Column(
                datetime.datetime,
                nullable=True,
                unique=False
            ),
            'run_time': pandera.Column(
                float,
                nullable=True,
                unique=False
            ),
            'file_name': pandera.Column(
                str,
                nullable=False,
                unique=False
            ),
            'inputs': pandera.Column(
                str,
                nullable=False,
                unique=False
            ),
            'outputs': pandera.Column(
                str,
                nullable=False,
                unique=False
            ),
            'run_information': pandera.Column(
                str,
                nullable=True,
                unique=False
            ),
            'parameters': pandera.Column(
                str,
                nullable=False,
                unique=False
            ),
            'tags': pandera.Column(
                str,
                nullable=False,
                unique=False
            ),
            'url': pandera.Column(
                str,
                nullable=False,
                unique=False
            )
        }
    )


# Define the `analysis` database connection
class Connection(_generic.Connection):
    """ The `users` sqlite3-database Connection. """

    def __init__(
        self
    ):
        """ Initializes an instance of the `analysis` sqlite3-database Connection. """

        super().__init__(
            db_name=setup.ANALYSIS_DB_NAME,
            dir_name=setup.DB_DIR
        )
