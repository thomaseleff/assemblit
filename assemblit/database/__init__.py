""" Database management """

from assemblit.database import _adapters
from assemblit.database import _structures

__all__ = ['_adapters', '_structures']

# Register sqlite3-object adapters
_adapters.Sqlite.register()
