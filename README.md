# LinkedIn Job Apply Bot 🤖

A beginner-friendly Python script that automatically scans recent LinkedIn posts matching
your job keyword, finds recruiter email addresses in those posts, and sends them your resume
via Gmail — without ever storing your Gmail password.

---

## Project Structure

```
linkedin_job_apply_bot/
├── config.py             # Loads settings from .env
├── linkedin_scraper.py   # Selenium: login, search, extract emails
├── gmail_sender.py       # Gmail API: OAuth login, build & send emails
├── main.py               # Main runner — ties everything together
├── sent_log.json         # Auto-updated list of already-contacted emails
├── requirements.txt      # Python dependencies
├── .env.example          # Template for your credentials
└── README.md             # This file
```

---

## Prerequisites

- Python 3.9 or higher
- Google Chrome installed
- A Gmail account (the one you'll send from)
- A LinkedIn account
- Your resume as a PDF file

---

## Step 1 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 2 — Set Up Gmail OAuth Credentials

This bot uses the **official Gmail API** instead of your Gmail password, which means emails
are sent securely and won't be flagged as spam.

### 2.1 — Create a Google Cloud Project

1. Go to [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Name it anything (e.g. `linkedin-bot`) and click **Create**

### 2.2 — Enable the Gmail API

1. In the Cloud Console, go to **APIs & Services → Library**
2. Search for **Gmail API**
3. Click on it and press **Enable**

### 2.3 — Set Up OAuth Consent Screen

1. Go to **APIs & Services → OAuth consent screen**
2. Choose **External** → click **Create**
3. Fill in:
   - App name: `LinkedIn Bot` (anything works)
   - User support email: your Gmail
   - Developer contact email: your Gmail
4. Click **Save and Continue** through all remaining steps (no need to add scopes manually here)
5. On the **Test Users** step, click **Add Users** and add your own Gmail address
6. Click **Save and Continue**

### 2.4 — Create OAuth 2.0 Credentials

1. Go to **APIs & Services → Credentials**
2. Click **+ Create Credentials → OAuth Client ID**
3. Application type: **Desktop app**
4. Name it anything → click **Create**
5. Click **Download JSON** on the popup
6. Rename the downloaded file to `credentials.json`
7. Move `credentials.json` into your `linkedin_job_apply_bot/` folder

### 2.5 — First Run (Browser OAuth Login)

On the **very first run**, the script will open a browser window asking you to
log in to Google and approve access. After you approve:
- A `token.json` file is saved automatically
- All future runs will use this token silently (no browser popup needed)

> ⚠️ **Never share `token.json` or `credentials.json` with anyone.**

---

## Step 3 — Configure Your Settings

Copy the example env file and fill in your details:

```bash
# On Windows:
copy .env.example .env

# On Mac/Linux:
cp .env.example .env
```

Then open `.env` and update all values:

```env
LINKEDIN_EMAIL=you@example.com
LINKEDIN_PASSWORD=your_linkedin_password

SEARCH_KEYWORD=Java Developer Contract
MAX_POSTS_TO_SCAN=20

RESUME_PATH=resume.pdf       # or full path like C:/Users/You/resume.pdf
YOUR_NAME=John Doe
YOUR_EMAIL=you@gmail.com

GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
```

Also place your **resume PDF** in the project folder (or update `RESUME_PATH` with the full path).

---

## Step 4 — Run the Bot

```bash
python main.py
```

### What happens:

1. Chrome opens and logs into LinkedIn
2. Searches for posts matching your keyword, sorted by latest
3. Skips posts older than 24 hours
4. Extracts any email addresses found in post text
5. Opens a browser for Gmail OAuth (first run only)
6. Sends your resume to each new recruiter email found
7. Saves contacted emails to `sent_log.json` to avoid duplicates

### Example console output:

```
==================================================
  LinkedIn Job Apply Bot — Starting
==================================================
[*] Loaded 3 previously contacted email(s) from log.
[*] Starting Chrome browser...
[+] Logged in to LinkedIn successfully.
[*] Searching LinkedIn posts for: 'Java Developer Contract'
[+] Scanned 20 posts. Found 4 with recruiter emails.
[*] Browser closed. Total posts with emails found: 4
[*] New (not yet contacted) recruiters: 2
[+] Gmail API authenticated successfully.
[+] Email sent | To: recruiter@company.com | Post: https://linkedin.com/... | Status: SUCCESS
[+] Email sent | To: hiring@startup.io | Post: https://linkedin.com/... | Status: SUCCESS
==================================================
  Done! Emails sent this run: 2
==================================================
```

---

## How Duplicate Prevention Works

Every time an email is sent successfully, the recruiter's email address is added to
`sent_log.json`. On the next run, the bot reads this file and skips any email that's
already in the list — so you'll never double-email the same person.

---

## Tips & Troubleshooting

| Problem | Fix |
|---|---|
| Chrome crashes on start | Make sure Chrome is installed and up to date |
| Login fails | Check your LinkedIn credentials in `.env` |
| "credentials.json not found" | Make sure the file is in the project folder |
| Gmail OAuth window doesn't open | Check that your Google account is added as a Test User |
| No posts found | Try a broader keyword or increase `MAX_POSTS_TO_SCAN` |
| Resume not attached | Check that `RESUME_PATH` points to an existing PDF file |

---

## Important Notes

- **LinkedIn rate limits**: Don't set `MAX_POSTS_TO_SCAN` above 30 in one run.
- **LinkedIn ToS**: Automated scraping may violate LinkedIn's terms of service. Use responsibly.
- **Gmail API quota**: Free tier allows ~1 billion quota units/day — more than enough for daily runs.

---

## File Safety Checklist

Before committing to GitHub, add these to your `.gitignore`:

```
.env
credentials.json
token.json
resume.pdf
sent_log.json
```
