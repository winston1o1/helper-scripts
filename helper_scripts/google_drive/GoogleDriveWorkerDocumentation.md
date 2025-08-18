
# 📦 Google Drive Worker – Documentation

## Overview

The `worker` class provides a convenient interface to interact with the Google Drive API. It supports:

- Reading metadata of files stored on Google Drive
- Downloading and exporting files
- Uploading local files to Google Drive
- Managing file permissions
- Deleting files

It uses a service account for authentication and supports scoped access (read-only or read/write).

---

## 🔧 Setup

### Requirements

- Python 3.6+
- A valid Google Cloud service account JSON key
- `google-api-python-client` installed

```
pip install google-api-python-client
```

### Folder Structure (example)

```
.
├── google_drive.py        # contains the get_service function
├── your_script.py         # where you instantiate and use the worker
├── credentials.json       # your service account key file
```

---

## 🚀 Getting Started

### Instantiating the Worker

```python
from your_module import worker

drive = worker(
    api_name='drive',
    api_version='v3',
    key_file_location='path/to/credentials.json'
)
```

---

## 🔑 Authentication Scopes

- `scope_readonly`: Read-only access to file metadata.
- `scope_write`: Full read/write access to Google Drive.

---

## 📄 Method Summary

### `construct_service(scope: str)`

Creates an authenticated Google Drive service using the provided scope.

---

### `read_drive_files(scope, file_id=None, filename=None, ignore_trashed=True)`

Searches for files in Google Drive.

#### Parameters:
- `file_id` *(str)*: Optional. Fetch a specific file by ID.
- `filename` *(str)*: Optional. Filter by name substring.
- `ignore_trashed` *(bool)*: Defaults to `True`. If `False`, includes trashed files.

#### Returns:
```json
{'code': 200, 'items': [...]}
```

---

### `download_drive_file(file_id=None, filename=None, download_path=None, export=False, filetype=None, mimetype=None, export_name=None)`

Downloads a file by ID or name. Can also export Google Docs formats to other types.

#### Parameters:
- `file_id` or `filename`: One must be provided.
- `download_path` *(str)*: Where to save the file (defaults to current directory).
- `export` *(bool)*: If `True`, converts Google Docs to desired format.
- `filetype` *(str)*: E.g., `"pdf"`, `"csv"` (used for export).
- `mimetype` *(str)*: Optional MIME type (overrides auto-detection).
- `export_name` *(str)*: Optional custom name for exported file.

#### Returns:
```json
{'code': 200, 'message': 'download complete'}
```

---

### `upload_file_to_drive(filename, file_path, parent_folder_id=None, mimetype=None)`

Uploads a file to Google Drive.

#### Parameters:
- `filename` *(str)*: The name to assign to the uploaded file.
- `file_path` *(str)*: Path to the local file.
- `parent_folder_id` *(str)*: Optional Drive folder ID.
- `mimetype` *(str)*: Optional MIME type (auto-detected if not provided).

#### Returns:
```json
{'code': 200, 'message': 'upload complete'}
```

---

### `get_file_permissions(file_id)`

Retrieves permission details of a Drive file.

#### Parameters:
- `file_id` *(str)*: The ID of the file.

#### Returns:
```json
{'code': 200, 'item': {...}}
```

---

### `delete_drive_files(file_ids=[], reset=False)`

Deletes files from Google Drive.

#### Parameters:
- `file_ids` *(list[str])*: List of file IDs to delete.
- `reset` *(bool)*: If `True`, deletes **all** files (use with caution).

#### Returns:
```json
{'code': 200, 'message': 'X files deleted', 'errors': [...]}
```

---

## 📚 MIME Type Support

| Extension | MIME Type |
|-----------|------------|
| xlsx      | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| csv       | `text/csv` |
| xls       | `application/vnd.ms-excel` |
| pdf       | `application/pdf` |

---

## ⚠️ Error Handling

All methods return:
- `code = 200` on success
- `code = -999` on failure, with an `error` field

---

## ✅ Example Usage

```python
# Read file metadata
result = drive.read_drive_files(filename='report')
print(result)

# Download a file
drive.download_drive_file(filename='report.pdf')

# Upload a file
drive.upload_file_to_drive(
    filename='new_upload.pdf',
    file_path='/path/to/local/file.pdf'
)

# Get permissions
permissions = drive.get_file_permissions(file_id='abc123')

# Delete files
drive.delete_drive_files(file_ids=['abc123', 'def456'])
```

---

## 🛠 Known TODOs
- Add support to check for existing files before upload
- Improve error details
- Add support for paginated results from Drive API
