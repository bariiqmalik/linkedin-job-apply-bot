import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import config


def create_driver():
    print("[*] Starting Chrome browser...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def login_to_linkedin(driver):
    print("[*] Navigating to LinkedIn login...")
    try:
        driver.get("https://www.linkedin.com/login")

        wait = WebDriverWait(driver, 15)

        email_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        email_field.clear()
        email_field.send_keys(config.LINKEDIN_EMAIL)

        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(config.LINKEDIN_PASSWORD)

        password_field.send_keys(Keys.RETURN)

        wait.until(EC.url_contains("feed"))
        print("[+] Logged in to LinkedIn successfully.")

    except Exception as e:
        print(f"[!] Login failed: {e}")
        raise


def is_within_24_hours(time_text):
    time_text = time_text.strip().lower()

    if "now" in time_text or "just" in time_text:
        return True

    if re.search(r"(\d+)\s*m", time_text):
        return True

    hour_match = re.search(r"(\d+)\s*h", time_text)
    if hour_match:
        hours = int(hour_match.group(1))
        return hours <= 23

    if re.search(r"\d+\s*d", time_text):
        return False

    if re.search(r"\d+\s*(w|mo|yr|y)", time_text):
        return False

    return True


def extract_email_from_text(text):
    pattern = r"[\w\.\-]+@[\w\.\-]+\.\w+"
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return None


def search_posts(driver, keyword, max_posts=20):
    print(f"[*] Searching LinkedIn posts for: '{keyword}'")

    search_url = (
        f"https://www.linkedin.com/search/results/content/"
        f"?keywords={keyword.replace(' ', '%20')}&sortBy=date_posted"
    )
    driver.get(search_url)

    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "search-results-container")))
    time.sleep(2)

    results = []
    scanned = 0

    while scanned < max_posts:
        post_cards = driver.find_elements(By.CSS_SELECTOR, ".search-results-container li")

        for card in post_cards:
            if scanned >= max_posts:
                break

            try:
                post_data = extract_post_data(card, driver)
            except Exception:
                scanned += 1
                continue

            if post_data:
                results.append(post_data)

            scanned += 1

        if scanned < max_posts:
            driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(2)
            new_cards = driver.find_elements(By.CSS_SELECTOR, ".search-results-container li")
            if len(new_cards) <= len(post_cards):
                break

    print(f"[+] Scanned {scanned} posts. Found {len(results)} with recruiter emails.")
    return results


def extract_post_data(card, driver):
    try:
        time_elem = card.find_element(By.CSS_SELECTOR, "span.update-components-actor__sub-description span[aria-hidden='true']")
        time_text = time_elem.text
    except Exception:
        time_text = "now"

    if not is_within_24_hours(time_text):
        return None

    try:
        text_elem = card.find_element(By.CSS_SELECTOR, ".update-components-text")
        post_text = text_elem.text
    except Exception:
        return None

    email = extract_email_from_text(post_text)
    if not email:
        return None

    try:
        link_elem = card.find_element(By.CSS_SELECTOR, "a.app-aware-link")
        post_url = link_elem.get_attribute("href")
    except Exception:
        post_url = driver.current_url

    return {
        "post_text": post_text,
        "recruiter_email": email,
        "post_url": post_url
    }
