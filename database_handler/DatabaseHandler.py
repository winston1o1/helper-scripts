from typing import Any, Optional, Union, overload
import psycopg2
import sys

from .ConfigParser import ConfigHandler


# Import optional DB driver cursor classes
MariaCursor = Any
try:
    import mariadb
    MariaCursor = mariadb.Connection.cursor
except ImportError:
    MariaCursor = Any  # fallback

MySQLCursor = Any
try:
    import mysql.connector
    MySQLCursor = mysql.connector.cursor_cext.CMySQLCursor
except ImportError:
    MySQLCursor = Any  # fallback

# Postgres
PgCursor = psycopg2.extensions.cursor

# Union of all cursor types
CursorType = Union[PgCursor, MariaCursor, MySQLCursor]

class DatabaseHandler(object):

    @overload
    def __init__(self, config_file: str, config_file_section: str, database_type: str = "postgres") -> None: ...
    @overload
    def __init__(self, config_file: str, config_file_section: str, database_type: str = "mariadb") -> None: ...
    @overload
    def __init__(self, config_file: str, config_file_section: str, database_type: str = "mysql") -> None: ...
    
    def __init__(self, config_file, config_file_section,database_type='postgres'):
        self.config_file = config_file
        self.config_file_section = config_file_section
        self.database_type = database_type
        self.conn = None 
        # self.cursor:Optional[CursorType] = None
                # Typed cursor placeholder
        if database_type == "postgres":
            self.cursor: Optional[PgCursor] = None
        elif database_type == "mariadb":
            self.cursor: Optional[MariaCursor] = None # type: ignore
        elif database_type == "mysql":
            self.cursor: Optional[MySQLCursor] = None # type: ignore
        else:
            raise ValueError(f"Unsupported database type: {database_type}")

    
    def read_db_config(self):
        #get database section
        config_parser = ConfigHandler(self.config_file,self.config_file_section)
        db = config_parser.read_config()

        return db
    
    def connect(self):

        try:
            # read connection parameters
            params = self.read_db_config()
            if self.database_type == 'postgres':
                self.conn = psycopg2.connect(**params)

            if self.database_type == 'mariadb':
                import mariadb # type: ignore
                self.conn = mariadb.connect(**params)

            if self.database_type == 'mysql':
                import mysql.connector # type: ignore
                self.conn = mysql.connector.connect(**params)

            if self.conn is None:
                raise Exception("FATAL: Unsupported database type")
            
        except Exception as ex:
            if str(ex)[:6] == 'FATAL:':
                sys.exit("Database (%s) connection error: %s" % (self.database_type,str(ex)[8:]))
            else:
                raise ex

    @overload
    def get_cursor(self, cursor_type: None = None) -> PgCursor: ...
    @overload
    def get_cursor(self, cursor_type: None = None) -> MariaCursor: ... # type: ignore
    @overload
    def get_cursor(self, cursor_type: None = None) -> MySQLCursor: ... # type: ignore
    
    def get_cursor(self,cursor_type = None) -> CursorType:
        """Create a cursor
        :return: cursor
        """

        if self.conn is None or self.conn.closed:
            self.connect()

        curs = self.conn.cursor(cursor_factory=cursor_type)
        self.cursor = curs
        
        return curs

    def close(self):
        """Close the database connection"""
        if self.conn and not self.conn.closed:
            self.conn.close()
        self.conn = None
        self.cursor = None
        return

    def commit(self):
        """Commit currently open transaction"""
        if self.conn:
            self.conn.commit()
        return

    def rollback(self):
        """Roll back currently open transaction"""
        if self.conn:
            self.conn.rollback()
        return

    def execute(self, query,cursor_type=None, args=None):
        """Create a cursor, execute a query and return the cursor
        :param query: text of the statement to execute
        :param args: arguments to query
        :return: cursor
        """
        curs = self.get_cursor(cursor_type=cursor_type)

        curs = self.cursor

        try:
            if args:
                return curs.execute(query, args)
            else:
                return curs.execute(query)
        except Exception as exc:
            if self.conn:
                self.rollback()
                self.close()

            raise exc


    def fetchone(self, query, cursor_type=None,args=None):
        """Execute a single row SELECT query and return row
        :param query: a SELECT query to be executed
        :param args: arguments to query
        :return: a psycopg2 DictRow
        The cursor is closed.
        """
        if cursor_type is None:
            if args:
                self.execute(query, args=args)
            else:
                self.execute(query)
        else:
            if args:
                self.execute(query, cursor_type=cursor_type, args=args)
            else:
                self.execute(query, cursor_type=cursor_type)

        row = self.cursor.fetchone()
        self.cursor.close()
        return row

    def fetchall(self, query, cursor_type=None, args=None):
        """Execute a SELECT query and return rows
        :param query: a SELECT query to be executed
        :param args: arguments to query
        :return: a list of psycopg2 DictRow's
        The cursor is closed.
        """
        if cursor_type is None:
            if args:
                self.execute(query, args=args)
            else:
                self.execute(query)
        else:
            if args:
                self.execute(query, cursor_type=cursor_type, args=args)
            else:
                self.execute(query, cursor_type=cursor_type)

        rows = self.cursor.fetchall()
        self.cursor.close()
        return rows

    def _require_postgres(self):
        """Raise if the handler is not configured for PostgreSQL.

        The COPY methods rely on psycopg2 cursor methods (``copy_to``,
        ``copy_from``, ``copy_expert``), which do not exist on the MariaDB
        or MySQL drivers.

        :raises NotImplementedError: if ``self.database_type`` is not ``"postgres"``
        """
        if self.database_type != "postgres":
            raise NotImplementedError(
                "COPY operations are only supported for PostgreSQL, not '%s'"
                % self.database_type
            )

    def copy_to(self, path, table, sep=','):
        """Copy a whole table to a local file (PostgreSQL only).

        Uses psycopg2's ``cursor.copy_to``, which streams the server-side
        ``COPY <table> TO STDOUT`` result into ``path``.

        :param path: destination file to write the data into (opened as text)
        :param table: possibly schema-qualified table name to export
        :param sep: column separator used in the output (default: ',')
        :raises NotImplementedError: if the handler is not configured for PostgreSQL
        """
        self._require_postgres()

        if self.conn is None or self.conn.closed:
            self.connect()
        if self.cursor is None or self.cursor.closed:
            self.get_cursor()

        with open(path, 'w') as f:
            curs = self.cursor
            try:
                curs.copy_to(f, table, sep)
            except Exception:
                curs.close()
                self.rollback()
                raise

    def sql_copy_to(self, sql, path):
        """Execute a raw SQL ``COPY ... TO STDOUT`` command to a file (PostgreSQL only).

        Uses psycopg2's ``cursor.copy_expert``, which allows a full COPY
        statement (custom ``FORMAT``, ``HEADER``, ``DELIMITER``, or a filtered
        ``SELECT``) rather than just a table name.

        :param sql: a complete ``COPY ... TO STDOUT`` statement
        :param path: destination file to write the data into (opened as text)
        :raises NotImplementedError: if the handler is not configured for PostgreSQL
        """
        self._require_postgres()

        if self.conn is None or self.conn.closed:
            self.connect()

        if self.cursor is None or self.cursor.closed:
            self.get_cursor()

        with open(path, 'w') as f:
            curs = self.cursor
            try:
                curs.copy_expert(sql, f)
            except Exception:
                curs.close()
                self.rollback()
                raise
    
    def sql_copy_from(self, sql, path):
        """Execute a raw SQL ``COPY ... FROM STDIN`` command from a file (PostgreSQL only).

        Uses psycopg2's ``cursor.copy_expert`` to load data from ``path`` into
        the database using a full COPY statement.

        :param sql: a complete ``COPY ... FROM STDIN`` statement
        :param path: source file to read the data from (opened as text)
        :raises NotImplementedError: if the handler is not configured for PostgreSQL
        """
        self._require_postgres()

        if self.conn is None or self.conn.closed:
            self.connect()

        if self.cursor is None or self.cursor.closed:
            self.get_cursor()

        with open(path, 'r') as f:
            curs = self.cursor
            try:
                curs.copy_expert(sql, f)
            except Exception:
                curs.close()
                self.rollback()
                raise

    def copy_from(self, path, table, sep=','):
        """Copy a whole table from a local file (PostgreSQL only).

        Uses psycopg2's ``cursor.copy_from``, which streams the contents of
        ``path`` into ``table`` via the server-side ``COPY <table> FROM STDIN``.

        :param path: source file to read the data from (opened as text)
        :param table: possibly schema-qualified table name to import into
        :param sep: column separator used in the input (default: ',')
        :raises NotImplementedError: if the handler is not configured for PostgreSQL
        """
        self._require_postgres()

        if self.conn is None or self.conn.closed:
            self.connect()

        if self.cursor is None or self.cursor.closed:
            self.get_cursor()

        with open(path, 'r') as f:
            curs = self.cursor
            try:
                curs.copy_from(f, table, sep)
            except Exception:
                curs.close()
                self.rollback()
                raise