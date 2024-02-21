"""
Information
---------------------------------------------------------------------
Name        : db.py
Location    : ~/
Author      : Tom Eleff
Published   : 2024-02-07
Revised on  : .

Description
---------------------------------------------------------------------
Database handler class for retrieving information from a sqlite3
database.
"""

import os
import sqlite3
import json
import ast


class Handler():

    def __init__(
        self,
        dir_name: str,
        db_name: str
    ):
        """ Initializes an instance of the database-handler Class().

        Parameters
        ----------
        dir_name : `str`
            Local directory path of the database.
        db_name : `str`
            Name of the database located within `dir_name`.
        """

        self.dir_name = dir_name
        self.db_name = db_name

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
                    table_name,
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
            "SELECT name FROM sqlite_master WHERE name='%s';" % (table_name)
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
            """DROP TABLE '%s'""" % (table_name)
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
                    table_name,
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

        # Get number of table records returned from the query
        records = self.select_num_table_records(
            table_name=table_name,
            filtr=filtr
        )

        if records == 1:

            # Update values in table
            self.cursor.execute(
                """
                UPDATE %s SET %s = '%s' WHERE %s = '%s';
                """ % (
                    table_name,
                    values['col'],
                    values['val'],
                    filtr['col'],
                    filtr['val']
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
        values: dict
    ):
        """ Resets a column value within a database table.

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
        """
        self.cursor.execute(
            """
            UPDATE %s SET %s = '%s';
            """ % (
                table_name,
                values['col'],
                values['val']
            )
        )
        self.connection.commit()

    # Define db function(s) to delete table values
    def delete(
        self,
        table_name: str,
        filtr: dict
    ):
        """ Removes a row of values in a filtered database table.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        filtr : `dict`
            Dictionary object containing the column `col` and value
                `val` to filter `table_name`. The returned record is
                deleted from `table_name`.

                e.g., {
                    'col' : 'id',
                    'val' : '1'
                }
        """

        # Delete values from table
        self.cursor.execute(
            """
            DELETE FROM %s WHERE %s = '%s';
            """ % (
                table_name,
                filtr['col'],
                filtr['val']
            )
        )
        self.connection.commit()

    # Define generic db function(s) for retrieving table information
    def table_record_exists(
        self,
        table_name: str,
        filtr: dict
    ) -> bool:
        """ Returns `True` when the filtered record exists within a database table.

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

        if self.cursor.execute(
            "SELECT %s FROM %s WHERE %s = '%s'" % (
                str(filtr['col']),
                table_name,
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
        """ Returns the table column names in a database table as a `list`.

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
                return as_type(
                    value=value[0],
                    return_dtype=return_dtype
                )
            elif len(value) == 1 and multi:
                return [as_type(
                    value=value[0],
                    return_dtype=return_dtype
                )]
            elif len(value) > 1 and multi:
                return [as_type(
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
                return as_type(
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
def as_type(
    value: str,
    return_dtype: str = 'str'
) -> str | int | float | bool | list | dict:
    """ Returns `value` as `return_dtype`.

    Parameters
    ----------
    value : `str`
        String of the value to convert to `return_dtype`.
    return_dtype : `str`
        Name of the datatype (`str`, `int`, `float`, `bool`, `list`, `dict`) of
            the returned value. If the returned value cannot be converted
            to `return_dtype` then a `TypeError` is raised. If the name of the
            `return_dtype` is invalid, then a `NameError` is returned.
    """

    try:
        if return_dtype.strip().upper() == 'STR':
            return str(value)

        elif return_dtype.strip().upper() == 'INT':
            return int(value)

        elif return_dtype.strip().upper() == 'FLOAT':
            return float(value)

        elif return_dtype.strip().upper() == 'BOOL':

            try:
                return ast.literal_eval(value)

            except (SyntaxError, ValueError):
                raise TypeError(
                    ' '.join([
                        "{%s} value" % (
                            value
                        ),
                        "cannot be converted to {%s}." % (
                            return_dtype
                        )
                    ])
                )

        elif (
            (return_dtype.strip().upper() == 'LIST')
            or (return_dtype.strip().upper() == 'DICT')
        ):
            try:
                return json.loads(value)

            except json.decoder.JSONDecodeError:
                raise TypeError(
                    ' '.join([
                        "{%s} value" % (
                            value
                        ),
                        "cannot be converted to {%s}." % (
                            return_dtype
                        )
                    ])
                )

        else:
            raise NameError(
                'Invalid return datatype {%s}.' % (
                    return_dtype
                )
            )

    except ValueError:
        raise TypeError(
            ' '.join([
                "{%s} value" % (
                    value
                ),
                "cannot be converted to {%s}." % (
                    return_dtype
                )
            ])
        )
