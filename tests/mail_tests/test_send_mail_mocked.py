import smtplib

import pytest

from send_mail.SendMail import SendMail


@pytest.fixture
def email_data():
    return {
        "email_message": "This is a test email.",
        "subject": "Test Email",
        "email_recepients": ["recipient@example.com"],
    }


class _FakeSMTP:
    """Minimal drop-in for ``smtplib.SMTP`` used as a context manager."""

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def starttls(self, *args, **kwargs):
        pass

    def login(self, *args, **kwargs):
        pass

    def sendmail(self, *args, **kwargs):
        return {}


class _FailingSMTP(_FakeSMTP):
    def sendmail(self, *args, **kwargs):
        raise smtplib.SMTPDataError(554, b"data error")


def test_send_mail_with_attachment(email_data, tmp_path, monkeypatch):
    attachment = tmp_path / "attach.txt"
    attachment.write_text("hello attachment")

    monkeypatch.setattr(smtplib, "SMTP", _FakeSMTP)
    result = SendMail.send_email(
        email_data["email_message"],
        email_data["subject"],
        email_data["email_recepients"],
        file_attachments=[str(attachment)],
    )
    assert result == {"code": 200, "message": "Email should be sent successfully."}


def test_send_mail_smtp_data_error_exhausts_retries(email_data, monkeypatch):
    monkeypatch.setattr(smtplib, "SMTP", _FailingSMTP)
    with pytest.raises(Exception, match="Emailing attempt stopped at 5 tries"):
        SendMail.send_email(
            email_data["email_message"],
            email_data["subject"],
            email_data["email_recepients"],
        )
