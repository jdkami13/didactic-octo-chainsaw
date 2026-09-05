"""Sends the digest by email via SMTP (e.g. Gmail)."""
import logging
import smtplib
from email.mime.text import MIMEText
from typing import Optional

logger = logging.getLogger(__name__)


def send_email(
    subject: str,
    body: str,
    to_addr: str,
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    from_addr: Optional[str] = None,
) -> bool:
    from_addr = from_addr or smtp_user
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_addr, [to_addr], msg.as_string())
        return True
    except (smtplib.SMTPException, OSError) as exc:
        logger.warning("Failed to send digest email: %s", exc)
        return False
