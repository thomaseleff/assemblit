"""
Information
---------------------------------------------------------------------
Name        : db.py
Location    : ~/
Author      : Tom Eleff
Published   : 2024-03-17
Revised on  : .

Description
---------------------------------------------------------------------
Database handler class for retrieving information from a sqlite3
database.
"""

import os
import sqlite3
from getstreamy import setup
from pytilities import utils


class Handler():

    def __init__(
        self,
        db_name: str,
        dir_name: str = setup.DB_DIR
    ):
        """ Initializes an instance of the database-handler Class().

        Parameters
        ----------
        db_name : `str`
            Name of the database located within `dir_name`.
        dir_name : `str`
            Local directory path of the database.
        """

        # Assign db class variables
        self.dir_name = dir_name
        self.db_name = db_name

        # Create the database directory if it does not exist
        if not os.path.exists(dir_name):
            os.mkdir(os.path.join(
                setup.ROOT_DIR,
                'db'
            ))

        # Setup connection
        self.connection = sqlite3.connect(
            os.path.join(
                dir_name,
                db_name
            )
        )

        # Setup cursor
        self.cursor = self.connection.cursor()

    # Define db function(s) to create tables
    def create_table(
        self,
        table_name: str,
        cols: list
    ):
        """ Creates a database table.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        cols : `list`
            List object containing the columns of `table_name`.
        """

        if not self.table_exists(table_name=table_name):
            self.cursor.execute(
                "CREATE TABLE %s(%s)" % (
                    str(table_name),
                    ', '.join(cols)
                )
            )

    def table_exists(
        self,
        table_name: str
    ) -> bool:
        """ Returns `True` when the table exists within a database.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        """

        if self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE name='%s';" % (str(table_name))
        ).fetchall():
            return True
        else:
            return False

    # Define db function(s) to drop tables
    def drop_table(
        self,
        table_name: str
    ):
        """ Drops a table from the database.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        """

        self.cursor.execute(
            """DROP TABLE '%s'""" % (str(table_name))
        )
        self.connection.commit()

    # Define db function(s) to insert/update table values
    def insert(
        self,
        table_name: str,
        values: dict,
        validate: dict = {}
    ):
        """ Inserts a row of values into a database table.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        values : `dict`
            Dictionary object containing the table columns (as keys)
                and values (as values) to insert into `table_name`. If
                the order of the columns does not match the order of
                columns in the database table, a `KeyError` is raised.
        validate : `dict`
            Dictionary object containing the column `col` and value
                `val` to filter `table_name`. If the filtered table
                returns a record, a `ValueError` is raised.

                e.g., {
                    'col' : 'id',
                    'val' : '1'
                }
        """

        # Validate
        if validate:
            if self.table_record_exists(
                table_name=table_name,
                filtr=validate
            ):
                raise ValueError(
                    'Table record already exists.'
                )

        # Check for missing values
        if (
            list(values.keys())
        ) == (
            self.select_table_column_names_as_list(
                table_name=table_name
            )
        ):

            # Insert values into table
            self.cursor.execute(
                """
                INSERT INTO %s VALUES (%s);
                """ % (
                    str(table_name),
                    ', '.join(
                        [
                            "'%s'" % str(i) for i in list(
                                values.values()
                            )
                        ]
                    )
                )
            )
            self.connection.commit()

        else:

            # Raise an error if the table columns mismatch
            #   the provided values
            raise KeyError(
                ' '.join([
                    "Missing values.",
                    "The Sqlite {%s} table in {%s} db" % (
                        table_name,
                        self.db_name
                    ),
                    "expects values in the following order,",
                    str(self.select_table_column_names_as_list(
                        table_name=table_name
                    ))
                ])
            )

    def update(
        self,
        table_name: str,
        values: dict,
        filtr: dict
    ):
        """ Updates a single column value in a filtered database table.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        values : `dict`
            Dictionary object containing the column `col` and value
                `val` to update in `table_name`.

                e.g., {
                    'col' : 'name',
                    'val' : 'Jimmy'
                }

        filtr : `dict`
            Dictionary object containing the column `col` and value
                `val` to filter `table_name`. If the filtered table
                returns more than one record, a `ValueError` is raised.

                e.g., {
                    'col' : 'id',
                    'val' : '1'
                }
        """

        # Get the number of table records returned from the query
        records = self.select_num_table_records(
            table_name=table_name,
            filtr=filtr
        )

        # Update values in the database table
        if records == 1:
            self.cursor.execute(
                """
                UPDATE %s SET %s = '%s' WHERE %s = '%s';
                """ % (
                    str(table_name),
                    str(values['col']),
                    str(values['val']),
                    str(filtr['col']),
                    str(filtr['val'])
                )
            )
            self.connection.commit()

        else:
            raise ValueError(
                'The query attempted to update more than 1 record.'
            )

    def reset_table_column_value(
        self,
        table_name: str,
        values: dict,
        filtr: dict = {}
    ):
        """ Resets a column value within a filtered database table.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        values : `dict`
            Dictionary object containing the column `col` and value
                `val` to update in `table_name`.

                e.g., {
                    'col' : 'name',
                    'val' : 'Jimmy'
                }

        filtr : `dict`
            Dictionary object containing the column `col` and value
                `val` to filter `table_name`. If the filtered table
                returns more than one record, a `ValueError` is raised.

                e.g., {
                    'col' : 'id',
                    'val' : '1'
                }
        """

        if filtr:
            if type(filtr['val']) is list:
                self.cursor.execute(
                    """
                    UPDATE %s SET %s = '%s'
                        WHERE %s IN (%s);
                    """ % (
                        str(table_name),
                        str(values['col']),
                        str(values['val']),
                        str(filtr['col']),
                        ', '.join(["'%s'" % str(i) for i in filtr['val']])
                    )
                )
            else:
                self.cursor.execute(
                    """
                    UPDATE %s SET %s = '%s'
                        WHERE %s = '%s';
                    """ % (
                        str(table_name),
                        str(values['col']),
                        str(values['val']),
                        str(filtr['col']),
                        str(filtr['val'])
                    )
                )
        else:
            self.cursor.execute(
                """
                UPDATE %s SET %s = '%s';
                """ % (
                    str(table_name),
                    str(values['col']),
                    str(values['val'])
                )
            )
        self.connection.commit()

    # Define db function(s) to delete table values
    def delete(
        self,
        database_table_object: list
    ):
        """ Removes all rows of values in a filtered database table for each
        database table object.

        Parameters
        ----------
        database_table_object: list
            List of dictionary objects containing kwargs for deleting table
                column values.

                e.g., [
                    {
                        'table_name': 'table',
                        'filtr': {
                            'col' : 'id',
                            'val' : ['1']
                        }
                    }
                ]
        """

        # Delete values from each database table object
        if database_table_object:
            for kwargs in database_table_object:
                self.delete_table_column_value(
                    **kwargs
                )

    def delete_table_column_value(
        self,
        table_name: str,
        filtr: dict
    ):
        """ Removes all rows of values in a filtered database table.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        filtr : `dict`
            Dictionary object containing the column `col` and value
                `val` to filter `table_name`. The returned record(s) are
                deleted from `table_name`.

                e.g., {
                    'col' : 'id',
                    'val' : '1'
                }
        """

        # Delete value(s) from the database table
        if type(filtr['val']) is list:
            self.cursor.execute(
                """
                DELETE FROM %s WHERE %s IN (%s);
                """ % (
                    str(table_name),
                    str(filtr['col']),
                    ', '.join(["'%s'" % str(i) for i in filtr['val']])
                )
            )
        else:
            self.cursor.execute(
                """
                DELETE FROM %s WHERE %s = '%s';
                """ % (
                    str(table_name),
                    str(filtr['col']),
                    str(filtr['val'])
                )
            )
        self.connection.commit()

    def build_database_table_objects_to_delete(
        self,
        table_names: list,
        query_index: str,
        query_index_values: list
    ) -> list:
        """ Creates a list object of database table objects to delete and returns it as a `list`.

        Parameters
        ----------
        table_names : `list`
            Names of all database tables that contain `query_index`.
        query_index : `str`
            Name of the database query index.
        query_index_values : `list`
            List of database `query_index` values that will be deleted.
        """

        object_to_delete = []
        if table_names:
            for table in table_names:
                if self.table_record_exists(
                    table_name=table,
                    filtr={
                        'col': query_index,
                        'val': query_index_values
                    }
                ):
                    object_to_delete += self.create_object_to_delete(
                        table_name=table,
                        query_index=query_index,
                        query_index_values=query_index_values
                    )
        return object_to_delete

    def create_database_table_dependencies(
        self,
        table_names: list,
        query_index: str,
        query_index_value: str,
        dependent_query_index: str
    ) -> list:
        """ Creates a list object of all `dependent_query_index` values that will no longer have
        an associated parent after the provided `query_index_value` is deleted and returns
        it as a `list`.

        Parameters
        ----------
        table_names : `list`
            Names of all database tables that contain `query_index`.
        query_index : `str`
            Name of the database query index, which identifies unique records within the database.
        query_index_value : `str`
            Value of the database `query_index` that will be deleted.
        dependent_query_index : `str`
            Name of the database `query_index` that depends on `query_index`.
        """

        dependent_query_index_values = []
        if table_names:
            for table in table_names:
                dependencies = self.select_orphaned_table_column_values(
                    table_name=table,
                    col=dependent_query_index,
                    filtr={
                        'col': query_index,
                        'val': query_index_value
                    }
                )
                if dependencies:
                    dependent_query_index_values += dependencies
        return dependent_query_index_values

    def select_orphaned_table_column_values(
        self,
        table_name: str,
        col: str,
        filtr: dict
    ) -> list:
        """ Selects the associated database table `col` values that belong
        only to the filtered index value, `filtr['val']`, and returns them as a `list`.
        The returned values would have no owner once `filtr['val']`
        is deleted from the database.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        col : `str`
            Name of the database table column.
        filtr : `dict`
            Dictionary object containing the column `col` and value
                `val` to filter `table_name`. The returned record is
                deleted from `table_name`.

                e.g., {
                    'col' : 'id',
                    'val' : '1'
                }
        """

        if type(filtr['val']) is list:
            query = """
                SELECT %s FROM (
                    SELECT %s, %s, COUNT(%s) as COUNT FROM %s
                        GROUP BY %s
                ) WHERE COUNT = 1 AND %s in (%s);
            """ % (
                str(col),
                str(col),
                str(filtr['col']),
                str(col),
                str(table_name),
                str(col),
                filtr['col'],
                ', '.join(["'%s'" % str(i) for i in filtr['val']])
            )
        else:
            query = """
                SELECT %s FROM (
                    SELECT %s, %s, COUNT(%s) as COUNT FROM %s
                        GROUP BY %s
                ) WHERE COUNT = 1 AND %s = '%s';
            """ % (
                str(col),
                str(col),
                str(filtr['col']),
                str(col),
                str(table_name),
                str(col),
                str(filtr['col']),
                str(filtr['val'])
            )

        values = [
            i[0] for i in self.cursor.execute(query).fetchall()
        ]

        return [utils.as_type(value=i, return_dtype='str') for i in values]

    def create_object_to_delete(
        self,
        table_name: str,
        query_index: str,
        query_index_values: list
    ) -> list:
        """ Creates a dictionary object containg kwargs for deleting rows of a database table
        and returns it as a `list`.

        Parameters
        ----------
        table_names : `list`
            Name of the database table.
        query_index : `str`
            Name of the database query index.
        query_index_values : `list`
            List of database `query_index` values that will be deleted.
        """

        return [
            {
                'table_name': table_name,
                'filtr': {
                    'col': query_index,
                    'val': query_index_values
                }
            }
        ]

    # Define generic db function(s) for retrieving table information
    def table_record_exists(
        self,
        table_name: str,
        filtr: dict
    ) -> bool:
        """ Returns `True` when the filtered records exist within a database table.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        filtr : `dict`
            Dictionary object containing the column `col` and value
                `val` to filter `table_name`. If the filtered table
                returns a record, `True` is returned.

                e.g., {
                    'col' : 'id',
                    'val' : '1'
                }
        """

        if type(filtr['val']) is list:
            if self.cursor.execute(
                "SELECT %s FROM %s WHERE %s IN (%s)" % (
                    str(filtr['col']),
                    str(table_name),
                    str(filtr['col']),
                    ', '.join(["'%s'" % str(i) for i in filtr['val']])
                )
            ).fetchall():
                return True
            else:
                return False
        else:
            if self.cursor.execute(
                "SELECT %s FROM %s WHERE %s = '%s'" % (
                    str(filtr['col']),
                    str(table_name),
                    str(filtr['col']),
                    str(filtr['val'])
                )
            ).fetchall():
                return True
            else:
                return False

    def select_table_column_names_as_list(
        self,
        table_name: str
    ) -> list:
        """ Returns the column names of a database table as a `list`.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        """
        return [
            col[0] for col in self.cursor.execute(
                "SELECT name FROM pragma_table_info('%s') ORDER BY cid;" % (
                    table_name
                )
            ).fetchall()
        ]

    def select_num_table_records(
        self,
        table_name: str,
        filtr: dict
    ) -> int:
        """ Returns the number of records from a filtered database table as an `int`.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        filtr : `dict`
            Dictionary object containing the column `col` and value
                `val` to filter `table_name`. If the filtered table
                returns (a) record(s), then the number of records
                is returned.

                e.g., {
                    'col' : 'id',
                    'val' : '1'
                }
        """

        query = "SELECT COUNT(*) FROM %s WHERE %s = '%s';" % (
            table_name,
            str(filtr['col']),
            str(filtr['val'])
        )
        value = [
            i[0] for i in self.cursor.execute(query).fetchall()
        ]

        if value:
            return int(value[0])
        else:
            return 0

    def select_all_tables_with_column_name(
        self,
        col: str
    ) -> list:
        """ Returns all table names from a database that contain some column
        name as a `list`.

        Parameters
        ----------
        col : `str`
            Name of the database table column.
        """

        query = """
            SELECT m.name AS table_name,
                p.name AS column_name
            FROM sqlite_master AS m
            LEFT OUTER JOIN pragma_table_info((m.name)) AS p
                ON m.name <> p.name
            WHERE column_name = '%s'
            ORDER BY table_name, column_name;
        """ % (col)

        return [i[0] for i in self.cursor.execute(query).fetchall()]

    # Define generic db function(s) for selecting table values
    def select_table_column_value(
        self,
        table_name: str,
        col: str,
        filtr: dict,
        return_dtype: str = 'str',
        multi: bool = False,
        order: str = 'ASC'
    ) -> str | int | float | bool | list | dict:
        """ Returns a single column value from a filtered database table as `return_dtype`.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        col : `str`
            Name of the database table column.
        filtr : `dict`
            Dictionary object containing the column `col` and value `val` to filter
                `table_name`. If the filtered table returns (a) record(s), then the
                `col` value is returned as `return_dtype`. If no record(s) are returned,
                then `NullReturnValue` is raised.

                e.g., {
                    'col' : 'id',
                    'val' : '1'
                }

        return_dtype : `str`
            Name of the datatype (`str`, `int`, `float`, `bool`, `list`, `dict`) of
                the returned value. If the returned value cannot be converted
                to `return_dtype` then a `TypeError` is raised.
        multi : `bool`
            `True` or `False`, whether multiple records are expected to be returned or not.
                If the number of returned records is inconsistent, a `ValueError` is raised.
        order : `order`
            The sorting method (`ASC`, `DESC`) for the returned values.
        """

        if type(filtr['val']) is list:
            query = "SELECT %s FROM %s WHERE %s in (%s) ORDER BY %s %s;" % (
                str(col),
                table_name,
                str(filtr['col']),
                ', '.join(["'%s'" % (i) for i in filtr['val']]),
                str(col),
                str(order)
            )
        else:
            query = "SELECT %s FROM %s WHERE %s = '%s' ORDER BY %s %s;" % (
                str(col),
                table_name,
                str(filtr['col']),
                str(filtr['val']),
                str(col),
                str(order)
            )

        value = [
            i[0] for i in self.cursor.execute(query).fetchall()
        ]

        if value:
            if len(value) == 1 and not multi:
                return utils.as_type(
                    value=value[0],
                    return_dtype=return_dtype
                )
            elif len(value) == 1 and multi:
                return [utils.as_type(
                    value=value[0],
                    return_dtype=return_dtype
                )]
            elif len(value) > 1 and multi:
                return [utils.as_type(
                    value=v,
                    return_dtype=return_dtype
                ) for v in value]
            else:
                raise ValueError(
                    ' '.join([
                        "The query {%s} returned more than one value." % (
                            query
                        )
                    ])
                )
        else:
            raise NullReturnValue(
                "The query {%s} returned a null value." % (
                    query
                )
            )

    def select_multi_table_column_value(
        self,
        table_name: str,
        cols: str,
        filtr: dict
    ) -> dict:
        """ Returns multiple column values from a filtered database table as a `dict`.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        cols : `str`
            Names of the database table columns.
        filtr : `dict`
            Dictionary object containing the column `col` and value `val` to filter
                `table_name`. If the filtered table returns (a) record(s), then
                the `cols` and values are returned as a `dict`. If no record(s) are
                returned, then `NullReturnValue` is raised.

                e.g., {
                    'col' : 'id',
                    'val' : '1'
                }
        """

        query = """
            SELECT %s
                FROM %s
                    WHERE %s = '%s';
        """ % (
            ', '.join(
                [
                    str(i) for i in cols
                ]
            ),
            table_name,
            filtr['col'],
            filtr['val']
        )
        values = self.cursor.execute(query).fetchall()[0]

        if values:
            return dict(
                zip(
                    cols,
                    values
                )
            )
        else:
            raise NullReturnValue(
                "The query {%s} returned a null value." % (
                    query
                )
            )

    def select_generic_query(
        self,
        query: str,
        return_dtype: str
    ) -> str | int | float | bool | list | dict:
        """ Returns the result of the SQL query as `return_dtype`.

        Parameters
        ----------
        query : `str`
            SQL-query string. If multiple records are returned, a 'ValueError` is raised.
            If no records are returned, a `NullReturnValue` is raised.
        return_dtype : `str`
            Name of the datatype (`str`, `int`, `float`, `bool`, `list`, `dict`) of
                the returned value. If the returned value cannot be converted
                to `return_dtype` then a `TypeError` is raised.
        """

        value = [
            i[0] for i in self.cursor.execute(query).fetchall()
        ]

        if value:
            if len(value) == 1:
                return utils.as_type(
                    value=value[0],
                    return_dtype=return_dtype
                )

            else:
                raise ValueError(
                    ' '.join([
                        "The query {%s} returned more than one value." % (
                            query
                        )
                    ])
                )

        else:
            raise NullReturnValue(
                "The query {%s} returned a null value." % (
                    query
                )
            )


# Define exception classes
class NullReturnValue(Exception):
    pass


# Define generic db function(s)
def initialize_table(
    db_name: str,
    table_name: str,
    cols: list
) -> Handler:
    """ Initializes a database table.

    Parameters
    ----------
    db_name : `str`
        Name of the database.
    table_name : `str`
        Name of the database table.
    cols : `list`
        List object containing the columns of `table_name`.
    """

    # Initialize the connection to the database
    Db = Handler(
        db_name=db_name
    )

    # Create the table in the database
    Db.create_table(
        table_name=table_name,
        cols=cols
    )

    return Db
