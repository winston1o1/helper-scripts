import unittest
from config import Config #import this to add the module to sys path

from send_mail.SendMail import SendMail

class TestSendMail(unittest.TestCase):

    def setUp(self):
        # Set up any necessary test data or configurations
        self.email_message = "This is a test email."
        self.subject = "Test Email"
        self.email_recepients = []
        self.file_attachments = []
        self.secondary_email = 'email_server_inhouse'

    def test_send_mail_success(self):
        # Test sending an email successfully
        result = SendMail.send_email(self.email_message, self.subject, self.email_recepients)
        self.assertTrue(result, "Email should be sent successfully.")

    def test_send_mail_secondary_server_success(self):
        # Test sending an email successfully with the secondary server
        result = SendMail.send_email(self.email_message, 'Secondary Server works', self.email_recepients, file_attachments=self.file_attachments)
        self.assertTrue(result, "Email should be sent successfully.")

    def test_send_mail_invalid_server(self):
        # Test sending an email with an invalid email server
        with self.assertRaisesRegex(Exception, "No Secondary Email Server Name provided"):
            SendMail.send_email(self.email_message, self.subject, self.email_recepients, email_server='invalid_server')

    def test_send_mail_invalid_sender_username(self):
        # Test sending an email with an invalid sender username
        with self.assertRaises(Exception):
            SendMail.send_email(self.email_message, self.subject, self.email_recepients)

    def test_send_mail_empty_subject(self):
        # Test sending an email with an empty subject
        with self.assertRaisesRegex(Exception, "SMTPDataError"):
            SendMail.send_email(self.email_message, "", self.email_recepients)

    def test_send_mail_empty_message(self):
        # Test sending an email with an empty message
        with self.assertRaisesRegex(Exception, "SMTPDataError"):
            SendMail.send_email("", self.subject, self.email_recepients)

if __name__ == "__main__":
    unittest.main()
    # pass
