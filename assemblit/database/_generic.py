""" Database table """

from __future__ import annotations
from typing import List, Literal
import os
import sqlite3
import contextlib
import pandera
from assemblit.blocks.structures import Setting
from assemblit.database import _datatypes, _syntax
from assemblit.database._structures import DBMS, Filter, Validate, Value, Table, Row
from pytensils import utils


# Define the generic database schema `class`
class Schema(pandera.DataFrameSchema):
    """ A `class` that represents a database table schema. """

    def from_settings(
        name: str,
        settings_object: List[Setting],
        primary_key: str | None = None
    ) -> Schema:
        """ Returns a `Schema` from a list of `assemblit.blocks.structures.Setting` objects.

        Parameters
        ----------
        name : `str`
            The name of the schema.
        settings : `List[Setting]`
            List of `assemblit.blocks.structures.Setting` objects.
        primary_key : `str | None`
            The primary key of the schema.
        """

        # Assert object type
        if not isinstance(settings_object, list):
            raise TypeError('Object must be a `list`.')

        # Assert object item type
        for setting in settings_object:
            if not isinstance(setting, Setting):
                raise TypeError('Object must be a list of `assemblit.blocks.structures.Setting` objects.')

        # Construct schema
        if primary_key:
            return Schema(
                name=str(name),
                columns={
                    **{primary_key: pandera.Column(str, nullable=False, unique=True, metadata={'primary_key': True})},
                    **{setting.parameter: setting.to_pandera() for setting in settings_object}
                }
            )
        else:
            return Schema(
                name=str(name),
                columns={setting.parameter: setting.to_pandera() for setting in settings_object}
            )

    def from_pandas() -> Schema:
        """ Returns a `Schema` from a `pandas.DataFrame` object.
        """
        raise NotImplementedError

    def from_sqlite() -> Schema:
        """ Returns a `Schema` from a sqlite3-database table.
        """
        raise NotImplementedError

    def cols(self) -> list[str]:
        """ Returns the schema columns as a `list`
        """
        return list(self.columns.keys())

    def to_dict(self) -> dict:
        """ Returns a `dict` object representation of the `Schema`.
        """
        raise NotImplementedError

    def to_sqlite(self) -> str:
        """ Returns a sqlite3-column schema definition. """
        column_name: str
        column_schema: pandera.Column
        columns: list[str] = []
        primary_keys: list[str] = []

        # Build column definitions(s)
        for column_name, column_schema in self.columns.items():

            # Append column definition
            columns.append(self._sqlite_column_def(column_name=column_name, column_schema=column_schema))

            # Append primary-key
            if column_schema.metadata:
                if 'primary_key' in column_schema.metadata:
                    primary_keys.append(column_name)

        if primary_keys:
            return ''.join(
                [
                    '(',
                    ', '.join(columns),
                    ', ',
                    'PRIMARY KEY',
                    '(',
                    ', '.join(primary_keys),
                    ')',
                    ' ',
                    _syntax.Conflict.primary_key_clause(),
                    ')'
                ]
            )
        else:
            return ''.join(
                [
                    '(',
                    ', '.join(columns),
                    ')'
                ]
            )

    def _sqlite_column_def(
        self,
        column_name: str,
        column_schema: pandera.Column
    ):
        """ Returns the sqlite3-column definition for a single schema column.

        Parameters
        ----------
        column_name : `str`
            The name of the column.
        column_schema : `pandera.Column`
            The `pandera` column schema definition.
        """
        column_def = ' '.join([
            column_name,
            _datatypes.from_pandera(column_schema.dtype).to_sqlite()
        ])

        if not column_schema.nullable:
            column_def = ' '.join([column_def, 'NOT NULL', _syntax.Conflict.nullable_clause()])
        if column_schema.unique:
            column_def = ' '.join([column_def, 'UNIQUE', _syntax.Conflict.unique_clause()])
        if column_schema.default is not None:
            column_def = ' '.join([column_def, 'DEFAULT', _syntax.Literal.value(column_schema.default)])

        return column_def


