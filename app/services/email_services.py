import asyncio
import datetime
import hashlib
import smtplib
import uuid

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import config
from app.logging_init import get_logger

logger = get_logger()


async def prepare_info_message(
    mail_type: str, email: str, name: str, phone: str, message: str
) -> tuple[str, str, str]:
    if mail_type == "hr":
        recipient = config.email.hr_email
        subject = """
            Предложение о партнёрстве - \n
            Форма обратной связи: хочу стать частью вашей команды
        """
    elif mail_type == "info":
        recipient = config.email.info_email
        subject = "Общая информация"
    else:
        raise ValueError("Invalid mail_type. Must be 'hr' or 'info'")

    email_body = f"""
        Имя: {name} \n
        Телефон: {phone} \n
        Email: {email} \n
        \n
        Сообщение: \n
        {message}
    """
    return recipient, subject, email_body


async def prepare_lk_access_message(email: str, first_name: str | None, last_name: str | None) -> tuple[str, str]:
    current_time = int(datetime.datetime.now().timestamp())
    password_uuid = str(uuid.uuid4())[:10]
    k_base_string = f"3ykOQzkL2X647dWw8dDx7h5c{email}{current_time}"
    k_hash = hashlib.md5(k_base_string.encode()).hexdigest()

    generated_link = (
        f"{config.frontend.users_login_url}?un={email}"
        f"&pw={password_uuid}&ln={last_name}"
        f"&fn={first_name}&mn="
        f"&g=&e={email}&t={current_time}"
        f"&k={k_hash}"
    )

    subject = "Доступ к Личному кабинету MIP"
    body = (
        f"Вы получили доступ к Личному кабинету на сайте mip.institute. \n"
        f"Перейдите по ссылке для его активации: {generated_link} \n"
        f"\n"
        f"Логин для входа: {email} \n"
        f"Пароль для входа: {password_uuid} \n"
        f"\n"
        f"\n"
        f"С Уважением, \n"
        f"Команда mip.institute"
    )

    return subject, body


def send_email_sync(recipient: str, subject: str, body: str) -> bool:
    try:
        smtp_user = config.smtp.user

        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = recipient
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(config.smtp.server, config.smtp.port) as server:
            server.starttls()
            server.login(smtp_user, config.smtp.password)
            server.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"Failed to send email to address {recipient}: {e}")
        return False


async def send_email(recipient: str, subject: str, body: str) -> bool:
    return await asyncio.to_thread(send_email_sync, recipient, subject, body)
