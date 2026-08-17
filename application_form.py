import os
import re
from pathlib import Path
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


# ============================================================
# CONFIGURATION
# ============================================================

RESUME_PATH = os.getenv(
    "RESUME_PATH",
    r"C:\Users\gbhan\Desktop\AI-Job-Automation\resume\resume.pdf"
)

APPLICANT_NAME = os.getenv(
    "APPLICANT_NAME",
    "G Bhanu Prasad"
)

EMAIL = os.getenv(
    "EMAIL",
    "gbhanuprasad1236@gmail.com"
)

PHONE = os.getenv(
    "PHONE",
    "9392801041"
)

YEARS_OF_EXPERIENCE = os.getenv(
    "YEARS_OF_EXPERIENCE",
    "0"
)

AUTO_SUBMIT = False


# ============================================================
# HELPERS
# ============================================================

def safe_inner_text(locator):
    try:
        return locator.inner_text().strip()
    except Exception:
        return ""


def safe_attribute(locator, attribute):
    try:
        return locator.get_attribute(attribute)
    except Exception:
        return None


def is_visible(locator):
    try:
        return locator.is_visible()
    except Exception:
        return False


def normalize(text):
    return re.sub(r"\s+", " ", text or "").strip().lower()


def is_resume_text(text):
    """
    Prevent LinkedIn resume choices from being detected
    as application questions.
    """

    if not text:
        return False

    text_lower = normalize(text)

    resume_extensions = (
        ".pdf",
        ".doc",
        ".docx",
        ".rtf"
    )

    resume_keywords = (
        "resume",
        "cv",
        "bhanuprasad",
        "bhanu prasad"
    )

    if any(ext in text_lower for ext in resume_extensions):
        return True

    if any(word in text_lower for word in resume_keywords):
        return True

    return False


# ============================================================
# BASIC FIELD FILLING
# ============================================================

def fill_name_fields(page):

    print("\nChecking name fields...")

    selectors = [
        'input[name*="name" i]',
        'input[id*="name" i]',
        'input[autocomplete="name"]'
    ]

    for selector in selectors:

        try:
            fields = page.locator(selector)

            for i in range(fields.count()):

                field = fields.nth(i)

                if not is_visible(field):
                    continue

                current = safe_attribute(field, "value")

                if not current:
                    field.fill(APPLICANT_NAME)
                    print("Name filled.")

        except Exception:
            pass


def fill_email_fields(page):

    print("\nChecking email field...")

    selectors = [
        'input[type="email"]',
        'input[name*="email" i]',
        'input[id*="email" i]'
    ]

    for selector in selectors:

        try:
            fields = page.locator(selector)

            for i in range(fields.count()):

                field = fields.nth(i)

                if not is_visible(field):
                    continue

                field.fill(EMAIL)
                print("Email filled.")
                return

        except Exception:
            pass


def fill_phone_fields(page):

    print("\nChecking phone field...")

    selectors = [
        'input[type="tel"]',
        'input[name*="phone" i]',
        'input[name*="mobile" i]',
        'input[id*="phone" i]',
        'input[id*="mobile" i]'
    ]

    for selector in selectors:

        try:
            fields = page.locator(selector)

            for i in range(fields.count()):

                field = fields.nth(i)

                if not is_visible(field):
                    continue

                try:
                    field.fill(PHONE)
                    print("Phone filled.")
                    return
                except Exception:
                    pass

        except Exception:
            pass


# ============================================================
# PHONE COUNTRY CODE
# ============================================================

