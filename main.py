import json
import os

import config
import linkedin_scraper
import gmail_sender


def load_sent_log():
    if not os.path.exists(config.SENT_LOG_FILE):
        return set()

    with open(config.SENT_LOG_FILE, "r") as f:
        try:
            data = json.load(f)
            return set(data)
        except json.JSONDecodeError:
            return set()


def save_sent_log(sent_emails_set):

    with open(config.SENT_LOG_FILE, "w") as f:
        json.dump(list(sent_emails_set), f, indent=2)


def run_bot():
    """
    Main function — runs the full automation flow from login to email sending.
    """
    print("=" * 50)
    print("  LinkedIn Job Apply Bot — Starting")
    print("=" * 50)

    already_contacted = load_sent_log()
    print(f"[*] Loaded {len(already_contacted)} previously contacted email(s) from log.")

    driver = linkedin_scraper.create_driver()
    try:
        linkedin_scraper.login_to_linkedin(driver)
    except Exception:
        print("[!] Could not log into LinkedIn. Check your credentials in config.py / .env")
        driver.quit()
        return

    posts = linkedin_scraper.search_posts(
        driver,
        keyword=config.SEARCH_KEYWORD,
        max_posts=config.MAX_POSTS_TO_SCAN
    )
    driver.quit()
    print(f"[*] Browser closed. Total posts with emails found: {len(posts)}")

    new_posts = [p for p in posts if p["recruiter_email"] not in already_contacted]
    print(f"[*] New (not yet contacted) recruiters: {len(new_posts)}")

    if not new_posts:
        print("[*] Nothing new to send. Exiting.")
        return

    try:
        gmail_service = gmail_sender.get_gmail_service()
    except Exception as e:
        print(f"[!] Gmail authentication failed: {e}")
        return

    sent_count = 0
    for post in new_posts:
        email = post["recruiter_email"]
        url = post["post_url"]

        success = gmail_sender.send_email(gmail_service, email, url)

        if success:
            already_contacted.add(email)
            sent_count += 1

    save_sent_log(already_contacted)

    print("=" * 50)
    print(f"  Done! Emails sent this run: {sent_count}")
    print("=" * 50)


if __name__ == "__main__":
    run_bot()
