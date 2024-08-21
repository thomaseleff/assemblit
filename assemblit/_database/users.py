""" Database table """

from typing import ClassVar
from dataclasses import dataclass
import pandera
from assemblit import setup
from assemblit._database import _generic


# Define the `users` database table schemas
@dataclass
class Schemas():
    """ A `class` that represents the `users` database schemas.

    Attributes
    ----------
    credentials : `assemblit.database._generic.Schema`
        The `users.credentials` database table schema.
    sessions : `assemblit.database._generic.Schema`
        The `users.sessions` database table schema.
    """

    # The `credentials` table Schema.
    credentials: ClassVar[_generic.Schema] = _generic.Schema(
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
    sessions: ClassVar[_generic.Schema] = _generic.Schema(
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
class Connection(_generic.Connection):
    """ The `users` sqlite3-database Connection. """

    def __init__(
        self
    ):
        """ Initializes an instance of the `users` sqlite3-database Connection. """

        super().__init__(
            db_name=setup.USERS_DB_NAME,
            dir_name=setup.DB_DIR
        )
