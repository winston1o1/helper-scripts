"""Shared pytest fixtures for database tests.

Provides the pytest equivalent of ``unittest``'s ``setUpClass`` /
``tearDownClass``: the dummy ``helper_scripts_users`` and
``helper_scripts_logs`` tables are created once per test session, made
available to every database test, and dropped when the session ends.
"""
import pytest

from database_handler.DatabaseHandler import DatabaseHandler as DB

TABLE_PREFIX = "helper_scripts_"
USERS_TABLE = TABLE_PREFIX + "users"
LOGS_TABLE = TABLE_PREFIX + "logs"


@pytest.fixture(scope="session")
def db():
    """Return a connected DatabaseHandler, closed at the end of the session."""
    handler = DB(".config.ini", "db_server")
    handler.connect()
    yield handler
    handler.close()


@pytest.fixture(scope="session")
def db_tables(db):
    """Create the dummy tables once and drop them at the end of the session.

    Yields a dict mapping ``"users"`` / ``"logs"`` to the generated table
    names, so tests can reference them without hardcoding the prefix.
    """
    db.execute(
        f"CREATE TABLE {USERS_TABLE} ("
        "id SERIAL PRIMARY KEY, "
        "username TEXT NOT NULL, "
        "email TEXT NOT NULL, "
        "created_at TIMESTAMP)"
    )
    db.execute(
        f"CREATE TABLE {LOGS_TABLE} ("
        "id SERIAL PRIMARY KEY, "
        "user_id INTEGER NOT NULL, "
        "level TEXT NOT NULL, "
        "message TEXT NOT NULL, "
        "created_at TIMESTAMP)"
    )
    db.execute(
        f"INSERT INTO {USERS_TABLE} (username, email, created_at) "
        "VALUES (%s, %s, %s), (%s, %s, %s)",
        args=(
            "alice", "alice@example.com", "2026-01-15 10:00:00",
            "bob", "bob@example.com", "2026-02-20 14:30:00",
        ),
    )
    db.execute(
        f"INSERT INTO {LOGS_TABLE} (user_id, level, message, created_at) "
        "VALUES (%s, %s, %s, %s), (%s, %s, %s, %s)",
        args=(
            1, "INFO", "user logged in", "2026-01-15 10:05:00",
            2, "WARNING", "password expiring soon", "2026-02-20 14:35:00",
        ),
    )
    db.commit()

    yield {"users": USERS_TABLE, "logs": LOGS_TABLE}

    db.rollback()
    db.execute(f"DROP TABLE IF EXISTS {LOGS_TABLE}")
    db.execute(f"DROP TABLE IF EXISTS {USERS_TABLE}")
    db.commit()
