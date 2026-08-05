import csv
from playwright.sync_api import sync_playwright
from config import LINKEDIN_EMAIL, LINKEDIN_PASSWORD


def search_jobs():

    with sync_playwright() as p:

        browser = p.chromium.connect_over_cdp(
            "http://127.0.0.1:9222"
        )
    

        context = browser.contexts[0]

        page = context.pages[0]

        print("Connected to:", page.title())

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

        print("Waiting for login...")
        page.wait_for_timeout(5000)

        if "checkpoint" in page.url:
            print("Complete CAPTCHA")
            input("Press ENTER after verification...")

            while "feed" not in page.url and "jobs" not in page.url:
             page.wait_for_timeout(1000)

        print("Logged in successfully")

       

        # ---------------------------------------
        # Jobs Page
        # ---------------------------------------

        page.goto(
            "https://www.linkedin.com/jobs/",
            wait_until="networkidle"
        )

        page.wait_for_timeout(4000)

        print(page.url)

        # ---------------------------------------
        # Search
        # ---------------------------------------

        search_box = page.get_by_placeholder(
            "Describe the job you want"
        )

        search_box.fill("Java Backend Developer")

        page.keyboard.press("Enter")

        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(4000)

        print(page.url)

        page.screenshot(
            path="search_results.png",
            full_page=True
        )

        # ---------------------------------------
        # Collect Jobs
        # ---------------------------------------

        print("\nSearching for job cards...")

        cards = page.locator(
            "li.scaffold-layout__list-item"
        )

        count = cards.count()

        print(f"Found {count} job cards\n")

        jobs = []

        for i in range(min(count, 20)):

            try:

                card = cards.nth(i)

                card.scroll_into_view_if_needed()

                page.wait_for_timeout(500)

                card.click(force=True)

                page.wait_for_timeout(2500)

                title = ""
                company = ""
                location = ""
                easy_apply = "No"

                try:
                    title = page.locator("h1").first.inner_text().strip()
                except:
                    pass

                try:
                    company = page.locator(
                        "a[href*='/company/']"
                    ).first.inner_text().strip()
                except:
                    pass

                try:
                    location = page.locator(
                        "div.job-details-jobs-unified-top-card__primary-description-container"
                    ).inner_text().strip()
                except:
                    pass

                body = page.locator("body").inner_text()

                if "Easy Apply" in body:
                    easy_apply = "Yes"

                jobs.append({
                    "Title": title,
                    "Company": company,
                    "Location": location,
                    "Easy Apply": easy_apply
                })

                print(f"{i+1}. {title}")

            except Exception as e:

                print(f"Skipped {i+1}: {e}")

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