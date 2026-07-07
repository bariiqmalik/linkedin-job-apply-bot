import os
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL", "your_linkedin_email@example.com")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "your_linkedin_password")

SEARCH_KEYWORD = os.getenv("SEARCH_KEYWORD", "Java Developer Contract")

MAX_POSTS_TO_SCAN = int(os.getenv("MAX_POSTS_TO_SCAN", "20"))

RESUME_PATH = os.getenv("RESUME_PATH", "resume.pdf")

YOUR_NAME = os.getenv("YOUR_NAME", "Your Name")

YOUR_EMAIL = os.getenv("YOUR_EMAIL", "your_gmail@gmail.com")

GMAIL_CREDENTIALS_FILE = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")

GMAIL_TOKEN_FILE = os.getenv("GMAIL_TOKEN_FILE", "token.json")

SENT_LOG_FILE = "sent_log.json"
