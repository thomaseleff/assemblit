""" Database clause defaults """

from dataclasses import dataclass
from typing import Any, ClassVar
import datetime
from assemblit.database import _adapters


@dataclass
class Conflict():
    """ A `class` that contains database conflict-clause defaults.
    
    Attributes
    ----------
    rollback : `str`
        Defines the default rollback clause.
    abort : `str`
        Defines the default abort clause.
    fail : `str`
        Defines the default fail clause.
    ignore : `str`
        Defines the default ignore clause.
    replace : `str`
        Defines the default replace clause.
    """

    rollback: ClassVar[str] = 'ROLLBACK'
    abort: ClassVar[str] = 'ABORT'
    fail: ClassVar[str] = 'FAIL'
    ignore: ClassVar[str] = 'IGNORE'
    replace: ClassVar[str] = 'REPLACE'

    def nullable_clause():
        """ Returns the conflict-clause for nullable value conflicts. """

        return 'ON CONFLICT %s' % (Conflict.abort)

    def unique_clause():
        """ Returns the conflict-clause for unique value conflicts. """

        return 'ON CONFLICT %s' % (Conflict.abort)

    def primary_key_clause():
        """ Returns the conflict-clause for primary-key conflicts. """

        return 'ON CONFLICT %s' % (Conflict.abort)


class Literal():
    """ A `class` for converting values to their literal string representation """

    def value(value: Any) -> str:
        """ Converts a value to its literal string value.

        value : `Any`
            The value to convert.
        """

        if value is None:
            return "'NULL'"
        elif isinstance(value, bool):
            if value:
                return "'TRUE'"
            else:
                return "'FALSE'"
        elif isinstance(value, datetime.datetime):
            return "'%s'" % (_adapters.Sqlite.adapt_datetime(value))
        elif isinstance(value, datetime.timedelta):
            return "'%s'" % (_adapters.Sqlite.adapt_timedelta(value))
        else:
            return "'%s'" % (value)