def select_india_country_code(page):

    print("\nChecking phone country code...")

    # First try native select.
    try:

        selects = page.locator("select")

        for i in range(selects.count()):

            select = selects.nth(i)

            if not is_visible(select):
                continue

            options = select.locator("option")

            for j in range(options.count()):

                option = options.nth(j)

                text = safe_inner_text(option)

                value = safe_attribute(option, "value")

                if "+91" in text or "India" in text:

                    try:
                        if value:
                            select.select_option(value=value)
                        else:
                            select.select_option(label=text)

                        print("Phone country code selected: India (+91)")
                        return True

                    except Exception:
                        pass

    except Exception:
        pass

    # LinkedIn often uses a custom combobox.
    try:

        combos = page.get_by_role("combobox")

        for i in range(combos.count()):

            combo = combos.nth(i)

            if not is_visible(combo):
                continue

            text = safe_inner_text(combo)

            aria = safe_attribute(combo, "aria-label")

            combined = normalize(f"{text} {aria}")

            if (
                "country" in combined
                or "phone" in combined
                or "+91" in combined
            ):

                try:
                    combo.click()

                    page.wait_for_timeout(500)

                    india = page.get_by_text(
                        re.compile(r"India.*\(\+91\)", re.I)
                    ).last

                    if is_visible(india):
                        india.click()

                        print(
                            "Phone country code selected: India (+91)"
                        )

                        return True

                except Exception:
                    pass

    except Exception:
        pass

    # Last attempt using visible text.
    try:

        india = page.get_by_text(
            re.compile(r"India.*\(\+91\)", re.I)
        ).last

        if is_visible(india):

            india.click()

            print(
                "Phone country code selected: India (+91)"
            )

            return True

    except Exception:
        pass

    print("Could not explicitly select India (+91).")
    print("Please verify the country code before submitting.")

    return False


# ============================================================
# RESUME SELECTION
# ============================================================

def select_existing_resume(page):

    print("\nChecking resume selection...")

    preferred_name = Path(RESUME_PATH).name.lower()

    print("Preferred resume:", preferred_name)

    # --------------------------------------------------------
    # METHOD 1: FILE INPUT
    # --------------------------------------------------------

    try:

        file_inputs = page.locator('input[type="file"]')

        if file_inputs.count() > 0:

            for i in range(file_inputs.count()):

                file_input = file_inputs.nth(i)

                if is_visible(file_input) or True:

                    if Path(RESUME_PATH).exists():

                        file_input.set_input_files(
                            RESUME_PATH
                        )

                        print(
                            "Resume uploaded:",
                            RESUME_PATH
                        )

                        return True

    except Exception as e:

        print("File input upload not available:", e)

    # --------------------------------------------------------
    # METHOD 2: LINKEDIN EXISTING RESUME SELECTOR
    # --------------------------------------------------------

    print("Looking for existing LinkedIn resume selector...")

    body_text = ""

    try:
        body_text = page.locator("body").inner_text()
    except Exception:
        pass

    pdf_lines = []

    for line in body_text.splitlines():

        line_clean = line.strip()

        if (
            ".pdf" in line_clean.lower()
            and len(line_clean) < 250
        ):
            pdf_lines.append(line_clean)

    if pdf_lines:

        print("Existing resumes detected:")

        for resume in pdf_lines[:10]:
            print(" -", resume)

    # --------------------------------------------------------
    # Try preferred resume first
    # --------------------------------------------------------

    preferred_stem = Path(
        RESUME_PATH
    ).stem.lower()

    candidates = page.locator(
        "text=/.*\\.pdf.*/i"
    )

    try:

        count = candidates.count()

        for i in range(count):

            candidate = candidates.nth(i)

            if not is_visible(candidate):
                continue

            text = safe_inner_text(candidate)

            if not text:
                continue

            if preferred_stem in text.lower():

                print(
                    "Preferred resume found:",
                    text
                )

                try:
                    candidate.click()
                    page.wait_for_timeout(500)

                    print("Preferred resume selected.")
                    return True

                except Exception:
                    pass

    except Exception:
        pass

    # --------------------------------------------------------
    # If preferred resume isn't found, select first PDF
    # --------------------------------------------------------

    try:

        for i in range(candidates.count()):

            candidate = candidates.nth(i)

            if not is_visible(candidate):
                continue

            text = safe_inner_text(candidate)

            if ".pdf" not in text.lower():
                continue

            print(
                "Selecting available resume:",
                text
            )

            try:

                candidate.click()

                page.wait_for_timeout(500)

                print("Resume selected.")

                return True

            except Exception:
                pass

    except Exception:
        pass

    # --------------------------------------------------------
    # Try labels / buttons containing PDF
    # --------------------------------------------------------

    try:

        elements = page.locator(
            "label, button, [role='radio'], [role='option']"
        )

        for i in range(elements.count()):

            element = elements.nth(i)

            if not is_visible(element):
                continue

            text = safe_inner_text(element)

            if ".pdf" not in text.lower():
                continue

            print(
                "Resume option found:",
                text
            )

            try:

                element.click()

                page.wait_for_timeout(500)

                print("Resume option selected.")

                return True

            except Exception:
                pass

    except Exception:
        pass

    print("No resume selector found on this page.")

    return False


