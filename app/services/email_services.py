import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.logging_init import get_logger

logger = get_logger()


async def send_email_success(to_email: str, subject: str, body: str) -> bool:
    try:
        smtp_server = "smtp.yandex.com"
        smtp_port = 587
        smtp_user = "notify@mip.institute"
        smtp_password = os.getenv("EMAIL_PASSWORD")

        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"Failed to send email to address {to_email}: {e}")
        return False
