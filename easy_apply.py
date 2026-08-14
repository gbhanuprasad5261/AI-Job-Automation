import csv
import os
import re
from application_form import inspect_and_prepare_form
from playwright.sync_api import sync_playwright


# ---------------------------------------
# Configuration
# ---------------------------------------

ANALYSIS_FILE = "data/job_analysis.csv"
TRACKER_FILE = "data/application_tracker.csv"

MIN_MATCH_SCORE = 70


# ---------------------------------------
# Load CSV
# ---------------------------------------

def load_csv(file_path):

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return []

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

        return list(csv.DictReader(f))


# ---------------------------------------
# Get Application Status
# ---------------------------------------

def get_application_statuses():

    tracker = load_csv(TRACKER_FILE)

    statuses = {}

    for row in tracker:

        title = row.get(
            "Title",
            ""
        ).strip()

        status = row.get(
            "Status",
            "NOT APPLIED"
        ).strip()

        if title:
            statuses[title] = status

    return statuses


# ---------------------------------------
# Select Recommended Jobs
# ---------------------------------------

def get_recommended_jobs():

    jobs = load_csv(ANALYSIS_FILE)

    if not jobs:
        return []

    statuses = get_application_statuses()

    recommended = []

    for job in jobs:

        try:

            score = float(
                job.get(
                    "Match Score",
                    "0"
                ).replace("%", "")
            )

        except ValueError:

            score = 0

        easy_apply = (
            job.get(
                "Easy Apply",
                ""
            )
            .strip()
            .lower()
        )

        title = job.get(
            "Title",
            ""
        ).strip()

        status = statuses.get(
            title,
            "NOT APPLIED"
        )

        # ---------------------------------------
        # Apply filters
        # ---------------------------------------

        if score < MIN_MATCH_SCORE:
            continue

        if easy_apply != "yes":
            continue

        if status != "NOT APPLIED":
            continue

        recommended.append(job)

    # Highest score first
    recommended.sort(
        key=lambda x: float(
            x.get(
                "Match Score",
                "0"
            ).replace("%", "")
        ),
        reverse=True
    )

    return recommended


# ---------------------------------------
# Display Jobs
# ---------------------------------------

def display_jobs(jobs):

    print()
    print("=" * 70)
    print("RECOMMENDED EASY APPLY JOBS")
    print("=" * 70)

    if not jobs:

        print()
        print(
            "No jobs currently meet the requirements."
        )

        print()
        print(
            f"Minimum Match Score : "
            f"{MIN_MATCH_SCORE}%"
        )

        print(
            "Easy Apply          : Yes"
        )

        print(
            "Application Status  : NOT APPLIED"
        )

        return

    for index, job in enumerate(
        jobs,
        start=1
    ):

        print()
        print(
            f"{index}. "
            f"{job.get('Title', '')}"
        )

        print(
            f"   Company : "
            f"{job.get('Company') or 'Not available'}"
        )

        print(
            f"   Location: "
            f"{job.get('Location') or 'Not available'}"
        )

        print(
            f"   Score   : "
            f"{job.get('Match Score', '0%')}"
        )

        print(
            f"   Priority: "
            f"{job.get('Priority', '')}"
        )

        print(
            f"   Easy Apply: "
            f"{job.get('Easy Apply', '')}"
        )

        print(
            "   Status  : NOT APPLIED"
        )


# ---------------------------------------
# Convert LinkedIn Search URL
# ---------------------------------------

def convert_to_job_url(link):

    if not link:
        return ""

    if "currentJobId=" in link:

        match = re.search(
            r"currentJobId=(\d+)",
            link
        )

        if match:

            job_id = match.group(1)

            return (
                "https://www.linkedin.com/jobs/view/"
                f"{job_id}/"
            )

    return link


# ---------------------------------------
# Find Easy Apply Button
# ---------------------------------------

def find_easy_apply_button(page):

    selectors = [

        # Standard LinkedIn button
        "button.jobs-apply-button",

        # Easy Apply text
        "button:has-text('Easy Apply')",

        # Button containing Easy Apply
        "[aria-label*='Easy Apply']",

        # Generic button
        "button"
    ]

    for selector in selectors:

        try:

            locator = page.locator(
                selector
            )

            count = locator.count()

            for index in range(count):

                element = locator.nth(index)

                try:

                    if not element.is_visible():
                        continue

                    text = (
                        element.inner_text()
                        .strip()
                        .lower()
                    )

                    aria = (
                        element.get_attribute(
                            "aria-label"
                        )
                        or ""
                    ).lower()

                    if (
                        "easy apply" in text
                        or "easy apply" in aria
                    ):

                        return element

                except Exception:
                    continue

        except Exception:
            continue

    return None


# ---------------------------------------
# Open Easy Apply
# ---------------------------------------

