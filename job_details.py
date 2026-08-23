import csv
import os
import re

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)


INPUT_FILE = "jobs.csv"
OUTPUT_FILE = "data/job_details.csv"


# ============================================================
# GENERIC TEXT EXTRACTION
# ============================================================

def extract_text(page, selectors):
    """
    Try multiple selectors and return the first useful text.
    """

    for selector in selectors:

        try:

            locator = page.locator(selector).first

            if locator.count() > 0:

                text = (
                    locator
                    .inner_text()
                    .strip()
                )

                if text:
                    return text

        except Exception:
            pass

    return ""


# ============================================================
# CLEAN LINES
# ============================================================

def clean_lines(text):
    """
    Convert page text into clean individual lines.
    """

    return [
        re.sub(r"\s+", " ", line).strip()
        for line in text.splitlines()
        if re.sub(r"\s+", " ", line).strip()
    ]


# ============================================================
# LOCATION VALIDATION
# ============================================================

def looks_like_location(value, job_title=""):
    """
    Determine whether a text value looks like a location.

    Important:
    A job title such as
    'Software Engineer - E-Commerce (Remote)'
    must NOT be detected as a location.
    """

    if not value:
        return False

    value = re.sub(
        r"\s+",
        " ",
        value
    ).strip()

    lower = value.lower()

    # Never treat the current job title as a location.
    if job_title:

        normalized_title = re.sub(
            r"\s+",
            " ",
            job_title
        ).strip().lower()

        if lower == normalized_title:
            return False

    # Obvious non-location values.
    invalid = [
        "promoted",
        "applicants",
        "applicant",
        "ago",
        "full-time",
        "part-time",
        "contract",
        "internship",
        "commission",
        "remote",
        "hybrid",
        "on-site",
        "onsite",
        "apply",
        "easy apply",
        "save",
        "no response insights",
        "actively reviewing applicants",
        "actively recruiting",
        "promoted by hirer"
    ]

    if lower in invalid:
        return False

    # Posting age.
    if re.fullmatch(
        r"\d+\s+"
        r"(day|days|week|weeks|month|months|"
        r"hour|hours|minute|minutes)"
        r"\s+ago",
        lower
    ):
        return False

    # Applicant counts.
    if "applicant" in lower:
        return False

    # Salary.
    if re.search(
        r"[$₹€£]\s*[\d,]+",
        value
    ):
        return False

    # India locations.
    india_places = [
        "india",
        "bengaluru",
        "bangalore",
        "hyderabad",
        "chennai",
        "pune",
        "mumbai",
        "delhi",
        "gurugram",
        "gurgaon",
        "noida",
        "kolkata",
        "kochi",
        "ahmedabad",
        "jaipur",
        "chandigarh",
        "mysuru",
        "mysore",
        "puducherry",
        "visakhapatnam",
        "puttur"
    ]

    if any(
        place in lower
        for place in india_places
    ):
        return True

    # Remote / hybrid location values.
    if re.fullmatch(
        r".*\b(remote|hybrid)\b.*",
        lower
    ):

        # Avoid job titles containing Remote.
        job_words = [
            "engineer",
            "developer",
            "software",
            "backend",
            "back end",
            "java",
            "python",
            "frontend",
            "full stack",
            "fullstack"
        ]

        if any(
            word in lower
            for word in job_words
        ):
            return False

        return True

    # City/state style locations.
    if "," in value and len(value) <= 120:
        return True

    return False


# ============================================================
# COMPANY EXTRACTION
# ============================================================

def extract_company_from_header(page):
    """
    Extract company for the CURRENT job.

    LinkedIn currently exposes the company as a
    /company/ link inside the main job content.
    """

    # --------------------------------------------------------
    # Strategy 1: Company links
    # --------------------------------------------------------

    try:

        links = page.locator(
            "a[href*='/company/']"
        )

        candidates = []

        for i in range(
            links.count()
        ):

            try:

                link = links.nth(i)

                if not link.is_visible():
                    continue

                text = (
                    link
                    .inner_text()
                    .strip()
                )

                href = (
                    link
                    .get_attribute("href")
                    or ""
                )

                if not text:
                    continue

                if "/company/" not in href:
                    continue

                if len(text) > 150:
                    continue

                candidates.append(text)

            except Exception:
                continue

        if candidates:

            # First company link belongs to
            # the current job header.
            return candidates[0]

    except Exception:
        pass

    # --------------------------------------------------------
    # Strategy 2: Current main content
    # --------------------------------------------------------

    try:

        main = page.locator(
            "main"
        ).first

        if main.count() > 0:

            lines = clean_lines(
                main.inner_text()
            )

            # Usually:
            #
            # Company
            # Job Title
            # Location
            #
            # The company is generally
            # immediately before the title.

            h1 = page.locator(
                "h1"
            ).first

            title = ""

            if h1.count() > 0:

                title = (
                    h1
                    .inner_text()
                    .strip()
                )

            if title in lines:

                title_index = (
                    lines.index(title)
                )

                if title_index > 0:

                    possible_company = (
                        lines[title_index - 1]
                    )

                    if (
                        possible_company
                        and
                        not looks_like_location(
                            possible_company,
                            title
                        )
                    ):

                        return possible_company

    except Exception:
        pass

    return ""