# ============================================================
# COMMON APPLICATION FIELDS
# ============================================================

def fill_common_fields(page):

    print("\nChecking common application fields...")

    # Experience
    selectors = [
        'input[name*="experience" i]',
        'input[id*="experience" i]',
        'input[aria-label*="experience" i]'
    ]

    for selector in selectors:

        try:

            fields = page.locator(selector)

            for i in range(fields.count()):

                field = fields.nth(i)

                if not is_visible(field):
                    continue

                try:

                    field.fill(
                        str(YEARS_OF_EXPERIENCE)
                    )

                    print(
                        "Filled experience:",
                        YEARS_OF_EXPERIENCE
                    )

                    return

                except Exception:
                    pass

        except Exception:
            pass


# ============================================================
# RADIO BUTTONS
# ============================================================

def inspect_radio_buttons(page):

    print("\nChecking radio buttons...")

    try:

        radios = page.locator(
            'input[type="radio"]'
        )

        count = radios.count()

        if count == 0:

            print("No radio buttons found.")
            return

        print(
            f"Radio buttons found: {count}"
        )

        for i in range(count):

            radio = radios.nth(i)

            print(
                f"\nRADIO {i + 1}"
            )

            print(
                "Value:",
                safe_attribute(radio, "value")
            )

            print(
                "Name:",
                safe_attribute(radio, "name")
            )

            print(
                "Checked:",
                safe_attribute(radio, "checked")
            )

        print(
            "\nRadio answers were NOT guessed or changed."
        )

    except Exception:
        print("Could not inspect radio buttons.")


# ============================================================
# CHECKBOXES
# ============================================================

def inspect_checkboxes(page):

    print("\nChecking checkboxes...")

    try:

        boxes = page.locator(
            'input[type="checkbox"]'
        )

        count = boxes.count()

        if count == 0:

            print("No checkboxes found.")
            return

        print(
            f"Checkboxes found: {count}"
        )

        for i in range(count):

            box = boxes.nth(i)

            print(
                f"CHECKBOX {i + 1}"
            )

            print(
                "Name:",
                safe_attribute(box, "name")
            )

            print(
                "Checked:",
                safe_attribute(box, "checked")
            )

        print(
            "Checkbox answers were NOT guessed or changed."
        )

    except Exception:
        print("Could not inspect checkboxes.")


# ============================================================
# DROPDOWNS
# ============================================================

def inspect_dropdowns(page):

    print("\nChecking dropdowns...")

    try:

        selects = page.locator("select")

        count = selects.count()

        if count == 0:

            print("No native dropdowns found.")
            return

        print(
            f"Dropdowns found: {count}"
        )

        for i in range(count):

            select = selects.nth(i)

            print(
                f"\nDROPDOWN {i + 1}"
            )

            print(
                "Name:",
                safe_attribute(select, "name")
            )

            print(
                "ID:",
                safe_attribute(select, "id")
            )

            options = select.locator("option")

            for j in range(min(options.count(), 15)):

                option = options.nth(j)

                print(
                    "  -",
                    safe_inner_text(option)
                )

    except Exception:
        print("Could not inspect dropdowns.")


# ============================================================
# APPLICATION QUESTION DETECTION
# ============================================================

def detect_questions(page):

    print(
        "\n======================================================================"
    )

    print(
        "APPLICATION QUESTION DETECTION"
    )

    print(
        "======================================================================"
    )

    questions = []

    # --------------------------------------------------------
    # Text-based detection
    # --------------------------------------------------------

    try:

        candidates = page.locator(
            "label, legend"
        )

        for i in range(candidates.count()):

            element = candidates.nth(i)

            if not is_visible(element):
                continue

            text = safe_inner_text(element)

            if not text:
                continue

            # IMPORTANT:
            # Resume filenames are NOT questions.
            if is_resume_text(text):
                continue

            questions.append(text)

    except Exception:
        pass

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    unique_questions = []

    for question in questions:

        normalized = normalize(question)

        if not normalized:
            continue

        if normalized not in [
            normalize(q)
            for q in unique_questions
        ]:

            unique_questions.append(question)

    if not unique_questions:

        print(
            "\nNo application questions detected."
        )

        return []

    for index, question in enumerate(
        unique_questions,
        start=1
    ):

        print(
            f"\nQUESTION {index}"
        )

        print("-" * 50)

        print(question)

    print(
        f"\nQUESTIONS FOUND: {len(unique_questions)}"
    )

    return unique_questions


