from playwright.sync_api import sync_playwright
import csv

with sync_playwright() as p:

    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")

    context = browser.contexts[0]

    page = None
    for pg in context.pages:
        print(pg.title(), "->", pg.url)

        if "/jobs" in pg.url:
            page = pg
            break

    if page is None:
        raise Exception("LinkedIn Jobs page not found")

    print("Connected:", page.title())

    page.wait_for_timeout(2000)

    cards = page.locator("div[data-job-id]")

    if cards.count() == 0:
        cards = page.locator("li")

    print(f"Found {cards.count()} cards\n")

    jobs = []

    for i in range(min(cards.count(), 20)):

        try:

            card = cards.nth(i)

            card.scroll_into_view_if_needed()
            card.locator("a").first.click(force=True)
            page.wait_for_load_state("domcontentloaded", timeout=5000)
            page.wait_for_timeout(1000)

            page.wait_for_timeout(1500)

            title = ""
            company = ""
            location = ""
            description = ""
            easy_apply = "No"
            link = page.url

            try:
                title = page.locator("h1").first.inner_text().strip()
            except:
                pass

            try:
                company = page.locator("a[href*='/company/']").first.inner_text().strip()
            except:
                pass

            try:
                location = page.locator("span").filter(has_text="India").first.inner_text().strip()
            except:
                pass

            try:
                description = page.locator("[class*='jobs-description']").first.inner_text(timeout=5000)
            except:
                description = page.locator("body").inner_text(timeout=5000)

            if "Easy Apply" in page.locator("body").inner_text():
                easy_apply = "Yes"

            jobs.append([
                title,
                company,
                location,
                easy_apply,
                link,
                description[:3000]
            ])

            print(f"{i+1}. {title}")
            page.go_back(wait_until="domcontentloaded")
            page.wait_for_timeout(1500)

        except Exception as e:
            print("Skipped:", i + 1)

    with open(
        "data/job_details.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "Title",
            "Company",
            "Location",
            "Easy Apply",
            "Link",
            "Description"
        ])

        writer.writerows(jobs)

    print("\nSaved to data/job_details.csv")