# ============================================================
# LOCATION EXTRACTION
# ============================================================

def extract_location_from_header(
    page,
    job_title=""
):
    """
    Extract the location for the CURRENT job.

    Cleans LinkedIn metadata such as:

        India · 6 days ago · Over 100 people clicked apply

    into:

        India
    """

    # --------------------------------------------------------
    # Helper: clean a possible location
    # --------------------------------------------------------

    def clean_location(value):

        if not value:
            return ""

        value = re.sub(
            r"\s+",
            " ",
            value
        ).strip()

        # Remove everything after LinkedIn's metadata separator.
        if " · " in value:
            value = value.split(
                " · ",
                1
            )[0].strip()

        # Remove common LinkedIn metadata.
        value = re.sub(
            r"\b\d+\s+(day|days|week|weeks|month|months|hour|hours)\s+ago\b",
            "",
            value,
            flags=re.IGNORECASE
        ).strip()

        value = re.sub(
            r"\b(reposted|posted)\b.*$",
            "",
            value,
            flags=re.IGNORECASE
        ).strip()

        return value

    # --------------------------------------------------------
    # Helper: validate final location
    # --------------------------------------------------------

    def valid_location(value):

        if not value:
            return False

        value = clean_location(value)

        if not value:
            return False

        lower = value.lower()

        # Never use job title as location.
        if job_title:
            if lower == job_title.lower():
                return False

        # Reject obvious non-location text.
        invalid_patterns = [
            "about ",
            "responsibilities",
            "requirements",
            "benefits",
            "full description",
            "apply",
            "save",
            "applicants",
            "clicked apply",
            "promoted",
            "contract",
            "full-time",
            "part-time",
            "internship"
        ]

        if any(
            pattern in lower
            for pattern in invalid_patterns
        ):
            return False

        # Strong India location indicators.
        india_places = [
            "india",
            "bengaluru",
            "bangalore",
            "hyderabad",
            "chennai",
            "pune",
            "mumbai",
            "delhi",
            "gurugram",
            "gurgaon",
            "noida",
            "kolkata",
            "kochi",
            "ahmedabad",
            "jaipur",
            "chandigarh",
            "mysuru",
            "mysore",
            "puducherry",
            "visakhapatnam",
            "puttur"
        ]

        if any(
            place in lower
            for place in india_places
        ):
            return True

        # Remote / hybrid.
        if re.search(
            r"\b(remote|hybrid)\b",
            lower
        ):
            return True

        # City/state style location.
        if "," in value and len(value) <= 120:
            return True

        return False

    # --------------------------------------------------------
    # Strategy 1: Main job content
    # --------------------------------------------------------

    try:

        main = page.locator(
            "main"
        ).first

        if main.count() > 0:

            lines = clean_lines(
                main.inner_text()
            )

            title_index = -1

            if job_title:

                try:
                    title_index = lines.index(
                        job_title
                    )
                except ValueError:
                    pass

            # Location normally appears immediately
            # after the job title.
            if title_index != -1:

                for line in lines[
                    title_index + 1:
                    title_index + 5
                ]:

                    cleaned = clean_location(
                        line
                    )

                    if valid_location(
                        cleaned
                    ):
                        return cleaned

    except Exception:
        pass

    # --------------------------------------------------------
    # Strategy 2: Known LinkedIn bullet selectors
    # --------------------------------------------------------

    selectors = [
        "span.jobs-unified-top-card__bullet",
        "span.job-details-jobs-unified-top-card__bullet"
    ]

    for selector in selectors:

        try:

            locator = page.locator(
                selector
            )

            for i in range(
                locator.count()
            ):

                element = locator.nth(i)

                if not element.is_visible():
                    continue

                value = (
                    element
                    .inner_text()
                    .strip()
                )

                for part in clean_lines(
                    value
                ):

                    cleaned = clean_location(
                        part
                    )

                    if valid_location(
                        cleaned
                    ):
                        return cleaned

        except Exception:
            pass

    # --------------------------------------------------------
    # Strategy 3: Search first 20 main lines
    # --------------------------------------------------------

    try:

        main = page.locator(
            "main"
        ).first

        if main.count() > 0:

            lines = clean_lines(
                main.inner_text()
            )

            for line in lines[:20]:

                cleaned = clean_location(
                    line
                )

                if valid_location(
                    cleaned
                ):
                    return cleaned

    except Exception:
        pass

    return ""


# ============================================================
# DESCRIPTION EXTRACTION
# ============================================================

