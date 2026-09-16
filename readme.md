# HELPER SCRIPTS
>>> Built for data professionals by data professionals.

Note: Despite the tagline, this package can be used by anyone.

## Installation

Install from PyPI (or your private index):

```bash
pip install helper_scripts
```

For local development, see [Development](#development) below.

## Configuration

`DatabaseHandler` and `SendMail` read their settings from a configuration
file. Both `.config.ini` (INI) and `.env` formats are supported and chosen
automatically by the file extension. Example files are included in this
repository (`.config.ini.example` and `.env.example`) — copy one to the matching
name and fill in your values.

### `.config.ini`

INI sections map directly to configuration keys:

```ini
[db_server]
host = localhost
port = 5432
dbname = my_database
user = postgres
password = your_password

[email_server]
smtp_server = smtp.example.com
port = 587
sender_email = you@example.com
sender_username = your_username
password = your_password
platform = example
```

### `.env`

`.env` files have no sections, so the section name becomes an uppercase prefix
separated from keys by a double underscore (`SECTION__KEY`). Keys are returned
lowercased, so `DB_SERVER__HOST` maps to `host`:

```env
DB_SERVER__HOST=localhost
DB_SERVER__PORT=5432
DB_SERVER__DBNAME=my_database
DB_SERVER__USER=postgres
DB_SERVER__PASSWORD=your_password
```

If the `.env` file is not found, the same variables are read from the live
operating system environment instead.

## Usage

### DatabaseHandler

Interact with a PostgreSQL database:

```python
from database_handler import DB

db = DB(".config.ini", "db_server")   # or DB(".env", "db_server")
db.connect()

rows = db.fetchall("SELECT id, username FROM users")
for row in rows:
    print(row[0], row[1])

db.execute("INSERT INTO logs (message) VALUES (%s)", args=("hello",))
db.commit()
db.close()
```

Bulk import/export with PostgreSQL `COPY`:

```python
db.copy_to("users.csv", "users")        # table -> file
db.copy_from("users.csv", "users")      # file -> table
db.sql_copy_to("COPY users TO STDOUT WITH CSV HEADER", "users.csv")
db.sql_copy_from(
    "COPY users (id, username) FROM STDIN WITH (FORMAT csv)", "users.csv"
)
```

Use `RealDictCursor` to fetch rows as dictionaries:

```python
from psycopg2.extras import RealDictCursor
rows = db.fetchall("SELECT * FROM users", cursor_type=RealDictCursor)
```

### SendMail

Send email (optionally with attachments):

```python
from send_mail import SendMail

result = SendMail.send_email(
    email_message="Hello, this is the body.",
    subject="Greetings",
    email_recepients=["someone@example.com"],
    file_attachments=["report.pdf"],   # optional
)
print(result)  # {'code': 200, 'message': 'Email should be sent successfully.'}
```

`send_email` reads SMTP settings from the `[email_server]` section (the primary
server) and falls back to `[secondary_server]` on retry.

### GoogleDrive

List, download, and upload files on Google Drive using a service account:

```python
from google_drive import worker

drive = worker(key_file_location="service_account.json")

files = drive.read_drive_files()                       # list files
drive.upload_file_to_drive(filename="report.xlsx", file_path="./report.xlsx")
drive.download_drive_file(filename="report.xlsx", download_path="./downloads")
```

### Legacy namespace

The `helper_scripts` package re-exports the top-level packages for
backward compatibility:

```python
from helper_scripts import DB, SendMail, worker
```

## Development

### Setup

```bash
git clone https://github.com/winston1o1/helper-scripts.git
cd helper-scripts
python -m venv .venv
```

Activate the environment and install with dev extras:

```bash
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"
```

### Running the tests

```bash
pytest
```

Coverage is collected automatically and the suite fails if total coverage drops
below **80%**.

### Test configuration notes

- Configuration is read from `.config.ini` (or `.env`). Copy
  `.config.ini.example` to `.config.ini` and point `[db_server]` at a reachable
  PostgreSQL instance before running the database tests.
- The `google_drive` tests are excluded from the default run
  (`--ignore=tests/google_drive_tests`) because they require a Google service
  account key file (`tests/google_drive_tests/service_account_dev.json`). Provide
  that file to run them locally.

## Packages

| Package | Purpose |
|---|---|
| `database_handler` | PostgreSQL connection, queries, and `COPY` operations |
| `send_mail` | SMTP email sending with attachments and retry/fallback |
| `google_drive` | Google Drive listing, upload, and download via service account |
| `excel_tooling` | Column-width helpers for spreadsheet writers |
| `helper_scripts` | Backward-compatible namespace re-exporting the above |
