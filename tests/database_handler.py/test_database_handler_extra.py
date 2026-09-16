import pytest
import psycopg2
from psycopg2.extras import RealDictCursor

from database_handler.DatabaseHandler import DatabaseHandler as DB


@pytest.fixture
def connection():
    """Return a DatabaseHandler pointed at the local ``.config.ini``."""
    return DB(".config.ini", "db_server")


def test_init_unsupported_database_type():
    with pytest.raises(ValueError, match="Unsupported database type"):
        DB(".config.ini", "db_server", database_type="oracle")


def test_init_mariadb_type():
    handler = DB(".config.ini", "db_server", database_type="mariadb")
    assert handler.database_type == "mariadb"
    assert handler.cursor is None


def test_init_mysql_type():
    handler = DB(".config.ini", "db_server", database_type="mysql")
    assert handler.database_type == "mysql"
    assert handler.cursor is None


def test_commit_without_connection():
    handler = DB(".config.ini", "db_server")
    handler.commit()
    assert handler.conn is None


def test_rollback_without_connection():
    handler = DB(".config.ini", "db_server")
    handler.rollback()
    assert handler.conn is None


def test_close_without_connection():
    handler = DB(".config.ini", "db_server")
    handler.close()
    assert handler.conn is None and handler.cursor is None


def test_require_postgres_ok():
    handler = DB(".config.ini", "db_server")  # postgres is the default
    handler._require_postgres()


def test_require_postgres_raises_for_mariadb():
    handler = DB(".config.ini", "db_server", database_type="mariadb")
    with pytest.raises(NotImplementedError):
        handler._require_postgres()


def test_copy_methods_require_postgres():
    handler = DB(".config.ini", "db_server", database_type="mysql")
    with pytest.raises(NotImplementedError):
        handler.copy_to("out.csv", "users")
    with pytest.raises(NotImplementedError):
        handler.sql_copy_to("COPY users TO STDOUT", "out.csv")
    with pytest.raises(NotImplementedError):
        handler.sql_copy_from("COPY users FROM STDIN", "in.csv")
    with pytest.raises(NotImplementedError):
        handler.copy_from("in.csv", "users")


def test_execute_error_rolls_back_and_raises(connection):
    with pytest.raises(Exception):
        connection.execute("SELECT * FROM definitely_missing_table")


def test_fetchone_with_args(connection):
    row = connection.fetchone("SELECT 1 AS col1 WHERE 1=%s", args=(1,))
    assert row[0] == 1


def test_fetchall_with_args_only(connection):
    rows = connection.fetchall("SELECT 1 AS col1 WHERE 1=%s", args=(1,))
    assert rows[0][0] == 1


def test_fetchall_with_args_and_cursor(connection):
    rows = connection.fetchall(
        "SELECT 1 AS col1 WHERE 1=%s", cursor_type=RealDictCursor, args=(1,)
    )
    assert rows[0]["col1"] == 1


def test_copy_to(db, db_tables, tmp_path):
    out = tmp_path / "users.csv"
    db.copy_to(str(out), db_tables["users"])
    data = out.read_text()
    assert "alice" in data


def test_sql_copy_to(db, db_tables, tmp_path):
    out = tmp_path / "users_sql.csv"
    db.sql_copy_to(
        f"COPY {db_tables['users']} TO STDOUT WITH CSV HEADER", str(out)
    )
    assert "alice" in out.read_text()


def test_copy_from(db, db_tables, tmp_path):
    src = tmp_path / "in.csv"
    src.write_text("3,charlie,charlie@example.com,2026-03-01 10:00:00\n")
    db.copy_from(str(src), db_tables["users"])
    db.commit()
    row = db.fetchone(f"SELECT username FROM {db_tables['users']} WHERE id = 3")
    assert row[0] == "charlie"