def extract_description(page):

    description = ""

    selectors = [
        "div.jobs-description__content",
        "div.jobs-box__html-content",
        "div#job-details",
        "article"
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

    # --------------------------------------------------------
    # Body fallback
    # --------------------------------------------------------

    if not description:

        try:

            body_text = page.locator(
                "body"
            ).inner_text()

            if (
                "About the job"
                in body_text
            ):

                description = body_text

        except Exception:
            pass

    return description


# ============================================================
# OPEN LINKEDIN JOB PAGE
# ============================================================

def open_job_page(
    page,
    link
):
    """
    Open LinkedIn job page safely.

    Two attempts are used because LinkedIn
    sometimes responds slowly.
    """

    for attempt in range(
        1,
        3
    ):

        try:

            print(
                f"Opening job page "
                f"(attempt {attempt}/2)..."
            )

            page.goto(
                link,
                wait_until="commit",
                timeout=30000
            )

            page.wait_for_timeout(
                3000
            )

            return True

        except PlaywrightTimeoutError:

            print(
                "Navigation timed out. "
                "Checking page..."
            )

            try:

                page.wait_for_timeout(
                    3000
                )

                if (
                    "linkedin.com"
                    in page.url
                ):

                    print(
                        "Page loaded enough. "
                        "Continuing extraction."
                    )

                    return True

            except Exception:
                pass

        except Exception as e:

            print(
                f"Navigation error: {e}"
            )

            if attempt == 1:

                print(
                    "Retrying navigation..."
                )

                try:

                    page.wait_for_timeout(
                        3000
                    )

                except Exception:
                    pass

    print(
        "Could not open job page."
    )

    return False


# ============================================================
# MAIN EXTRACTION
# ============================================================

def extract_job_details():

    # --------------------------------------------------------
    # Check input
    # --------------------------------------------------------

    if not os.path.exists(
        INPUT_FILE
    ):

        print(
            f"{INPUT_FILE} not found."
        )

        return

    os.makedirs(
        "data",
        exist_ok=True
    )

    # --------------------------------------------------------
    # Read jobs.csv
    # --------------------------------------------------------

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(
            file
        )

        jobs = list(reader)

    print(
        f"Found {len(jobs)} jobs "
        f"in {INPUT_FILE}"
    )

    if not jobs:

        print(
            "No jobs found."
        )

        return

    results = []

    # --------------------------------------------------------
    # Connect to existing Chrome
    # --------------------------------------------------------

    with sync_playwright() as p:

        browser = p.chromium.connect_over_cdp(
            "http://127.0.0.1:9222"
        )

        context = browser.contexts[0]

        if context.pages:

            page = context.pages[0]

        else:

            page = context.new_page()

        # ----------------------------------------------------
        # Process every job
        # ----------------------------------------------------

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

            # ------------------------------------------------
            # Convert LinkedIn search URL
            # ------------------------------------------------

            if (
                "currentJobId="
                in link
            ):

                match = re.search(
                    r"currentJobId=(\d+)",
                    link
                )

                if match:

                    job_id = (
                        match.group(1)
                    )

                    link = (
                        "https://www.linkedin.com/"
                        "jobs/view/"
                        f"{job_id}/"
                    )

            description = ""

            print(
                f"Title   : {title}"
            )

            print(
                f"Company : {company}"
            )

            try:

                # ------------------------------------------------
                # Open page
                # ------------------------------------------------

                if not link:

                    print(
                        "No job link found."
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

                    continue

                opened = open_job_page(
                    page,
                    link
                )

                if not opened:

                    print(
                        "Could not open job."
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

                    continue

                # ------------------------------------------------
                # Actual title
                # ------------------------------------------------

                actual_title = extract_text(
                    page,
                    ["h1"]
                )

                if actual_title:

                    title = actual_title

                # ------------------------------------------------
                # Company
                # ------------------------------------------------

                linkedin_company = (
                    extract_company_from_header(
                        page
                    )
                )

                if linkedin_company:

                    company = (
                        linkedin_company
                    )

                # ------------------------------------------------
                # Location
                # ------------------------------------------------

                linkedin_location = (
                    extract_location_from_header(
                        page,
                        title
                    )
                )

                if linkedin_location:

                    location = (
                        linkedin_location
                    )

                # ------------------------------------------------
                # Description
                # ------------------------------------------------

                description = (
                    extract_description(
                        page
                    )
                )

                # ------------------------------------------------
                # Display
                # ------------------------------------------------

                print()

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
                        "Description extracted: "
                        f"{len(description)} "
                        "characters"
                    )

                else:

                    print(
                        "Description not found."
                    )

                # ------------------------------------------------
                # Save result
                # ------------------------------------------------

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

                # Preserve original data
                # if extraction fails.

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

    # ========================================================
    # SAVE OUTPUT CSV
    # ========================================================

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

            job["Description"] = (
                job.get(
                    "Description",
                    ""
                )
                .replace(
                    "\r",
                    " "
                )
                .replace(
                    "\n",
                    " "
                )
                .strip()
            )

            writer.writerow(
                job
            )

    # ========================================================
    # STATISTICS
    # ========================================================

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

    # ========================================================
    # FINAL OUTPUT
    # ========================================================

    print()

    print("=" * 50)

    print(
        "JOB DETAILS EXTRACTION COMPLETED"
    )

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


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":
    extract_job_details()