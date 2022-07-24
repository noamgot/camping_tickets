import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import GLOBAL_CONFIG

mailer_config = GLOBAL_CONFIG["mailer"]

port = 465  # For SSL
password = mailer_config["gmail_password_token"]
sender_email = mailer_config["sender"]
receivers = mailer_config["receivers"]
if mailer_config.get("send_to_sender", False):
    receivers.append(sender_email)
receivers = ", ".join(receivers)
mail_subject = mailer_config["subject"]


def send_mail(text):
    message = MIMEMultipart("plain")
    message["Subject"] = mail_subject
    message["From"] = sender_email
    message["To"] = receivers

    # Turn these into plain/html MIMEText objects
    mime_text = MIMEText(text, "plain")
    message.attach(mime_text)

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receivers, message.as_string())


def send_error_mail():
    message = MIMEMultipart("plain")
    message["Subject"] = "📛 הסקריפט שלך נפל! 📛"
    message["From"] = sender_email
    message["To"] = sender_email

    # Turn these into plain/html MIMEText objects
    mime_text = MIMEText("Check this one please...", "plain")
    message.attach(mime_text)

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, sender_email, message.as_string())