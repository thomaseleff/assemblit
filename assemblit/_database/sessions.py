""" Database table """

from typing import ClassVar
from dataclasses import dataclass
import pandera
from assemblit import setup
from assemblit._database import _generic


# Define the `sessions` database table schemas
@dataclass
class Schemas():
    """ A `class` that represents the `sessions` database schemas.

    Attributes
    ----------
    data : `assemblit.database._generic.Schema`
        The `sessions.data` database table schema.
    analysis : `assemblit.database._generic.Schema`
        The `sessions.analysis` database table schema.
    """

    # The `data` table Schema
    data: ClassVar[_generic.Schema] = _generic.Schema(
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
    analysis: ClassVar[_generic.Schema] = _generic.Schema(
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
class Connection(_generic.Connection):
    """ The `sessions` sqlite3-database Connection. """

    def __init__(
        self
    ):
        """ Initializes an instance of the `sessions` sqlite3-database Connection. """

        super().__init__(
            db_name=setup.SESSIONS_DB_NAME,
            dir_name=setup.DB_DIR
        )
