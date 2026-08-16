"""Send the digest via Gmail SMTP using an app password.

Reads credentials from environment variables (set as GitHub Actions secrets):
  GMAIL_USER      - your gmail address (also the sender)
  GMAIL_APP_PASS  - 16-char Gmail app password (NOT your login password)
  MAIL_TO         - recipient (can be the same gmail address)
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(subject, html_body):
    user = os.environ["GMAIL_USER"]
    app_pass = os.environ["GMAIL_APP_PASS"]
    to_addr = os.environ.get("MAIL_TO", user)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_addr
    msg.attach(MIMEText("Your email client does not support HTML.", "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(user, app_pass)
        server.sendmail(user, [a.strip() for a in to_addr.split(",")], msg.as_string())
    print(f"[mailer] sent to {to_addr}")