# ============================================================
# FILL KNOWN EXPERIENCE QUESTIONS
# ============================================================

def fill_known_experience_questions(page):
    """
    Fill experience questions whose answer is explicitly configured.
    This project uses 0 years for Java experience.
    """

    print("\nChecking known experience questions...")

    selectors = [
        'input[aria-label*="experience" i]',
        'input[name*="experience" i]',
        'input[id*="experience" i]',
    ]

    filled = False

    for selector in selectors:
        try:
            fields = page.locator(selector)

            for i in range(fields.count()):
                field = fields.nth(i)

                if not is_visible(field):
                    continue

                aria = safe_attribute(field, "aria-label") or ""
                name = safe_attribute(field, "name") or ""
                field_id = safe_attribute(field, "id") or ""

                combined = normalize(
                    f"{aria} {name} {field_id}"
                )

                if "experience" not in combined:
                    continue

                current = safe_attribute(field, "value") or ""

                if current.strip():
                    print(
                        f"Experience already filled: {current}"
                    )
                    filled = True
                    continue

                field.fill(str(YEARS_OF_EXPERIENCE))

                print(
                    f"Filled experience question with: "
                    f"{YEARS_OF_EXPERIENCE}"
                )

                filled = True

        except Exception:
            continue

    if not filled:
        print("No known experience question found.")

    return filled


# ============================================================
# CLOSE BLOCKING DIALOGS
# ============================================================

def close_blocking_dialogs(page):
    """
    Close visible non-application dialogs that can block Next.
    """

    print("\nChecking for blocking dialogs...")

    closed = False

    try:
        dialogs = page.locator('[role="dialog"]')

        for i in range(dialogs.count()):
            dialog = dialogs.nth(i)

            if not is_visible(dialog):
                continue

            dialog_text = normalize(
                safe_inner_text(dialog)
            )

            # Never close the actual Easy Apply form.
            if (
                "application" in dialog_text
                or "easy apply" in dialog_text
            ):
                continue

            close_selectors = [
                'button[aria-label*="close" i]',
                'button[aria-label*="dismiss" i]',
                '[role="button"][aria-label*="close" i]',
                '[role="button"][aria-label*="dismiss" i]',
            ]

            for selector in close_selectors:
                try:
                    buttons = dialog.locator(selector)

                    for j in range(buttons.count()):
                        button = buttons.nth(j)

                        if not is_visible(button):
                            continue

                        button.click(timeout=3000)
                        page.wait_for_timeout(500)

                        print("Closed blocking dialog.")

                        closed = True
                        break

                    if closed:
                        break

                except Exception:
                    continue

            if closed:
                break

    except Exception:
        pass

    if not closed:
        print("No blocking dialog detected.")

    return closed


# ============================================================
# REQUIRED FIELD CHECK
# ============================================================

def check_required_fields(page):

    print(
        "\n======================================================================"
    )

    print(
        "CHECKING REQUIRED FIELDS"
    )

    print(
        "======================================================================"
    )

    empty_required = []

    try:

        required = page.locator(
            "[required]"
        )

        count = required.count()

        print(
            f"Required elements found: {count}"
        )

        for i in range(count):

            field = required.nth(i)

            if not is_visible(field):
                continue

            value = safe_attribute(
                field,
                "value"
            )

            if value is None:
                value = ""

            if not value.strip():

                empty_required.append(
                    field
                )

        if empty_required:

            print(
                f"Empty required fields: {len(empty_required)}"
            )

        else:

            print(
                "\nNo empty required fields detected."
            )

    except Exception:
        print(
            "Could not inspect required fields."
        )

    return empty_required


# ============================================================
# FIND NEXT / REVIEW / SUBMIT
# ============================================================

def find_next_button(page):

    patterns = [
        r"Next",
        r"Continue",
        r"Review",
        r"Next:.*",
    ]

    for pattern in patterns:

        try:

            buttons = page.get_by_role(
                "button",
                name=re.compile(
                    pattern,
                    re.I
                )
            )

            for i in range(buttons.count()):

                button = buttons.nth(i)

                if is_visible(button):

                    return button

        except Exception:
            pass

    return None


