import csv
import os
import re

from playwright.sync_api import sync_playwright


INPUT_FILE = "jobs.csv"
OUTPUT_FILE = "data/job_details.csv"


def extract_job_details():

    if not os.path.exists(INPUT_FILE):
        print(f"{INPUT_FILE} not found.")
        return

    # Create data folder if it doesn't exist
    os.makedirs("data", exist_ok=True)

    # Read jobs.csv
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        jobs = list(reader)

    print(f"Found {len(jobs)} jobs in {INPUT_FILE}")

    if not jobs:
        print("No jobs found.")
        return

    results = []

    with sync_playwright() as p:

        # Connect to already-running Chrome
        browser = p.chromium.connect_over_cdp(
            "http://127.0.0.1:9222"
        )

        context = browser.contexts[0]

        # Use existing page if available
        if context.pages:
            page = context.pages[0]
        else:
            page = context.new_page()

        for i, job in enumerate(jobs, start=1):

            print()
            print("=" * 50)
            print(f"Processing job {i}/{len(jobs)}")
            print("=" * 50)

            title = job.get("Title", "")
            company = job.get("Company", "")
            location = job.get("Location", "")
            easy_apply = job.get("Easy Apply", "")
            link = job.get("Link", "")

            # Convert LinkedIn search-result URL to direct job URL
            if "currentJobId=" in link:

                match = re.search(
                    r"currentJobId=(\d+)",
                    link
                )

                if match:
                    job_id = match.group(1)

                    link = (
                        f"https://www.linkedin.com/jobs/view/"
                        f"{job_id}/"
                    )

            description = ""

            print(f"Title   : {title}")
            print(f"Company : {company}")

            try:

                if not link:
                    print("No job link found.")
                    continue

                # Open job page
                page.goto(
                    link,
                    wait_until="domcontentloaded",
                    timeout=30000
                )

                page.wait_for_timeout(3000)

                # Try main job description selectors
                selectors = [
                    "div.jobs-description__content",
                    "div.jobs-box__html-content",
                    "div#job-details",
                    "article",
                ]

                for selector in selectors:

                    try:
                        locator = page.locator(selector).first

                        if locator.count() > 0:

                            text = locator.inner_text().strip()

                            if len(text) > len(description):
                                description = text

                    except Exception:
                        pass

                # Fallback: search page text
                if not description:

                    try:
                        body_text = page.locator(
                            "body"
                        ).inner_text()

                        if "About the job" in body_text:
                            description = body_text

                    except Exception:
                        pass

                if description:

                    print(
                        f"Description extracted: "
                        f"{len(description)} characters"
                    )

                else:

                    print("Description not found.")

                # Add extracted data to results
                results.append({
                    "Title": title,
                    "Company": company,
                    "Location": location,
                    "Experience": "",
                    "Easy Apply": easy_apply,
                    "Skills": "",
                    "Link": link,
                    "Description": description
                })

            except Exception as e:

                print(
                    f"Error processing job {i}: {e}"
                )

                results.append({
                    "Title": title,
                    "Company": company,
                    "Location": location,
                    "Experience": "",
                    "Easy Apply": easy_apply,
                    "Skills": "",
                    "Link": link,
                    "Description": ""
                })

    # ---------------------------------------
    # Save results
    # ---------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Title",
                "Company",
                "Location",
                "Experience",
                "Easy Apply",
                "Skills",
                "Link",
                "Description"
            ],
            quoting=csv.QUOTE_ALL
        )

        writer.writeheader()

        # Save RESULTS, not original jobs
        for job in results:

            # Clean description before saving
            job["Description"] = (
                job.get("Description", "")
                .replace("\r", " ")
                .replace("\n", " ")
            )

            writer.writerow(job)

    # ---------------------------------------
    # Completion message
    # ---------------------------------------

    descriptions_found = sum(
        1
        for job in results
        if job.get("Description", "").strip()
    )

    print()
    print("=" * 50)
    print("JOB DETAILS EXTRACTION COMPLETED")
    print("=" * 50)
    print(f"Jobs processed       : {len(results)}")
    print(f"Descriptions found   : {descriptions_found}")
    print(f"Saved file           : {OUTPUT_FILE}")
    print("=" * 50)

    input("\nPress ENTER to finish...")


if __name__ == "__main__":
    extract_job_details()