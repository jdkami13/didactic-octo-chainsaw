import smtplib
from unittest.mock import MagicMock, patch

from job_search_bot.mailer import send_email


def test_send_email_success():
    smtp_instance = MagicMock()
    smtp_cm = MagicMock()
    smtp_cm.__enter__.return_value = smtp_instance
    with patch("job_search_bot.mailer.smtplib.SMTP", return_value=smtp_cm) as smtp_ctor:
        result = send_email(
            subject="Test digest",
            body="1 new posting",
            to_addr="me@example.com",
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_user="me@example.com",
            smtp_password="app-password",
        )
    assert result is True
    smtp_ctor.assert_called_once_with("smtp.gmail.com", 587, timeout=20)
    smtp_instance.starttls.assert_called_once()
    smtp_instance.login.assert_called_once_with("me@example.com", "app-password")
    assert smtp_instance.sendmail.called


def test_send_email_handles_auth_failure_gracefully():
    smtp_cm = MagicMock()
    smtp_cm.__enter__.side_effect = smtplib.SMTPAuthenticationError(535, b"bad creds")
    with patch("job_search_bot.mailer.smtplib.SMTP", return_value=smtp_cm):
        result = send_email(
            subject="Test digest",
            body="1 new posting",
            to_addr="me@example.com",
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_user="me@example.com",
            smtp_password="wrong-password",
        )
    assert result is False
