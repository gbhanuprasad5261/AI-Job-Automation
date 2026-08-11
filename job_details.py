import csv
import os
import re

from playwright.sync_api import sync_playwright


INPUT_FILE = "jobs.csv"
OUTPUT_FILE = "data/job_details.csv"


def extract_text(page, selectors):
    """
    Try multiple selectors and return the first useful text.
    """

    for selector in selectors:

        try:
            locator = page.locator(selector).first

            if locator.count() > 0:

                text = locator.inner_text().strip()

                if text:
                    return text

        except Exception:
            pass

    return ""


def extract_job_details():

    # ---------------------------------------
    # Check input file
    # ---------------------------------------

    if not os.path.exists(INPUT_FILE):

        print(f"{INPUT_FILE} not found.")
        return

    os.makedirs("data", exist_ok=True)

    # ---------------------------------------
    # Read jobs.csv
    # ---------------------------------------

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)
        jobs = list(reader)

    print(
        f"Found {len(jobs)} jobs in {INPUT_FILE}"
    )

    if not jobs:

        print("No jobs found.")
        return

    results = []

    # ---------------------------------------
    # Connect to Chrome
    # ---------------------------------------

    with sync_playwright() as p:

        browser = p.chromium.connect_over_cdp(
            "http://127.0.0.1:9222"
        )

        context = browser.contexts[0]

        if context.pages:

            page = context.pages[0]

        else:

            page = context.new_page()

        # ---------------------------------------
        # Process jobs
        # ---------------------------------------

        for i, job in enumerate(
            jobs,
            start=1
        ):

            print()
            print("=" * 50)
            print(
                f"Processing job "
                f"{i}/{len(jobs)}"
            )
            print("=" * 50)

            # ---------------------------------------
            # Original CSV values
            # ---------------------------------------

            title = job.get(
                "Title",
                ""
            ).strip()

            company = job.get(
                "Company",
                ""
            ).strip()

            location = job.get(
                "Location",
                ""
            ).strip()

            easy_apply = job.get(
                "Easy Apply",
                ""
            ).strip()

            link = job.get(
                "Link",
                ""
            ).strip()

            # ---------------------------------------
            # Convert search URL to direct job URL
            # ---------------------------------------

            if "currentJobId=" in link:

                match = re.search(
                    r"currentJobId=(\d+)",
                    link
                )

                if match:

                    job_id = match.group(1)

                    link = (
                        "https://www.linkedin.com/"
                        f"jobs/view/{job_id}/"
                    )

            description = ""

            print(f"Title   : {title}")
            print(f"Company : {company}")

            try:

                # ---------------------------------------
                # Open job page
                # ---------------------------------------

                if not link:

                    print("No job link found.")

                    continue

                page.goto(
                    link,
                    wait_until="domcontentloaded",
                    timeout=30000
                )

                page.wait_for_timeout(3000)

                # ---------------------------------------
                # Extract Company
                # ---------------------------------------

                linkedin_company = extract_text(
                    page,
                    [
                        "div.job-details-jobs-unified-top-card__company-name",
                        "a.job-details-jobs-unified-top-card__company-name",
                        "div.jobs-unified-top-card__company-name",
                        "a.jobs-unified-top-card__company-name",
                        "div.job-details-jobs-unified-top-card__primary-description-container a",
                    ]
                )

                if linkedin_company:

                    company = linkedin_company

                # ---------------------------------------
                # Extract Location
                # ---------------------------------------

                linkedin_location = extract_text(
                    page,
                    [
                        "div.job-details-jobs-unified-top-card__primary-description-container",
                        "div.jobs-unified-top-card__primary-description-container",
                        "span.jobs-unified-top-card__bullet",
                    ]
                )

                if linkedin_location:

                    # Sometimes LinkedIn puts company,
                    # location and other metadata together.
                    # Try to find a useful location value.

                    location_parts = [
                        part.strip()
                        for part in re.split(
                            r"\n|\|",
                            linkedin_location
                        )
                        if part.strip()
                    ]

                    # Prefer a part that looks like a location.
                    for part in location_parts:

                        lower_part = part.lower()

                        if any(
                            keyword in lower_part
                            for keyword in [
                                "india",
                                "bengaluru",
                                "bangalore",
                                "hyderabad",
                                "chennai",
                                "pune",
                                "mumbai",
                                "delhi",
                                "remote",
                                "onsite",
                                "on-site",
                                "hybrid"
                            ]
                        ):

                            location = part
                            break

                # ---------------------------------------
                # Try additional location selector
                # ---------------------------------------

                if not location:

                    location = extract_text(
                        page,
                        [
                            "span.jobs-unified-top-card__bullet",
                            "span.job-details-jobs-unified-top-card__bullet",
                        ]
                    )

                # ---------------------------------------
                # Extract Job Description
                # ---------------------------------------

                selectors = [

                    "div.jobs-description__content",

                    "div.jobs-box__html-content",

                    "div#job-details",

                    "article",
                ]

                for selector in selectors:

                    try:

                        locator = page.locator(
                            selector
                        ).first

                        if locator.count() > 0:

                            text = (
                                locator
                                .inner_text()
                                .strip()
                            )

                            if len(text) > len(
                                description
                            ):

                                description = text

                    except Exception:
                        pass

                # ---------------------------------------
                # Fallback: page body
                # ---------------------------------------

                if not description:

                    try:

                        body_text = (
                            page.locator(
                                "body"
                            ).inner_text()
                        )

                        if (
                            "About the job"
                            in body_text
                        ):

                            description = body_text

                    except Exception:
                        pass

                # ---------------------------------------
                # Display results
                # ---------------------------------------

                if company:

                    print(
                        f"Company extracted : "
                        f"{company}"
                    )

                else:

                    print(
                        "Company not found."
                    )

                if location:

                    print(
                        f"Location extracted: "
                        f"{location}"
                    )

                else:

                    print(
                        "Location not found."
                    )

                if description:

                    print(
                        "Description "
                        f"extracted: "
                        f"{len(description)} "
                        "characters"
                    )

                else:

                    print(
                        "Description not found."
                    )

                # ---------------------------------------
                # Add result
                # ---------------------------------------

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
                    f"Error processing "
                    f"job {i}: {e}"
                )

                # ---------------------------------------
                # Keep original values on error
                # ---------------------------------------

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
    ) as file:

        writer = csv.DictWriter(
            file,

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

        for job in results:

            # Clean description
            job["Description"] = (
                job.get(
                    "Description",
                    ""
                )
                .replace("\r", " ")
                .replace("\n", " ")
                .strip()
            )

            writer.writerow(job)

    # ---------------------------------------
    # Completion statistics
    # ---------------------------------------

    descriptions_found = sum(
        1
        for job in results
        if job.get(
            "Description",
            ""
        ).strip()
    )

    companies_found = sum(
        1
        for job in results
        if job.get(
            "Company",
            ""
        ).strip()
    )

    locations_found = sum(
        1
        for job in results
        if job.get(
            "Location",
            ""
        ).strip()
    )

    print()
    print("=" * 50)
    print("JOB DETAILS EXTRACTION COMPLETED")
    print("=" * 50)

    print(
        f"Jobs processed       : "
        f"{len(results)}"
    )

    print(
        f"Descriptions found   : "
        f"{descriptions_found}"
    )

    print(
        f"Companies found      : "
        f"{companies_found}"
    )

    print(
        f"Locations found      : "
        f"{locations_found}"
    )

    print(
        f"Saved file           : "
        f"{OUTPUT_FILE}"
    )

    print("=" * 50)

    input(
        "\nPress ENTER to finish..."
    )


if __name__ == "__main__":
    extract_job_details()