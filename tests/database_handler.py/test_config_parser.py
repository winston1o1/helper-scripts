import pytest

from database_handler.ConfigParser import ConfigHandler


def test_env_prefix():
    assert ConfigHandler._env_prefix("db_server") == "DB_SERVER__"
    assert ConfigHandler._env_prefix("my-section.x") == "MY_SECTION_X__"


def test_parse_dotenv(tmp_path):
    f = tmp_path / ".env"
    f.write_text(
        "DB_SERVER__HOST=localhost\n"
        "DB_SERVER__PORT=5433\n"
        "# a comment line\n"
        "DB_SERVER__NAME=\"quoted value\"\n"
        "DB_SERVER__FLAG='single'\n"
        "\n"
        "NO_EQUALS_LINE\n"
    )
    result = ConfigHandler._parse_dotenv(str(f))
    assert result["DB_SERVER__HOST"] == "localhost"
    assert result["DB_SERVER__PORT"] == "5433"
    assert result["DB_SERVER__NAME"] == "quoted value"
    assert result["DB_SERVER__FLAG"] == "single"


def test_read_env_config_from_file(tmp_path):
    f = tmp_path / "db.env"
    f.write_text("DB_SERVER__HOST=localhost\nDB_SERVER__PORT=5433\n")
    config = ConfigHandler(str(f), "db_server").read_config()
    assert config["host"] == "localhost"
    assert config["port"] == "5433"


def test_read_env_config_from_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_SERVER__HOST", "envhost")
    monkeypatch.setenv("DB_SERVER__PORT", "9999")
    # Non-existent .env file -> falls back to the live environment.
    config = ConfigHandler(str(tmp_path / "missing.env"), "db_server").read_config()
    assert config["host"] == "envhost"
    assert config["port"] == "9999"


def test_read_env_config_no_vars(tmp_path):
    f = tmp_path / "empty.env"
    f.write_text("# no matching vars\nSOMETHING_ELSE=1\n")
    with pytest.raises(Exception, match="No DB_SERVER__"):
        ConfigHandler(str(f), "db_server").read_config()


def test_read_ini_config_missing_section():
    with pytest.raises(Exception, match="Section nope not found"):
        ConfigHandler(".config.ini", "nope").read_config()
