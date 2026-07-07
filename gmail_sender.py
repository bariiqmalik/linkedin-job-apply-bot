import os
import base64
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import config

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

EMAIL_TEMPLATE = """\
Dear Hiring Team,

I came across your post on LinkedIn and would love to express my interest in the {role} position.
I am {name}, and I believe my skills align well with what you're looking for.
Please find my resume attached for your consideration.
I look forward to connecting with you.

Best regards,
{name}
"""


def get_gmail_service():
    creds = None

    if os.path.exists(config.GMAIL_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(config.GMAIL_TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config.GMAIL_CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(config.GMAIL_TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    print("[+] Gmail API authenticated successfully.")
    return service


def build_email_message(to_email, recruiter_name="Hiring Team"):
    role = config.SEARCH_KEYWORD

    msg = MIMEMultipart()
    msg["To"] = to_email
    msg["From"] = config.YOUR_EMAIL
    msg["Subject"] = f"Application for {role}"

    body_text = EMAIL_TEMPLATE.format(name=config.YOUR_NAME, role=role)
    msg.attach(MIMEText(body_text, "plain"))

    attach_resume(msg, config.RESUME_PATH)

    raw_bytes = msg.as_bytes()
    raw_b64 = base64.urlsafe_b64encode(raw_bytes).decode("utf-8")
    return {"raw": raw_b64}


def attach_resume(msg, resume_path):
    if not os.path.exists(resume_path):
        print(f"[!] Resume not found at: {resume_path} — sending email without attachment.")
        return

    with open(resume_path, "rb") as resume_file:
        attachment = MIMEBase("application", "octet-stream")
        attachment.set_payload(resume_file.read())

    encoders.encode_base64(attachment)
    filename = os.path.basename(resume_path)
    attachment.add_header("Content-Disposition", f"attachment; filename={filename}")
    msg.attach(attachment)


def send_email(service, to_email, post_url):
    try:
        message = build_email_message(to_email)
        service.users().messages().send(userId="me", body=message).execute()
        print(f"[+] Email sent | To: {to_email} | Post: {post_url} | Status: SUCCESS")
        return True
    except Exception as e:
        print(f"[!] Failed to send email to {to_email} | Error: {e}")
        return False
