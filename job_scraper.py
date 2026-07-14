from playwright.sync_api import sync_playwright
import csv

with sync_playwright() as p:

    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]

    page = None
    for pg in context.pages:
        if "linkedin.com/jobs" in pg.url:
            page = pg
            break

    if page is None:
        raise Exception("LinkedIn Jobs tab not found!")

    print("Connected to:", page.title())

    links = page.locator("a")

    jobs = []

    for i in range(links.count()):

        try:
            text = links.nth(i).inner_text().strip()
            href = links.nth(i).get_attribute("href")

            if href and "currentJobId=" in href and text:

                lines = text.split("\n")

                title = lines[0] if len(lines) > 0 else ""

                company = ""
                if len(lines) > 1:
                    company = lines[1]

                location = ""
                for line in lines:
                    if any(city in line for city in [
                        "Bengaluru",
                        "Hyderabad",
                        "Chennai",
                        "Remote",
                        "Pune",
                        "Mumbai",
                        "India"
                    ]):
                        location = line
                        break

                easy_apply = "Yes" if "Easy Apply" in text else "No"

                jobs.append([
                    title,
                    company,
                    location,
                    easy_apply,
                    href
                ])

        except:
            pass

with open("jobs.csv", "w", newline="", encoding="utf-8") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Title",
        "Company",
        "Location",
        "Easy Apply",
        "Link"
    ])

    writer.writerows(jobs)

print(f"Saved {len(jobs)} jobs to jobs.csv")