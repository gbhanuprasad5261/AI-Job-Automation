from playwright.sync_api import sync_playwright
from config import LINKEDIN_EMAIL, LINKEDIN_PASSWORD


def search_jobs():
    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            slow_mo=500
        )

        page = browser.new_page(viewport={"width": 1400, "height": 900})

        # Login
        print("Opening LinkedIn...")
        page.goto("https://www.linkedin.com/login")

        print("Typing Email...")
        page.get_by_role("textbox", name="Email or phone").fill(LINKEDIN_EMAIL)

        print("Typing Password...")
        page.get_by_role("textbox", name="Password").fill(LINKEDIN_PASSWORD)

        print("Clicking Sign In...")
        page.get_by_role("button", name="Sign in", exact=True).click()

        page.wait_for_url("**/feed/**", timeout=60000)

        print("Login Successful!")

        # Jobs
        print("Opening Jobs page...")
        page.goto("https://www.linkedin.com/jobs/")
        page.wait_for_timeout(5000)
        print(page.url)
        page.screenshot(path="jobs_page.png")

        # Search
        print("Searching jobs...")

        search_box = page.get_by_placeholder("Describe the job you want")
        search_box.click()
        search_box.fill("Java Backend Developer")
        page.keyboard.press("Enter")

        page.wait_for_timeout(5000)

        print(page.url)

        # Find job cards
        print("Finding job cards...")

        jobs = page.locator("div[role='button']")

        count = jobs.count()

        print(f"Found {count} job cards")

        for i in range(min(count, 5)):
            try:
                print(f"\nOpening Job {i+1}")

                jobs.nth(i).scroll_into_view_if_needed()
                jobs.nth(i).click()

                page.wait_for_timeout(3000)

                print("Opened Successfully")

            except Exception as e:
                print("Failed:", e)

        input("\nPress ENTER to close...")
        browser.close()


if __name__ == "__main__":
    search_jobs()