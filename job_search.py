import csv
from playwright.sync_api import sync_playwright
from config import LINKEDIN_EMAIL, LINKEDIN_PASSWORD


def search_jobs():
    with sync_playwright() as p:

        # ---------------------------------------
        # Launch Browser
        # ---------------------------------------
        browser = p.chromium.launch(
            headless=False,
            slow_mo=500,
            args=["--start-maximized"]
        )

        context = browser.new_context(
            viewport=None
        )

        page = context.new_page()

        # ---------------------------------------
        # Login
        # ---------------------------------------
        print("Opening LinkedIn...")
        page.goto("https://www.linkedin.com/login")

        print("Typing Email...")
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

        # ---------------------------------------
        # Handle Verification
        # ---------------------------------------

        print("Waiting for login...")
        page.wait_for_timeout(5000)

        if "checkpoint" in page.url:
            print("\nLinkedIn verification detected.")
            print("Complete the CAPTCHA in the browser.")
            input("Press ENTER after verification...")

            # Wait until LinkedIn finishes redirecting
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(5000)

        print("Login Successful!")

        # ---------------------------------------
        # Open Jobs Page
        # ---------------------------------------

        print("Opening Jobs page...")

        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        page.goto(
            "https://www.linkedin.com/jobs/",
            wait_until="networkidle"
        )

        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        print(page.url)
        # ---------------------------------------
        # Search Job
        # ---------------------------------------
        print("Searching jobs...")

        search_box = page.get_by_placeholder(
            "Describe the job you want"
        )

        search_box.click()
        search_box.fill("Java Backend Developer")
        page.keyboard.press("Enter")

        page.wait_for_timeout(5000)

        print(page.url)

        # ---------------------------------------
        # Collect Jobs
        # ---------------------------------------
        print("\nCollecting job information...\n")

        page.wait_for_timeout(5000)

        job_cards = page.get_by_role("button")

        count = job_cards.count()

        print(f"Found {count} buttons\n")

        jobs = []

        for i in range(min(count, 20)):

            try:

                card = job_cards.nth(i)

                text = card.inner_text().strip()

                print("----------------------------------")
                print(f"Button {i + 1}")
                print(text)

                if not text:
                    continue

                lines = [
                    line.strip()
                    for line in text.split("\n")
                    if line.strip()
                ]

                # Skip filter buttons
                if len(lines) < 3:
                    continue

                title = lines[0]
                company = lines[1]
                location = lines[2]

                easy_apply = "Yes" if "Easy Apply" in text else "No"

                jobs.append({
                    "Title": title,
                    "Company": company,
                    "Location": location,
                    "Easy Apply": easy_apply
                })

            except Exception as e:
                print(f"Skipping Button {i + 1}: {e}")

        # ---------------------------------------
        # Save CSV
        # ---------------------------------------
        with open(
            "jobs.csv",
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "Title",
                    "Company",
                    "Location",
                    "Easy Apply"
                ]
            )

            writer.writeheader()
            writer.writerows(jobs)

        print(f"\nSaved {len(jobs)} jobs to jobs.csv")

        input("\nPress ENTER to close...")

        context.close()
        browser.close()


if __name__ == "__main__":
    search_jobs()