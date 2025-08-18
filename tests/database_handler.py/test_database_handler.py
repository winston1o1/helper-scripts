import unittest
from psycopg2.extras import RealDictCursor
from config import Config #import this to add the module to sys path

from database_handler.DatabaseHandler import DatabaseHandler as DB

class TestDatabaseHandler(unittest.TestCase):

    def setUp(self):
        # Set up any necessary test data or configurations
        self.connection = DB('.config.ini','db_server')
        self.query = 'SELECT 1 AS col1,2 AS col2;'

    def test_read_db_config(self):
        result = self.connection.read_db_config()
        self.assertTrue(result, "Read config file failed")

    def test_db_connection(self):
        self.connection.connect()
        result = self.connection.conn
        self.assertTrue(result is not None, "Database connection failed")

    def test_create_cursor(self):
        result = self.connection.get_cursor()
        self.assertTrue(result == self.connection.cursor, "Cursor creation failed")

    def test_execute_on_db(self):
        self.connection.execute(self.query)
        result = self.connection.cursor.fetchone()
        self.assertTrue(result, "Database execution failed")

    def test_fetchone(self):
        result = self.connection.fetchone(self.query)
        self.assertTrue(result, "Fetchone failed")

    def test_fetchone_with_custom_cursor(self):
        result = self.connection.fetchone(self.query,cursor_type=RealDictCursor)
        print(result)
        self.assertTrue(result, "Fetchone failed")

    def test_fetchall(self):
        result = self.connection.fetchall(self.query)
        self.assertTrue(result, "Fetch all failed")

    def test_close_connection(self):
        self.connection.close()
        
        self.assertTrue(self.connection.conn == self.connection.cursor == None, "Failed to close connection to DB")



if __name__ == "__main__":
    unittest.main()