def open_easy_apply(
    job,
    browser_context
):

    link = job.get(
        "Link",
        ""
    )

    link = convert_to_job_url(link)

    if not link:

        print()
        print("Job URL not found.")

        return False

    print()
    print("=" * 70)
    print("OPENING JOB")
    print("=" * 70)

    print(
        f"Title   : "
        f"{job.get('Title', '')}"
    )

    print(
        f"Company : "
        f"{job.get('Company') or 'Not available'}"
    )

    print(
        f"Location: "
        f"{job.get('Location') or 'Not available'}"
    )

    print(
        f"Score   : "
        f"{job.get('Match Score', '')}"
    )

    print(
        f"URL     : "
        f"{link}"
    )

    # ---------------------------------------
    # Get existing page
    # ---------------------------------------

    if browser_context.pages:

        page = browser_context.pages[0]

    else:

        page = browser_context.new_page()

    # ---------------------------------------
    # Open job
    # ---------------------------------------

    try:

        page.goto(
            link,
            wait_until="domcontentloaded",
            timeout=30000
        )

        page.wait_for_timeout(3000)

    except Exception as e:

        print()
        print(
            "Could not open job page."
        )

        print(
            f"Error: {e}"
        )

        return False

    print()
    print(
        f"Page title: {page.title()}"
    )

    # ---------------------------------------
    # Read page text
    # ---------------------------------------

    try:

        body_text = page.locator(
            "body"
        ).inner_text()

    except Exception:

        body_text = ""

    body_lower = body_text.lower()

    # ---------------------------------------
    # Check closed job
    # ---------------------------------------

    closed_messages = [

        "no longer accepting applications",

        "this job is no longer accepting applications",

        "job is no longer accepting applications",

        "applications are closed",

        "no longer accepting",

    ]

    for message in closed_messages:

        if message in body_lower:

            print()
            print(
                "JOB CLOSED"
            )

            print(
                "This job is no longer "
                "accepting applications."
            )

            print(
                "Skipping this job..."
            )

            return False

    # ---------------------------------------
    # Find Easy Apply
    # ---------------------------------------

    easy_apply_button = (
        find_easy_apply_button(page)
    )

    if easy_apply_button is None:

        print()
        print(
            "Easy Apply button not found."
        )

        print(
            "Skipping this job..."
        )

        return False

    # ---------------------------------------
    # Easy Apply found
    # ---------------------------------------

    print()
    print(
        "Easy Apply button found."
    )

    # ---------------------------------------
    # Click Easy Apply
    # ---------------------------------------

    try:

        easy_apply_button.click(
            timeout=10000
        )

    except Exception as e:

        print()
        print(
            "Could not click Easy Apply."
        )

        print(
            f"Error: {e}"
        )

        return False

    # ---------------------------------------
    # Wait for application form
    # ---------------------------------------

    page.wait_for_timeout(2000)

    print()
    print("=" * 70)
    print(
        "EASY APPLY FORM OPENED"
    )
    print("=" * 70)

    # ---------------------------------------
    # Display form text
    # ---------------------------------------

    try:

        form_text = page.locator(
            "body"
        ).inner_text()

        print(
            form_text[:12000]
        )

    except Exception:

        print(
            "Could not read application form."
        )

    print()
    print("=" * 70)

    print(
        "Application form is ready."
    )

    print(
        "Automation will NOT submit the application yet."
    )

    print()

    inspect_and_prepare_form(page)

    print()
    print("=" * 70)
    print("READY FOR APPLICATION AUTOMATION")
    print("=" * 70)

    input(
        "\nPress ENTER to continue..."
    )

    return True


# ---------------------------------------
# Main
# ---------------------------------------

def main():

    print()
    print("=" * 70)
    print(
        "AI JOB AUTOMATION - EASY APPLY"
    )
    print("=" * 70)

    # ---------------------------------------
    # Load eligible jobs
    # ---------------------------------------

    jobs = get_recommended_jobs()

    print()
    print(
        f"Eligible jobs: {len(jobs)}"
    )

    display_jobs(jobs)

    if not jobs:
        return

    print()

    # ---------------------------------------
    # Select starting job
    # ---------------------------------------

    try:

        choice = int(
            input(
                f"Select starting job "
                f"(1-{len(jobs)}): "
            )
        )

    except ValueError:

        print(
            "Invalid selection."
        )

        return

    if choice < 1 or choice > len(jobs):

        print(
            "Invalid job number."
        )

        return

    # ---------------------------------------
    # Connect to Chrome
    # ---------------------------------------

    with sync_playwright() as p:

        try:

            browser = (
                p.chromium.connect_over_cdp(
                    "http://127.0.0.1:9222"
                )
            )

        except Exception as e:

            print()
            print(
                "Could not connect to Chrome."
            )

            print()
            print(
                "Start Chrome using:"
            )

            print(
                ".\\start_chrome.bat"
            )

            print()
            print(
                f"Error: {e}"
            )

            return

        context = browser.contexts[0]

        # ---------------------------------------
        # Try selected job and following jobs
        # ---------------------------------------

        for index in range(
            choice - 1,
            len(jobs)
        ):

            job = jobs[index]

            print()
            print("=" * 70)

            print(
                f"TRYING JOB "
                f"{index + 1}/{len(jobs)}"
            )

            print("=" * 70)

            print(
                f"Title : "
                f"{job.get('Title', '')}"
            )

            print(
                f"Score : "
                f"{job.get('Match Score', '')}"
            )

            success = open_easy_apply(
                job,
                context
            )

            # ---------------------------------------
            # Active Easy Apply job found
            # ---------------------------------------

            if success:

                print()
                print("=" * 70)

                print(
                    "READY FOR APPLICATION AUTOMATION"
                )

                print("=" * 70)

                return

            # ---------------------------------------
            # Try next job
            # ---------------------------------------

            if index + 1 < len(jobs):

                print()
                print(
                    "Trying next eligible job..."
                )

        # ---------------------------------------
        # No active jobs found
        # ---------------------------------------

        print()
        print("=" * 70)

        print(
            "NO ACTIVE EASY APPLY JOB FOUND"
        )

        print("=" * 70)

        print(
            "All selected/remaining jobs were "
            "closed or unavailable."
        )


# ---------------------------------------
# Entry Point
# ---------------------------------------

if __name__ == "__main__":
    main()