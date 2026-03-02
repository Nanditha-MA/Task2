import smtplib
from email.mime.text import MIMEText
from app.core.config import settings

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email

    server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
    server.starttls()
    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
    server.sendmail(settings.SMTP_FROM, to_email, msg.as_string())
    server.quit()