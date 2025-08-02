import asyncio
import smtplib
from email.mime.text import MIMEText

from celery import Celery
from app.settings import SMTP_HOST, SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD

clry = Celery(
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)


@clry.task
def send_email(to_email: str, subject: str, body: str):
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

    except Exception as e:
        print(f"Failed to send email to {to_email}: {e!s}")


async def write_notification(email: str, message: str = ""):
    await asyncio.sleep(3)
    with open("log.txt", mode="a") as email_file:
        content = f"Notification for {email}: {message}\n"
        email_file.write(content)
