from datetime import datetime as dt
from os import path, remove

import pytest

from google_drive import worker, get_service

SECRETS_FILE_PATH = path.join(path.dirname(__file__), "service_account_dev.json")
API_NAME = "drive"
API_VERSION = "v3"
SCOPE_WRITE = "https://www.googleapis.com/auth/drive"


def test_create_service():
    try:
        service = get_service(
            api_name=API_NAME,
            api_version=API_VERSION,
            scopes=SCOPE_WRITE,
            key_file_location=SECRETS_FILE_PATH,
        )
        assert service is not None
    except Exception:
        pytest.fail("Could not create service")


def test_read_drive_files():
    worker_run = worker(key_file_location=SECRETS_FILE_PATH)
    result = worker_run.read_drive_files()
    assert result.get("code") == 200


def test_upload_file():
    worker_run = worker(key_file_location=SECRETS_FILE_PATH)
    filename = dt.now().strftime("%Y%m%d%H%M%S") + "test.txt"
    with open(filename, "w") as f:
        f.write("Hello World")

    result = worker_run.upload_file_to_drive(filename=filename, file_path=filename)
    code = result.get("code")
    remove(filename)
    assert code == 200


def test_download_file():
    worker_run = worker(key_file_location=SECRETS_FILE_PATH)
    filename = dt.now().strftime("%Y%m%d%H%M%S") + "test.txt"
    result = worker_run.download_drive_file(filename=filename, download_path=".")
    code = result.get("code")
    if path.exists(filename):
        remove(filename)

    assert code == 200
