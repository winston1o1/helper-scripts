
# 📧 SendMail Utility

## Overview

`SendMail` is a utility class for sending emails with optional attachments, configurable through a `.config.ini` file. It supports retrying email delivery using a secondary email server in the event of SMTP errors.

This module is intended for developers who want to programmatically send emails from Python applications with minimal setup.

---

## 📦 Prerequisites

- Python 3.6+
- `smtplib`, `ssl`, and `email` (all standard libraries)
- A `.config.ini` file in your working directory with the appropriate email server configuration

---

## 🛠️ Installation

Clone or download the package into your project directory.

Make sure your `.config.ini` file looks something like this:

```ini
[email_server]
smtp_server = smtp.example.com
port = 587
sender_email = your_email@example.com
sender_username = your_username
password = your_password
platform = example

[secondary_server]
smtp_server = smtp.backup.com
port = 587
sender_email = backup_email@example.com
sender_username = backup_username
password = backup_password
platform = backup
```

---

## ✉️ Usage

```python
from send_mail.SendMail import SendMail

email_body = "This is a test message."
subject = "Test Email"
recipients = ["recipient@example.com"]
attachments = ["./report.pdf", "./log.txt"]  # Optional

result = SendMail.send_email(
    email_message=email_body,
    subject=subject,
    email_recepients=recipients,
    file_attachments=attachments,
    email_server='email_server',
    extra_email_server='secondary_server'
)

print(result)
```

---

## 🔍 Method Reference

### `SendMail.send_email(...)`

Send an email with HTML content and optional file attachments.

**Parameters:**

| Name                 | Type        | Description                                                                 |
|----------------------|-------------|-----------------------------------------------------------------------------|
| `email_message`      | `str`       | The HTML message body of the email                                         |
| `subject`            | `str`       | Email subject line                                                         |
| `email_recepients`   | `list[str]` | List of recipient email addresses                                          |
| `file_attachments`   | `list[str]` | (Optional) List of file paths to attach to the email                       |
| `attempt`            | `int`       | (Optional) Retry counter, defaults to `0`. Handled internally.             |
| `email_server`       | `str`       | The name of the primary config section in `.config.ini`                    |
| `extra_email_server` | `str`       | The name of the secondary config section (used if primary fails)           |

**Returns:**

- `{'code': 200, 'message': 'Email should be sent successfully.'}` on success
- `{'code': SMTP_CODE, 'message': SMTP_ERROR}` on failure after 5 retries

---

## 🔁 Retry Mechanism

The function will retry up to 5 times on SMTP failures. The first two attempts use the primary email server, and subsequent ones use the secondary (if provided). If both servers fail after 5 tries, the final error is returned.

---

## 📎 Attachments

- File paths must point to accessible files.
- Each file is attached with MIME encoding using `application/octet-stream`.

---

## ⚠️ Error Handling

- SMTP errors like `SMTPDataError` are caught and retried.
- Missing configuration or invalid servers raise exceptions.
- If `extra_email_server` is `None`, fallback will be skipped.

---

## 🧩 ConfigHandler Dependency

This class depends on `ConfigHandler` in `send_mail/ConfigParser.py` with the following API:

```python
class ConfigHandler:
    def __init__(self, config_file: str, section: str):
        ...
    def read_config(self) -> dict:
        ...
```

---

## ✅ Best Practices

- Use environment variables or secrets manager to store sensitive credentials.
- Always validate your config before deploying to production.
- Avoid retry loops deeper than necessary to reduce unnecessary mail server load.
