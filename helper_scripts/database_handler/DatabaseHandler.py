import psycopg2
from psycopg2.extras import DictCursor
import sys

from database_handler.ConfigParser import ConfigHandler


class DatabaseHandler(object):

    def __init__(self, config_file, config_file_section,database_type='postgres'):
        self.config_file = config_file
        self.config_file_section = config_file_section
        self.database_type = database_type
        self.conn = None 
        self.cursor = None

    
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

    def get_cursor(self,cursor_type = DictCursor):
        """Create a cursor
        :return: cursor
        """
        # if self.cursor is not None:
        #     self.cursor.close()
        #     self.cursor = None

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

    def execute(self, query,args=None):
        """Create a cursor, execute a query and return the cursor
        :param query: text of the statement to execute
        :param args: arguments to query
        :return: cursor
        """
        if self.cursor:
            curs = self.cursor
        else:
            curs = self.get_cursor()

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


    def fetchone(self, query, args=None):
        """Execute a single row SELECT query and return row
        :param query: a SELECT query to be executed
        :param args: arguments to query
        :return: a psycopg2 DictRow
        The cursor is closed.
        """
        curs = self.execute(query, args)
        row = curs.fetchone()
        curs.close()
        return row

    def fetchall(self, query, args=None):
        """Execute a SELECT query and return rows
        :param query: a SELECT query to be executed
        :param args: arguments to query
        :return: a list of psycopg2 DictRow's
        The cursor is closed.
        """
        curs = self.execute(query, args)
        rows = curs.fetchall()
        curs.close()
        return rows

    def copy_to(self, path, table, sep=','):
        """Execute a COPY command to a file
        :param path: file name/path to copy into
        :param table: possibly schema qualified table name
        :param sep: separator between columns
        """
        if self.conn is None or self.conn.closed:
            self.connect()
        with open(path, 'w') as f:
            curs = self.conn.cursor()
            try:
                curs.copy_to(f, table, sep)
            except:
                curs.close()
                raise

    def sql_copy_to(self, sql, path):
        """Execute an SQL COPY command to a file
        :param sql: SQL copy command
        :param path: file name/path to copy into
        """
        if self.conn is None or self.conn.closed:
            self.connect()
        with open(path, 'w') as f:
            curs = self.conn.cursor()
            try:
                curs.copy_expert(sql, f)
            except:
                curs.close()
                raise
    
    def sql_copy_from(self, sql, path):
        """Execute an SQL COPY command from a file
        :param sql: SQL copy command
        :param path: file name/path to copy from
        """
        if self.conn is None or self.conn.closed:
            self.connect()
        with open(path, 'r') as f:
            curs = self.conn.cursor()
            try:
                curs.copy_expert(sql, f)
            except:
                curs.close()
                raise

    def copy_from(self, path, table, sep=','):
        """Execute a COPY command from a file
        :param path: file name/path to copy from
        :param table: possibly schema qualified table name
        :param sep: separator between columns
        """
        if self.conn is None or self.conn.closed:
            self.connect()
        with open(path, 'r') as f:
            curs = self.conn.cursor()
            try:
                curs.copy_from(f, table, sep)
            except:
                curs.close()
                raise