import pytest

from send_mail.SendMail import SendMail


@pytest.fixture
def email_data():
    return {
        "email_message": "This is a test email.",
        "subject": "Test Email",
        "email_recepients": ["ntdootxfdyxfjkmr@ethereal.email"],
        "file_attachments": [],
    }


def test_send_mail_success(email_data):
    result = SendMail.send_email(
        email_data["email_message"],
        email_data["subject"],
        email_data["email_recepients"],
    )
    assert result


def test_send_mail_secondary_server_success(email_data):
    result = SendMail.send_email(
        email_data["email_message"],
        "Secondary Server works",
        email_data["email_recepients"],
        file_attachments=email_data["file_attachments"],
    )
    assert result


def test_send_mail_invalid_server(email_data):
    with pytest.raises(Exception, match="No Secondary Email Server Name provided"):
        SendMail.send_email(
            email_data["email_message"],
            email_data["subject"],
            email_data["email_recepients"],
            attempt=4,
            extra_email_server=None
        )