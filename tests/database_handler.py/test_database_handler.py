import pytest
from psycopg2.extras import RealDictCursor

from database_handler.DatabaseHandler import DatabaseHandler as DB

QUERY = 'SELECT 1 AS col1,2 AS col2;'


@pytest.fixture
def connection():
    """Return a DatabaseHandler pointed at the local ``.config.ini``."""
    return DB('.config.ini', 'db_server')


def test_read_db_config(connection):
    assert connection.read_db_config()


def test_db_connection(connection):
    connection.connect()
    assert connection.conn is not None


def test_create_cursor(connection):
    result = connection.get_cursor()
    assert result == connection.cursor


def test_execute_on_db(connection):
    connection.execute(QUERY)
    assert connection.cursor.fetchone()


def test_fetchone(connection):
    assert connection.fetchone(QUERY)


def test_fetchone_with_custom_cursor(connection):
    assert connection.fetchone(QUERY, cursor_type=RealDictCursor)


def test_fetchall(connection):
    assert connection.fetchall(QUERY)


def test_close_connection(connection):
    connection.close()
    assert connection.conn is None and connection.cursor is None


def test_dummy_tables_populated(db, db_tables):
    users = db.fetchall(f"SELECT COUNT(*) FROM {db_tables['users']}")
    logs = db.fetchall(f"SELECT COUNT(*) FROM {db_tables['logs']}")
    assert users[0][0] == 2
    assert logs[0][0] == 2