def find_submit_button(page):

    patterns = [
        r"Submit application",
        r"Submit"
    ]

    for pattern in patterns:

        try:

            buttons = page.get_by_role(
                "button",
                name=re.compile(
                    pattern,
                    re.I
                )
            )

            for i in range(buttons.count()):

                button = buttons.nth(i)

                if is_visible(button):

                    return button

        except Exception:
            pass

    return None


# ============================================================
# PROCESS CURRENT APPLICATION PAGE
# ============================================================

def prepare_application_page(page):

    print(
        "\n======================================================================"
    )

    print(
        "PREPARING APPLICATION PAGE"
    )

    print(
        "======================================================================"
    )

    try:

        page_number = page.locator(
            "text=/\\d+\\/\\d+ pages/i"
        ).first.inner_text()

        print(
            "Application page:",
            page_number
        )

    except Exception:

        print(
            "Application page: unknown"
        )

    # --------------------------------------------------------
    # Basic fields
    # --------------------------------------------------------

    print("\nChecking name fields...")
    fill_name_fields(page)

    print("\nChecking email field...")
    fill_email_fields(page)

    print("\nChecking phone field...")
    fill_phone_fields(page)

    select_india_country_code(page)

    # --------------------------------------------------------
    # Resume
    # --------------------------------------------------------

    select_existing_resume(page)

    # --------------------------------------------------------
    # Other fields
    # --------------------------------------------------------

    fill_common_fields(page)

    inspect_radio_buttons(page)

    inspect_checkboxes(page)

    inspect_dropdowns(page)

    detect_questions(page)

    empty_required = check_required_fields(page)

    return empty_required


# ============================================================
# MAIN AUTOMATION FUNCTION
# ============================================================

def inspect_and_prepare_form(page):

    print(
        "\n======================================================================"
    )

    print(
        "APPLICATION FORM AUTOMATION"
    )

    print(
        "======================================================================"
    )

    print(
        "\nResume:",
        RESUME_PATH
    )

    print(
        "Auto Submit:",
        AUTO_SUBMIT
    )

    page_number = 1

    max_pages = 8

    while page_number <= max_pages:

        print(
            "\n======================================================================"
        )

        print(
            f"PROCESSING APPLICATION PAGE {page_number}"
        )

        print(
            "======================================================================"
        )

        page.wait_for_timeout(800)

        prepare_application_page(page)

        # ----------------------------------------------------
        # Check submit button
        # ----------------------------------------------------

        submit_button = find_submit_button(page)

        if submit_button:

            print(
                "\nFinal application page detected."
            )

            print(
                "\n======================================================================"
            )

            print(
                "FINAL APPLICATION REVIEW"
            )

            print(
                "======================================================================"
            )

            print(
                "Submit button found."
            )

            if AUTO_SUBMIT:

                print(
                    "\nAUTO_SUBMIT = True"
                )

                print(
                    "Submitting application..."
                )

                submit_button.click()

                page.wait_for_timeout(3000)

                print(
                    "Application submitted."
                )

            else:

                print(
                    "\nAUTO_SUBMIT = False"
                )

                print(
                    "Application will NOT be submitted."
                )

                print(
                    "Review the application manually."
                )

            break

        # ----------------------------------------------------
        # Find next button
        # ----------------------------------------------------

        next_button = find_next_button(page)

        if not next_button:

            print(
                "\nNext/Continue/Review button not found."
            )

            print(
                "Could not find another page."
            )

            print(
                "Stopping automation."
            )

            break

        try:

            close_blocking_dialogs(page)

            page.wait_for_timeout(300)

            next_button.scroll_into_view_if_needed()

            next_button.click(
                timeout=10000
            )

            page.wait_for_timeout(1200)

            print(
                "\nMoved to next application page."
            )

            page_number += 1

        except Exception as e:

            print(
                "\nNormal Next click failed:"
            )

            print(e)

            try:

                close_blocking_dialogs(page)

                if is_visible(next_button):

                    next_button.click(
                        force=True,
                        timeout=5000
                    )

                    page.wait_for_timeout(1200)

                    print(
                        "\nMoved to next application page "
                        "using fallback click."
                    )

                    page_number += 1

                else:

                    print(
                        "Next button is no longer visible."
                    )

                    break

            except Exception as fallback_error:

                print(
                    "Fallback Next click failed:"
                )

                print(fallback_error)

                break

    print(
        "\n======================================================================"
    )

    print(
        "READY FOR APPLICATION AUTOMATION"
    )

    print(
        "======================================================================"
    )

    return True