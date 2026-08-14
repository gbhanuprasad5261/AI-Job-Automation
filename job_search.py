import csv
import re

from playwright.sync_api import sync_playwright


# ---------------------------------------
# Configuration
# ---------------------------------------

SEARCH_KEYWORD = "Java Backend Developer"
OUTPUT_FILE = "jobs.csv"
MAX_JOBS = 20


# ---------------------------------------
# Search Jobs
# ---------------------------------------

def search_jobs():

    with sync_playwright() as p:

        # ---------------------------------------
        # Connect to Chrome
        # ---------------------------------------

        try:

            browser = p.chromium.connect_over_cdp(
                "http://127.0.0.1:9222"
            )

        except Exception as e:

            print()
            print("Could not connect to Chrome.")
            print()
            print("Start Chrome using:")
            print(".\\start_chrome.bat")
            print()
            print(f"Error: {e}")

            return

        context = browser.contexts[0]

        if context.pages:
            page = context.pages[0]
        else:
            page = context.new_page()

        print(
            "Connected to:",
            page.title()
        )

        # ---------------------------------------
        # Open LinkedIn Jobs
        # ---------------------------------------

        print()
        print("Opening LinkedIn...")

        page.goto(
            "https://www.linkedin.com/jobs/",
            wait_until="domcontentloaded",
            timeout=30000
        )

        page.wait_for_timeout(4000)

        # ---------------------------------------
        # Login Check
        # ---------------------------------------

        if "login" in page.url:

            print()
            print("LinkedIn login required.")

            input(
                "Login manually and press ENTER..."
            )

            page.goto(
                "https://www.linkedin.com/jobs/",
                wait_until="domcontentloaded",
                timeout=30000
            )

            page.wait_for_timeout(3000)

        # ---------------------------------------
        # Search
        # ---------------------------------------

        print()
        print(
            f"Searching for: {SEARCH_KEYWORD}"
        )

        try:

            search_box = page.get_by_placeholder(
                "Describe the job you want"
            )

            search_box.fill(
                SEARCH_KEYWORD
            )

            page.keyboard.press(
                "Enter"
            )

            page.wait_for_timeout(5000)

        except Exception:

            print(
                "Search box not available."
            )

            search_url = (
                "https://www.linkedin.com/jobs/search/"
                "?keywords="
                + SEARCH_KEYWORD.replace(
                    " ",
                    "%20"
                )
            )

            page.goto(
                search_url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            page.wait_for_timeout(5000)

        print()
        print(
            "Search URL:",
            page.url
        )

        page.screenshot(
            path="search_results.png",
            full_page=True
        )

        # ---------------------------------------
        # Find Job Result Titles
        # ---------------------------------------

        print()
        print(
            "Finding job results..."
        )

        spans = page.locator("span")

        span_count = spans.count()

        job_titles = []

        # Common job-title keywords
        keywords = [
            "java",
            "backend",
            "developer",
            "software engineer",
            "sde",
            "spring",
            "microservices"
        ]

        for i in range(span_count):

            try:

                text = (
                    spans
                    .nth(i)
                    .inner_text()
                    .strip()
                )

                if not text:
                    continue

                if len(text) > 150:
                    continue

                text_lower = text.lower()

                if not any(
                    keyword in text_lower
                    for keyword in keywords
                ):
                    continue

                # Avoid duplicate titles
                if text not in job_titles:

                    job_titles.append(text)

            except Exception:
                pass

        print(
            f"Potential job titles found: "
            f"{len(job_titles)}"
        )

        # ---------------------------------------
        # Limit jobs
        # ---------------------------------------

        job_titles = job_titles[
            :MAX_JOBS
        ]

        # ---------------------------------------
        # Collect Jobs
        # ---------------------------------------

        jobs = []

        seen_links = set()

        # ---------------------------------------
        # Process each title
        # ---------------------------------------

        for index, title in enumerate(
            job_titles,
            start=1
        ):

            try:

                print()
                print("=" * 70)

                print(
                    f"Processing job "
                    f"{index}/{len(job_titles)}"
                )

                print(
                    f"Title: {title}"
                )

                # ---------------------------------------
                # Find matching span
                # ---------------------------------------

                title_locator = page.locator(
                    "span"
                ).filter(
                    has_text=title
                ).first

                if title_locator.count() == 0:

                    print(
                        "Title element not found."
                    )

                    continue

                # ---------------------------------------
                # Click job title
                # ---------------------------------------

                title_locator.scroll_into_view_if_needed()

                page.wait_for_timeout(300)

                title_locator.click(
                    force=True
                )

                page.wait_for_timeout(2500)

                # ---------------------------------------
                # Get current URL
                # ---------------------------------------

                current_url = page.url

                job_id_match = re.search(
                    r"currentJobId=(\d+)",
                    current_url
                )

                job_link = ""

                if job_id_match:

                    job_id = (
                        job_id_match.group(1)
                    )

                    job_link = (
                        "https://www.linkedin.com/jobs/view/"
                        f"{job_id}/"
                    )

                else:

                    # Try selected job link
                    try:

                        link_locator = page.locator(
                            "a[href*='/jobs/view/']"
                        ).first

                        if link_locator.count() > 0:

                            job_link = (
                                link_locator
                                .get_attribute("href")
                                or ""
                            )

                            if job_link:

                                job_link = (
                                    job_link
                                    .split("?")[0]
                                )

                    except Exception:
                        pass

                if not job_link:

                    print(
                        "Job URL not found."
                    )

                    continue

                if job_link in seen_links:

                    continue

                seen_links.add(
                    job_link
                )

                # ---------------------------------------
                # Extract Title
                # ---------------------------------------

                actual_title = title

                try:

                    actual_title = (
                        page.locator("h1")
                        .first
                        .inner_text()
                        .strip()
                    )

                except Exception:
                    pass

                # ---------------------------------------
                # Extract Company
                # ---------------------------------------

                company = ""

                company_selectors = [

                    "a[href*='/company/']",

                    "div.job-details-jobs-unified-top-card__company-name a",

                    "div.job-details-jobs-unified-top-card__company-name"

                ]

                for selector in company_selectors:

                    try:

                        locator = page.locator(
                            selector
                        ).first

                        if locator.count() > 0:

                            value = (
                                locator
                                .inner_text()
                                .strip()
                            )

                            if value:

                                company = value

                                break

                    except Exception:
                        pass

                # ---------------------------------------
                # Extract Location
                # ---------------------------------------

                location = ""

                location_selectors = [

                    "div.job-details-jobs-unified-top-card__primary-description-container",

                    "span.jobs-unified-top-card__bullet"

                ]

                for selector in location_selectors:

                    try:

                        locator = page.locator(
                            selector
                        ).first

                        if locator.count() > 0:

                            value = (
                                locator
                                .inner_text()
                                .strip()
                            )

                            if value:

                                location = value

                                break

                    except Exception:
                        pass

                # ---------------------------------------
                # Read Body
                # ---------------------------------------

                try:

                    body = page.locator(
                        "body"
                    ).inner_text()

                except Exception:

                    body = ""

                body_lower = body.lower()

                # ---------------------------------------
                # Closed Check
                # ---------------------------------------

                closed_messages = [

                    "no longer accepting applications",

                    "this job is no longer accepting applications",

                    "applications are closed",

                    "no longer accepting"

                ]

                closed = any(
                    message in body_lower
                    for message in closed_messages
                )

                if closed:

                    print(
                        "Status : CLOSED"
                    )

                    print(
                        "Skipping."
                    )

                    continue

                # ---------------------------------------
                # Easy Apply Detection
                # ---------------------------------------

                easy_apply = False

                buttons = page.locator(
                    "button"
                )

                for button_index in range(
                    buttons.count()
                ):

                    try:

                        button = buttons.nth(
                            button_index
                        )

                        if not button.is_visible():
                            continue

                        text = (
                            button
                            .inner_text()
                            .strip()
                            .lower()
                        )

                        aria = (
                            button
                            .get_attribute(
                                "aria-label"
                            )
                            or ""
                        ).lower()

                        if (
                            "easy apply" in text
                            or "easy apply" in aria
                        ):

                            easy_apply = True

                            break

                    except Exception:
                        continue

                # ---------------------------------------
                # Active Applicants
                # ---------------------------------------

                actively_reviewing = (
                    "actively reviewing applicants"
                    in body_lower
                )

                # ---------------------------------------
                # Print
                # ---------------------------------------

                print(
                    f"Company : "
                    f"{company or 'Not available'}"
                )

                print(
                    f"Location: "
                    f"{location or 'Not available'}"
                )

                print(
                    f"Easy Apply: "
                    f"{'Yes' if easy_apply else 'No'}"
                )

                print(
                    f"Actively Reviewing: "
                    f"{'Yes' if actively_reviewing else 'No'}"
                )

                print(
                    f"URL: {job_link}"
                )

                # ---------------------------------------
                # Save
                # ---------------------------------------

                jobs.append({

                    "Title":
                        actual_title,

                    "Company":
                        company,

                    "Location":
                        location,

                    "Easy Apply":
                        "Yes"
                        if easy_apply
                        else "No",

                    "Link":
                        job_link

                })

            except Exception as e:

                print(
                    f"Skipped job: {e}"
                )

        # ---------------------------------------
        # Save CSV
        # ---------------------------------------

        with open(
            OUTPUT_FILE,
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
                    "Easy Apply",
                    "Link"
                ]
            )

            writer.writeheader()

            writer.writerows(
                jobs
            )

        # ---------------------------------------
        # Summary
        # ---------------------------------------

        easy_apply_count = sum(
            1
            for job in jobs
            if job["Easy Apply"] == "Yes"
        )

        print()
        print("=" * 70)
        print(
            "JOB SEARCH COMPLETED"
        )
        print("=" * 70)

        print(
            f"Jobs collected      : {len(jobs)}"
        )

        print(
            f"Easy Apply jobs     : "
            f"{easy_apply_count}"
        )

        print(
            f"Saved file          : "
            f"{OUTPUT_FILE}"
        )

        print("=" * 70)

        input(
            "\nPress ENTER to finish..."
        )


# ---------------------------------------
# Entry Point
# ---------------------------------------

if __name__ == "__main__":
    search_jobs()