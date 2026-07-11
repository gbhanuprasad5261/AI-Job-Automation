from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")

    context = browser.contexts[0]

    page = None
    for tab in context.pages:
        if "linkedin.com/jobs" in tab.url:
            page = tab
            break

    if page is None:
        raise Exception("Jobs page not found!")

    print("Title:", page.title())

    print("\n===== ALL LINKS =====\n")

    links = page.locator("a")

    print("Total links:", links.count())

    for i in range(min(50, links.count())):
        try:
            text = links.nth(i).inner_text().strip()
            href = links.nth(i).get_attribute("href")

            if text:
                print(f"\n{i+1}")
                print("TEXT :", text)
                print("LINK :", href)

        except:
            pass

    input("\nPress ENTER...")