from playwright.sync_api import sync_playwright
from config import LINKEDIN_EMAIL, LINKEDIN_PASSWORD

def login():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=500
        )

        page = browser.new_page(viewport={"width": 1400, "height": 900})

        print("=" * 60)
        print("LinkedIn Login Automation")
        print("=" * 60)

        print("\nOpening LinkedIn...")
        page.goto(
            "https://www.linkedin.com/login",
            wait_until="domcontentloaded"
        )

        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)

        print("Current URL :", page.url)
        print("Page Title  :", page.title())

        print("\nTyping Email...")
        page.get_by_role(
            "textbox",
            name="Email or phone"
        ).fill(LINKEDIN_EMAIL)

        print("Typing Password...")
        page.get_by_role(
            "textbox",
            name="Password"
        ).fill(LINKEDIN_PASSWORD)

        print("Clicking Sign In...")
        page.get_by_role(
            "button",
            name="Sign in",
            exact=True
        ).click()

        print("\nWaiting for login...")

        page.wait_for_timeout(10000)

        print("Current URL :", page.url)

        page.screenshot(
            path="data/screenshots/after_login.png",
            full_page=True
        )

        print("Screenshot saved.")

        input("\nPress ENTER to close browser...")

        browser.close()

if __name__ == "__main__":
    login()