# Define the generic database connection `class`
class Connection():
    """ A `class` that represents a database connection. """

    def __init__(
        self,
        db_name: str,
        dir_name: str
    ):
        """ Initializes an instance of the database-connection `class`.

        Parameters
        ----------
        db_name : `str`
            Name of the database located within `dir_name`.
        dir_name : `str`
            Local directory path of the database.
        """

        # Assign class variables
        self.dir_name: str = dir_name
        self.db_name: str = parse_db_name(db_name=db_name)
        self.conn: sqlite3.Connection = sqlite3.connect(os.path.join(self.dir_name, self.db_name))

        # Create the database directory if it does not exist
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)

    # Define db function(s) to handle connections
    def connection(self) -> sqlite3.Connection:
        """ Returns a new sqlite3-connection context manager for all
        `DELETE`, `INSERT` and `UPDATE` commands.
        """
        return sqlite3.connect(os.path.join(self.dir_name, self.db_name))

    def __del__(self):
        """ Closes the sqlite3-connection when deconstructed.
        """
        try:
            self.conn.close()
        except AttributeError:
            pass

    # Define db function(s) to create tables
    def create_table(
        self,
        table_name: str,
        schema: Schema
    ) -> Connection:
        """ Creates {table_name} in the database if it does not exist.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        schema : `assemblit.database.generic.Schema`
            Database table schema object.
        """
        self.conn.cursor().execute(
            """
                CREATE TABLE IF NOT EXISTS %s %s;
            """ % (str(table_name), schema.to_sqlite())
        )

        return self

    # Define db function(s) to drop tables
    def drop_table(
        self,
        table_name: str
    ):
        """ Drops {table_name} from the database if it exists.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        """
        self.conn.cursor().execute(
            """
                DROP TABLE IF EXISTS '%s';
            """ % (
                str(table_name)
            )
        )

    # Define db function(s) to insert/update table values
    def insert(
        self,
        table_name: str,
        row: Row,
        validate: Validate | None = None
    ):
        """ Inserts a row of values into the database table.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        row : `Row`
            Row object containing the table columns `cols`
                and values `vals` to insert into `table_name`. If
                the order of the columns does not match the order of
                columns in the database table, a `KeyError` is raised.
        validate : `Validate`
            Validate object containing the column `col` and value
                `val` to filter `table_name`. If the filtered table
                returns a record, a `ValueError` is raised.
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

        # Insert values
        if (list(row.cols)) == (
            self.select_table_column_names_as_list(
                table_name=table_name
            )
        ):
            with contextlib.closing(self.connection()) as connection:
                connection.cursor().execute(
                    """
                        INSERT INTO %s
                        VALUES (%s);
                    """ % (
                        str(table_name),
                        ', '.join(
                            [
                                "'%s'" % normalize(string=i) for i in list(
                                    row.vals
                                )
                            ]
                        )
                    )
                )
                connection.commit()

        # Raise an error if the table columns mismatch
        #   the provided values
        else:
            raise KeyError(
                ' '.join([
                    "Missing values.",
                    "The Sqlite {%s} table in {%s} " % (
                        table_name,
                        self.db_name
                    ),
                    "expects values in the following order,",
                    str(
                        self.select_table_column_names_as_list(
                            table_name=table_name
                        )
                    )
                ])
            )

    def update(
        self,
        table_name: str,
        value: Value,
        filtr: Filter
    ):
        """ Updates a single column value in a filtered database table.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        value : `Value`
            Value object containing the column `col` and value
                `val` to update in `table_name`.
        filtr : `Filter`
            Filter object containing the column `col` and value
                `val` to filter `table_name`. If the filtered table
                returns more than one record, a `ValueError` is raised.
        """

        # Update value
        if self.select_num_table_records(
            table_name=table_name,
            filtr=filtr
        ) == 1:
            with contextlib.closing(self.connection()) as connection:
                connection.cursor().execute(
                    """
                        UPDATE %s
                        SET %s = '%s'
                        WHERE %s = '%s';
                    """ % (
                        str(table_name),
                        str(value.col),
                        normalize(string=value.val),
                        str(filtr.col),
                        normalize(string=filtr.val)
                    )
                )
                connection.commit()

        # Raise an error if the query attempts to update more
        #   than one record.
        else:
            raise ValueError(
                'The query attempted to update more than one record.'
            )

    def reset_table_column_value(
        self,
        table_name: str,
        value: Value,
        filtr: Filter | None = None
    ):
        """ Resets a column value in the database table.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        value : `Value`
            Value object containing the column `col` and value
                `val` to update in `table_name`.
        filtr : `Filter`
            Filter object containing the column `col` and value
                `val` to filter `table_name`. If the filtered table
                returns more than one record, a `ValueError` is raised.
        """

        with contextlib.closing(self.connection()) as connection:
            if filtr:
                if isinstance(filtr.val, list):
                    connection.cursor().execute(
                        """
                            UPDATE %s
                            SET %s = '%s'
                            WHERE %s IN (%s);
                        """ % (
                            str(table_name),
                            str(value.col),
                            normalize(string=value.val),
                            str(filtr.col),
                            ', '.join(["'%s'" % normalize(string=i) for i in filtr.val])
                        )
                    )
                else:
                    connection.cursor().execute(
                        """
                            UPDATE %s
                            SET %s = '%s'
                            WHERE %s = '%s';
                        """ % (
                            str(table_name),
                            str(value.col),
                            normalize(string=value.val),
                            str(filtr.col),
                            normalize(string=filtr.val)
                        )
                    )
            else:
                connection.cursor().execute(
                    """
                        UPDATE %s
                        SET %s = '%s';
                    """ % (
                        str(table_name),
                        str(value.col),
                        normalize(string=value.val)
                    )
                )
            connection.commit()

    # Define db function(s) to delete table values
    def delete(
        self,
        tables: list[Table]
    ):
        """ Removes all rows in a filtered database table for each database table object.

        Parameters
        ----------
        tables: `list[Table]`
            List of Table objects containing parameters for deleting table
                column values.
        """
        if tables:
            for table in tables:
                table: Table
                self.delete_table_column_value(
                    table_name=table.table_name,
                    filtr=table.filtr
                )

    def delete_table_column_value(
        self,
        table_name: str,
        filtr: Filter
    ):
        """ Removes all rows of values in a filtered database table.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        filtr : `Filter`
            Filter object containing the column `col` and value
                `val` to filter `table_name`. The returned record(s) are
                deleted from `table_name`.
        """
        with contextlib.closing(self.connection()) as connection:
            if isinstance(filtr.val, list):
                connection.cursor().execute(
                    """
                        DELETE FROM %s
                        WHERE %s IN (%s);
                    """ % (
                        str(table_name),
                        str(filtr.col),
                        ', '.join(["'%s'" % normalize(string=i) for i in filtr.val])
                    )
                )
            else:
                connection.cursor().execute(
                    """
                        DELETE FROM %s
                        WHERE %s = '%s';
                    """ % (
                        str(table_name),
                        str(filtr.col),
                        normalize(string=filtr.val)
                    )
                )
            connection.commit()

    def build_database_table_objects_to_delete(
        self,
        table_names: list[str],
        query_index: str,
        query_index_values: list[str]
    ) -> list[str]:
        """ Creates a list object of database Table objects to delete and returns it as a `list`.

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
            for table_name in table_names:
                if self.table_record_exists(
                    table_name=table_name,
                    filtr=Filter(
                        col=str(query_index),
                        val=query_index_values
                    )
                ):
                    object_to_delete += [
                        self.create_object_to_delete(
                            table_name=table_name,
                            query_index=query_index,
                            query_index_values=query_index_values
                        )
                    ]
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
                    table_name=str(table),
                    col=dependent_query_index,
                    filtr=Filter(
                        col=str(query_index),
                        val=str(query_index_value)
                    )
                )
                if dependencies:
                    dependent_query_index_values += dependencies
        return dependent_query_index_values

    def select_orphaned_table_column_values(
        self,
        table_name: str,
        col: str,
        filtr: Filter
    ) -> list[str]:
        """ Selects the associated database table `col` values that belong
        only to the filtered index value, `filtr.val`, and returns them as a `list`.
        The returned values would have no owner once `filtr.val` is deleted
        from the database.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        col : `str`
            Name of the database table column.
        filtr : `Filter`
            Filter object containing the column `col` and value
                `val` to filter `table_name`. The returned record is
                deleted from `table_name`.
        """

        if isinstance(filtr.val, list):
            query = """
                SELECT %s
                FROM (
                    SELECT %s, %s, COUNT(%s) as COUNT
                    FROM %s
                    GROUP BY %s
                ) WHERE COUNT = 1 AND %s in (%s);
            """ % (
                str(col),
                str(col),
                str(filtr.col),
                str(col),
                str(table_name),
                str(col),
                str(filtr.col),
                ', '.join(["'%s'" % normalize(string=i) for i in filtr.val])
            )
        else:
            query = """
                SELECT %s FROM (
                    SELECT %s, %s, COUNT(%s) as COUNT
                    FROM %s
                    GROUP BY %s
                ) WHERE COUNT = 1 AND %s = '%s';
            """ % (
                str(col),
                str(col),
                str(filtr.col),
                str(col),
                str(table_name),
                str(col),
                str(filtr.col),
                normalize(string=filtr.val)
            )

        values = [
            i[0] for i in self.conn.cursor().execute(query).fetchall()
        ]

        return [utils.as_type(value=i, return_dtype='str') for i in values]

    def create_object_to_delete(
        self,
        table_name: str,
        query_index: str,
        query_index_values: list[str]
    ) -> list[Table]:
        """ Creates a Table object containg parameters for deleting rows of a database table
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
        return Table(
            table_name=str(table_name),
            filtr=Filter(
                col=str(query_index),
                val=query_index_values
            )
        )

    # Define generic db function(s) for retrieving table information
    def table_exists(
        self,
        table_name: str
    ) -> bool:
        """ Returns `True` when {table_name} exists within the database.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        """
        if self.conn.cursor().execute(
            """
                SELECT name
                FROM sqlite_master
                WHERE name = '%s';
            """ % (str(table_name))
        ).fetchall():
            return True
        else:
            return False

    def table_record_exists(
        self,
        table_name: str,
        filtr: Filter
    ) -> bool:
        """ Returns `True` when the filtered records exist within a database table.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        filtr : `Filter`
            Filter object containing the column `col` and value
                `val` to filter `table_name`. If the filtered table
                returns a record, `True` is returned.
        """
        if isinstance(filtr.val, list):
            if self.conn.cursor().execute(
                """
                    SELECT %s
                    FROM %s
                    WHERE %s IN (%s);
                """ % (
                    str(filtr.col),
                    str(table_name),
                    str(filtr.col),
                    ', '.join(["'%s'" % normalize(string=i) for i in filtr.val])
                )
            ).fetchall():
                return True
            else:
                return False
        else:
            if self.conn.cursor().execute(
                """
                    SELECT %s
                    FROM %s
                    WHERE %s = '%s';
                """ % (
                    str(filtr.col),
                    str(table_name),
                    str(filtr.col),
                    normalize(string=filtr.val)
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
            col[0] for col in self.conn.cursor().execute(
                """
                    SELECT name
                    FROM pragma_table_info('%s')
                    ORDER BY cid;
                """ % (
                    table_name
                )
            ).fetchall()
        ]

    def select_num_table_records(
        self,
        table_name: str,
        filtr: Filter
    ) -> int:
        """ Returns the number of records from a filtered database table as an `int`.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        filtr : `Filter`
            Filter object containing the column `col` and value
                `val` to filter `table_name`. If the filtered table
                returns (a) record(s), then the number of records
                is returned.
        """
        query = """
            SELECT COUNT(*)
            FROM %s
            WHERE %s = '%s';
        """ % (
            str(table_name),
            str(filtr.col),
            normalize(string=filtr.val)
        )
        value = [
            i[0] for i in self.conn.cursor().execute(query).fetchall()
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
            SELECT
                m.name AS table_name,
                p.name AS column_name
            FROM sqlite_master AS m
            LEFT OUTER JOIN pragma_table_info((m.name)) AS p
            ON m.name <> p.name
            WHERE column_name = '%s'
            ORDER BY table_name, column_name;
        """ % (str(col))

        return [i[0] for i in self.conn.cursor().execute(query).fetchall()]

    # Define generic db function(s) for selecting table values
    def select_table_column_value(
        self,
        table_name: str,
        col: str,
        filtr: Filter,
        return_dtype: Literal['str', 'int', 'float', 'bool', 'list', 'dict'] = 'str',
        multi: bool = False,
        order: str = 'ASC',
        contains: bool = True
    ) -> str | int | float | bool | list | dict:
        """ Returns a single column value from a filtered database table as `return_dtype`.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        col : `str`
            Name of the database table column.
        filtr : `Filter`
            Filter object containing the column `col` and value `val` to filter
                `table_name`. If the filtered table returns (a) record(s), then the
                `col` value is returned as `return_dtype`. If no record(s) are returned,
                then `NullReturnValue` is raised.
        return_dtype : `Literal['str', 'int', 'float', 'bool', 'list', 'dict']`
            Name of the datatype (`str`, `int`, `float`, `bool`, `list`, `dict`) of
                the returned value. If the returned value cannot be converted
                to `return_dtype` then a `TypeError` is raised.
        multi : `bool`
            `True` or `False`, whether multiple records are expected to be returned or not.
                If the number of returned records is inconsistent, a `ValueError` is raised.
        order : `order`
            The sorting method (`ASC`, `DESC`) for the returned values.
        contains : `bool`
            `True` or `False`, whether to filter where the filter column values are in
                or not in the filter value(s).
        """

        # Parse filter value
        if not isinstance(filtr.val, list):
            filtr.val = [filtr.val]

        if contains:
            query = """
                SELECT %s
                FROM %s
                WHERE %s IN (%s)
                ORDER BY %s %s;
            """ % (
                str(col),
                str(table_name),
                str(filtr.col),
                ', '.join(["'%s'" % normalize(string=i) for i in filtr.val]),
                str(col),
                str(order)
            )
        else:
            query = """
                SELECT %s
                FROM %s
                WHERE %s NOT IN (%s)
                ORDER BY %s %s;
            """ % (
                str(col),
                str(table_name),
                str(filtr.col),
                ', '.join(["'%s'" % normalize(string=i) for i in filtr.val]),
                str(col),
                str(order)
            )

        value = [
            i[0] for i in self.conn.cursor().execute(query).fetchall()
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
        cols: list[str],
        filtr: Filter
    ) -> dict:
        """ Returns multiple column values from a filtered database table as a `dict`.

        Parameters
        ----------
        table_name : `str`
            Name of the database table.
        cols : `list`
            Names of the database table columns.
        filtr : `Filter`
            Filter object containing the column `col` and value `val` to filter
                `table_name`. If the filtered table returns (a) record(s), then
                the `cols` and values are returned as a `dict`. If no record(s) are
                returned, then `NullReturnValue` is raised.
        """
        if isinstance(filtr.val, list):
            query = """
                SELECT %s
                FROM %s
                WHERE %s IN (%s);
            """ % (
                ', '.join([str(i) for i in cols]),
                str(table_name),
                str(filtr.col),
                ', '.join(["'%s'" % normalize(string=i) for i in filtr.val])
            )
        else:
            query = """
                SELECT %s
                FROM %s
                WHERE %s = '%s';
            """ % (
                ', '.join([str(i) for i in cols]),
                str(table_name),
                str(filtr.col),
                normalize(string=filtr.val)
            )

        values = self.conn.cursor().execute(query).fetchall()[0]

        if values:
            return dict(zip(cols, values))
        else:
            raise NullReturnValue(
                "The query {%s} returned a null value." % (
                    query
                )
            )

    def select_generic_query(
        self,
        query: str,
        return_dtype: Literal['str', 'int', 'float', 'bool', 'list', 'dict'] = 'str'
    ) -> str | int | float | bool | list | dict:
        """ Returns the result of the SQL query as `return_dtype`.

        Parameters
        ----------
        query : `str`
            SQL-query string. If multiple records are returned, a `ValueError` is raised.
            If no records are returned, a `NullReturnValue` is raised.
        return_dtype : `Literal['str', 'int', 'float', 'bool', 'list', 'dict']`
            Name of the datatype (`str`, `int`, `float`, `bool`, `list`, `dict`) of
                the returned value. If the returned value cannot be converted
                to `return_dtype` then a `TypeError` is raised.
        """
        value = [
            i[0] for i in self.conn.cursor().execute(query).fetchall()
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
def parse_db_name(db_name: str) -> str:
    """ Parses `db_name` and ensures the database name contains a supported DBMS file-extension.

    Parameters
    ----------
    db_name : `str`
        Name of the database.
    """
    file_name, extension = os.path.splitext(db_name)

    if extension and extension.lower().replace('.', '') in DBMS.OPTIONS:
        return ''.join([file_name, extension.lower()])
    else:
        return '.'.join([file_name, DBMS.DEFAULT])


def normalize(
    string: str
) -> str:
    """ Applies all string-formatting to `string` returning the value as a `str`.

    Parameters
    ----------
    string: `str`
        String to format.
    """
    return escape_quote_char(string=string)


def escape_quote_char(
    string: str
) -> str:
    """ Escapes all single quote-characters found in `string` returning the final value as `str`.

    Parameters
    ----------
    string: `str`
        String to escape.
    """
    return str(string).replace("'", "''")