def test_sql_copy_from(db, db_tables, tmp_path):
    src = tmp_path / "in_sql.csv"
    src.write_text("4,dave,dave@example.com,2026-03-02 10:00:00\n")
    db.sql_copy_from(
        f"COPY {db_tables['users']} (id, username, email, created_at) "
        "FROM STDIN WITH (FORMAT csv)",
        str(src),
    )
    db.commit()
    row = db.fetchone(f"SELECT username FROM {db_tables['users']} WHERE id = 4")
    assert row[0] == "dave"


def test_fetchone_with_cursor_and_args(connection):
    row = connection.fetchone(
        "SELECT 1 AS col1 WHERE 1=%s", cursor_type=RealDictCursor, args=(1,)
    )
    assert row["col1"] == 1


def test_fetchall_with_cursor_only(connection):
    rows = connection.fetchall("SELECT 1 AS col1", cursor_type=RealDictCursor)
    assert rows[0]["col1"] == 1


def test_connect_fatal_unsupported(monkeypatch):
    monkeypatch.setattr(psycopg2, "connect", lambda **kwargs: None)
    handler = DB(".config.ini", "db_server")
    with pytest.raises(SystemExit):
        handler.connect()


def test_connect_nonfatal_error(monkeypatch):
    def boom(**kwargs):
        raise psycopg2.OperationalError("connection refused")

    monkeypatch.setattr(psycopg2, "connect", boom)
    handler = DB(".config.ini", "db_server")
    with pytest.raises(psycopg2.OperationalError):
        handler.connect()


def test_copy_to_lazy_connect(db_tables, tmp_path):
    handler = DB(".config.ini", "db_server")
    out = tmp_path / "users_lazy.csv"
    handler.copy_to(str(out), db_tables["users"])
    assert "alice" in out.read_text()
    handler.close()


def test_sql_copy_to_lazy_connect(db_tables, tmp_path):
    handler = DB(".config.ini", "db_server")
    out = tmp_path / "users_lazy_sql.csv"
    handler.sql_copy_to(
        f"COPY {db_tables['users']} TO STDOUT WITH CSV HEADER", str(out)
    )
    assert "alice" in out.read_text()
    handler.close()


def test_sql_copy_from_lazy_connect(db_tables, tmp_path):
    handler = DB(".config.ini", "db_server")
    src = tmp_path / "in_lazy.csv"
    src.write_text("5,eve,eve@example.com,2026-03-03 10:00:00\n")
    handler.sql_copy_from(
        f"COPY {db_tables['users']} (id, username, email, created_at) "
        "FROM STDIN WITH (FORMAT csv)",
        str(src),
    )
    handler.commit()
    handler.close()


def test_copy_from_lazy_connect(db_tables, tmp_path):
    handler = DB(".config.ini", "db_server")
    src = tmp_path / "in_lazy2.csv"
    src.write_text("6,frank,frank@example.com,2026-03-04 10:00:00\n")
    handler.copy_from(str(src), db_tables["users"])
    handler.commit()
    handler.close()


def test_copy_to_error(db, tmp_path):
    out = tmp_path / "err.csv"
    with pytest.raises(Exception):
        db.copy_to(str(out), "nonexistent_table_xyz")


def test_sql_copy_to_error(db, tmp_path):
    out = tmp_path / "err_sql.csv"
    with pytest.raises(Exception):
        db.sql_copy_to("COPY nonexistent_table_xyz TO STDOUT", str(out))


def test_sql_copy_from_error(db, tmp_path):
    src = tmp_path / "err_in.csv"
    src.write_text("1,2,3,4\n")
    with pytest.raises(Exception):
        db.sql_copy_from("COPY nonexistent_table_xyz FROM STDIN", str(src))


def test_copy_from_error(db, tmp_path):
    src = tmp_path / "err_in2.csv"
    src.write_text("1,2,3,4\n")
    with pytest.raises(Exception):
        db.copy_from(str(src), "nonexistent_table_xyz")
