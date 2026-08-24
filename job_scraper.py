from playwright.sync_api import sync_playwright
import csv
import re


INPUT_OUTPUT_FILE = "jobs.csv"


def clean_text(text):
    """Clean extra whitespace from text."""
    return re.sub(r"\s+", " ", text or "").strip()


def extract_job_id(href):
    """Extract LinkedIn currentJobId from a search-result URL."""
    if not href:
        return ""

    match = re.search(r"currentJobId=(\d+)", href)

    if match:
        return match.group(1)

    return ""


def make_direct_job_url(job_id):
    """Create a direct LinkedIn job URL."""
    if not job_id:
        return ""

    return f"https://www.linkedin.com/jobs/view/{job_id}/"


def extract_location(text):
    """Extract a likely location from the job card."""
    locations = [
        "Bengaluru",
        "Bangalore",
        "Hyderabad",
        "Chennai",
        "Remote",
        "Pune",
        "Mumbai",
        "Delhi",
        "Gurugram",
        "Gurgaon",
        "Noida",
        "Kolkata",
        "India",
        "Ahmedabad",
        "Jaipur",
        "Chandigarh",
        "Kochi",
        "Visakhapatnam",
        "Puttur",
    ]

    lines = [
        clean_text(line)
        for line in text.splitlines()
        if clean_text(line)
    ]

    for line in lines:
        for location in locations:
            if location.lower() in line.lower():
                return line

    return ""


def extract_company(text):
    """
    Extract company from the job card.

    LinkedIn search cards generally have:
        Job Title
        Company
        Location
        ...

    We only use this as preliminary data.
    job_details.py will verify the company from the actual job page.
    """

    lines = [
        clean_text(line)
        for line in text.splitlines()
        if clean_text(line)
    ]

    if len(lines) < 2:
        return ""

    # Usually the second line is the company.
    company = lines[1]

    # Avoid accidentally treating location/status as company.
    invalid_company_terms = [
        "India",
        "Remote",
        "Bengaluru",
        "Bangalore",
        "Hyderabad",
        "Chennai",
        "Pune",
        "Mumbai",
        "Delhi",
        "Gurugram",
        "Gurgaon",
        "Noida",
        "Promoted",
        "Actively reviewing applicants",
    ]

    if any(
        term.lower() == company.lower()
        for term in invalid_company_terms
    ):
        return ""

    return company


with sync_playwright() as p:

    # Connect to the already-open Chrome/LinkedIn session.
    browser = p.chromium.connect_over_cdp(
        "http://127.0.0.1:9222"
    )

    context = browser.contexts[0]

    # Find LinkedIn Jobs page.
    page = None

    for pg in context.pages:
        try:
            if "linkedin.com/jobs" in pg.url:
                page = pg
                break
        except Exception:
            pass

    if page is None:
        raise Exception("LinkedIn Jobs tab not found!")

    print("Connected to:", page.title())
    print("URL:", page.url)

    print()
    print("=" * 60)
    print("COLLECTING LINKEDIN JOBS")
    print("=" * 60)

    links = page.locator("a")

    jobs = []
    seen_job_ids = set()

    for i in range(links.count()):

        try:
            link = links.nth(i)

            if not link.is_visible():
                continue

            text = link.inner_text().strip()
            href = link.get_attribute("href")

            if not href:
                continue

            if "currentJobId=" not in href:
                continue

            if not text:
                continue

            # Extract actual LinkedIn job ID.
            job_id = extract_job_id(href)

            if not job_id:
                continue

            # Prevent duplicates.
            if job_id in seen_job_ids:
                continue

            seen_job_ids.add(job_id)

            lines = [
                clean_text(line)
                for line in text.splitlines()
                if clean_text(line)
            ]

            # Job title.
            title = lines[0] if lines else ""

            # Preliminary company from card.
            company = extract_company(text)

            # Location.
            location = extract_location(text)

            # Easy Apply indicator.
            easy_apply = (
                "Yes"
                if "Easy Apply" in text
                else "No"
            )

            # IMPORTANT:
            # Store direct job URL instead of the long search-result URL.
            direct_url = make_direct_job_url(job_id)

            jobs.append([
                title,
                company,
                location,
                easy_apply,
                direct_url
            ])

            print()
            print(f"Job #{len(jobs)}")
            print(f"Title    : {title}")
            print(f"Company  : {company or 'Not detected'}")
            print(f"Location : {location or 'Not detected'}")
            print(f"Easy Apply: {easy_apply}")
            print(f"Job ID   : {job_id}")
            print(f"URL      : {direct_url}")

        except Exception as e:
            print(
                f"Skipping link {i} because of error: {e}"
            )


# Save jobs.csv.
with open(
    INPUT_OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "Title",
        "Company",
        "Location",
        "Easy Apply",
        "Link"
    ])

    writer.writerows(jobs)


print()
print("=" * 60)
print("JOB SCRAPING COMPLETED")
print("=" * 60)

print(f"Jobs collected : {len(jobs)}")
print(f"Unique jobs    : {len(seen_job_ids)}")
print(f"Saved file     : {INPUT_OUTPUT_FILE}")

print("=" * 60)