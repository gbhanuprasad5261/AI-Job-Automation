from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")

    page = browser.contexts[0].pages[0]

    print(page.title())

    page.screenshot(path="job_page.png", full_page=True)

    with open("page.html", "w", encoding="utf-8") as f:
        f.write(page.content())

    print("Saved page.html")