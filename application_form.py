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

AUTO_SUBMIT = True

# Unknown questions are never guessed. Optional unknown questions are left
# untouched. Required unknown questions cause the current job to be skipped.
UNKNOWN_QUESTIONS_POLICY = "SKIP"


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

def _field_has_value(field):
    """Return True when a required LinkedIn control is actually populated."""
    try:
        tag = (field.evaluate("(e) => e.tagName") or "").upper()
    except Exception:
        tag = ""

    # Native input/textarea/select values.
    if tag in ("INPUT", "TEXTAREA", "SELECT"):
        try:
            value = field.input_value()
        except Exception:
            value = safe_attribute(field, "value") or ""

        if str(value).strip():
            return True

        # A select can have a selected option even when value handling differs.
        if tag == "SELECT":
            try:
                selected = field.locator("option:checked").first
                if selected.count() > 0:
                    return bool(safe_inner_text(selected).strip())
            except Exception:
                pass

        return False

    # Custom LinkedIn combobox/listbox controls.
    try:
        aria_value = safe_attribute(field, "aria-valuetext") or ""
        if aria_value.strip():
            return True

        text = safe_inner_text(field)
        if text.strip():
            return True
    except Exception:
        pass

    return False


def _required_field_description(field):
    """Produce useful diagnostics for a required field."""
    try:
        tag = field.evaluate("(e) => e.tagName")
    except Exception:
        tag = ""

    aria = safe_attribute(field, "aria-label") or ""
    name = safe_attribute(field, "name") or ""
    field_id = safe_attribute(field, "id") or ""
    placeholder = safe_attribute(field, "placeholder") or ""

    return (
        f"tag={tag}, aria={aria!r}, name={name!r}, "
        f"id={field_id!r}, placeholder={placeholder!r}"
    )


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
        # Native required controls.
        required = page.locator(
            "input[required], textarea[required], select[required], "
            "[role='combobox'][aria-required='true'], "
            "[role='listbox'][aria-required='true']"
        )

        count = required.count()

        print(
            f"Required elements found: {count}"
        )

        for i in range(count):

            field = required.nth(i)

            if not is_visible(field):
                continue

            if not _field_has_value(field):
                empty_required.append(field)

        # LinkedIn frequently puts aria-required on a wrapper while the
        # actual input/select is nested inside it. Check those wrappers too.
        wrappers = page.locator(
            "[aria-required='true']"
        )

        for i in range(wrappers.count()):

            wrapper = wrappers.nth(i)

            if not is_visible(wrapper):
                continue

            # Skip native controls already covered above.
            try:
                tag = (wrapper.evaluate("(e) => e.tagName") or "").upper()
            except Exception:
                tag = ""

            if tag in ("INPUT", "TEXTAREA", "SELECT"):
                continue

            # Prefer nested native controls.
            nested = wrapper.locator(
                "input, textarea, select, [role='combobox'], [role='listbox']"
            )

            if nested.count() > 0:
                has_value = False

                for j in range(nested.count()):
                    child = nested.nth(j)

                    if not is_visible(child):
                        continue

                    if _field_has_value(child):
                        has_value = True
                        break

                if not has_value:
                    # Avoid duplicate entries.
                    if not any(
                        existing == wrapper
                        for existing in empty_required
                    ):
                        empty_required.append(wrapper)
                continue

            # Custom required control with its own displayed value.
            if not _field_has_value(wrapper):
                if not any(
                    existing == wrapper
                    for existing in empty_required
                ):
                    empty_required.append(wrapper)

        if empty_required:

            print(
                f"Empty required fields: {len(empty_required)}"
            )

            for index, field in enumerate(
                empty_required,
                start=1
            ):
                print(
                    f"  REQUIRED {index}: "
                    f"{_required_field_description(field)}"
                )

        else:

            print(
                "\nNo empty required fields detected."
            )

    except Exception as e:

        print(
            "Could not inspect required fields:",
            e
        )

    return empty_required


# ============================================================
# EASY APPLY DIALOG / NAVIGATION
# ============================================================

def find_application_dialog(page):
    """
    Locate LinkedIn's Easy Apply form without relying on role="dialog".

    The live LinkedIn form observed for this project is rendered without
    role="dialog". It exposes a progress marker such as "1/4 pages" and a
    local Next/Continue/Review button. We therefore anchor detection to
    those application-specific markers and never use a global LinkedIn
    button by itself.
    """

    try:
        body_text = safe_inner_text(page.locator("body"))

        if not re.search(
            r"\b\d+\s*/\s*\d+\s+pages?\b",
            body_text,
            re.I,
        ):
            return None

        if not re.search(
            r"\bapply\s+to\b",
            body_text,
            re.I,
        ):
            return None

        # First: use a real dialog if LinkedIn exposes one.
        dialogs = page.locator('[role="dialog"]')

        for i in range(dialogs.count()):
            dialog = dialogs.nth(i)

            if not is_visible(dialog):
                continue

            text = normalize(safe_inner_text(dialog))

            if (
                re.search(r"\b\d+\s*/\s*\d+\s+pages?\b", text, re.I)
                and (
                    "apply to" in text
                    or "contact info" in text
                    or "application" in text
                )
            ):
                return dialog

        # Current LinkedIn implementation: find the actual application
        # navigation button and walk upward until the application container
        # is reached. Page 1 has "Next"; later pages may have Back + Next.
        nav_buttons = page.locator(
            'button, [role="button"]'
        )

        target_patterns = (
            r"^\s*Next\s*$",
            r"^\s*Continue\s*$",
            r"^\s*Review\s*$",
            r"^\s*Submit\s+application\s*$",
            r"^\s*Submit\s*$",
        )

        for i in range(nav_buttons.count()):
            button = nav_buttons.nth(i)

            if not is_visible(button):
                continue

            label = normalize(
                safe_inner_text(button)
                or safe_attribute(button, "aria-label")
                or ""
            )

            if not any(
                re.fullmatch(pattern, label, re.I)
                for pattern in target_patterns
            ):
                continue

            container = button

            for _ in range(18):
                try:
                    container = container.locator("xpath=..")

                    if not is_visible(container):
                        break

                    text = normalize(
                        safe_inner_text(container)
                    )

                    has_progress = bool(
                        re.search(
                            r"\b\d+\s*/\s*\d+\s+pages?\b",
                            text,
                            re.I,
                        )
                    )

                    has_application_marker = (
                        "apply to" in text
                        or "contact info" in text
                        or "additional questions" in text
                        or "application" in text
                    )

                    if has_progress and has_application_marker:
                        return container

                except Exception:
                    break

        # Last fallback: use the progress marker and walk upward.
        # This is intentionally conservative: it only succeeds when an
        # application-specific marker is present.
        progress = page.locator(
            r"text=/\b\d+\s*\/\s*\d+\s+pages?\b/i"
        )

        for i in range(progress.count()):
            marker = progress.nth(i)

            if not is_visible(marker):
                continue

            container = marker

            for _ in range(18):
                try:
                    container = container.locator("xpath=..")

                    if not is_visible(container):
                        break

                    text = normalize(
                        safe_inner_text(container)
                    )

                    if (
                        re.search(
                            r"\b\d+\s*/\s*\d+\s+pages?\b",
                            text,
                            re.I,
                        )
                        and (
                            "apply to" in text
                            or "contact info" in text
                            or "additional questions" in text
                            or "application" in text
                        )
                    ):
                        return container

                except Exception:
                    break

    except Exception as e:
        print(
            f"Could not identify Easy Apply container: {e}"
        )

    return None

def fill_known_application_questions(page):
    """
    Fill only answers explicitly configured for this project.

    Observed Diligente form:
      - onsite setting -> Yes
      - ATG Commerce experience -> 0 years

    Unknown questions are never guessed.
    """

    print("\nChecking known application questions...")
    filled = 0

    # Onsite question -> Yes
    try:
        question = page.get_by_text(
            re.compile(
                r"Are you comfortable working in an onsite setting",
                re.I,
            )
        ).last

        if is_visible(question):
            container = question
            for _ in range(8):
                try:
                    container = container.locator("xpath=..")
                    if not is_visible(container):
                        break

                    text = normalize(safe_inner_text(container))
                    if "comfortable working in an onsite setting" not in text:
                        continue

                    yes = container.get_by_text(
                        re.compile(r"^Yes$", re.I)
                    ).last

                    if is_visible(yes):
                        yes.click()
                        page.wait_for_timeout(200)
                        print("Answered onsite question: Yes")
                        filled += 1
                        break
                except Exception:
                    continue
    except Exception:
        pass

    # ATG Commerce experience -> configured value (0)
    try:
        fields = page.locator(
            'input[aria-label*="ATG Commerce" i], '
            'input[name*="ATG" i], '
            'input[id*="ATG" i]'
        )

        for i in range(fields.count()):
            field = fields.nth(i)
            if not is_visible(field):
                continue

            field.fill(str(YEARS_OF_EXPERIENCE))
            field.press("Tab")
            page.wait_for_timeout(200)

            print(
                "ATG Commerce experience:",
                YEARS_OF_EXPERIENCE
            )
            filled += 1
            break
    except Exception:
        pass

    if filled == 0:
        print("No configured application questions found on this page.")

    return filled


def fill_java_experience(page):
    """Fill the known Java experience question with the configured value."""

    print("\nChecking Java experience question...")

    selector = (
        'input[aria-label*="How many years of work experience '
        'do you have with Java" i]'
    )

    try:
        fields = page.locator(selector)

        for i in range(fields.count()):
            field = fields.nth(i)

            if not is_visible(field):
                continue

            value = safe_attribute(field, "value") or ""

            if value.strip() == str(YEARS_OF_EXPERIENCE):
                print(
                    "Java experience already filled:",
                    YEARS_OF_EXPERIENCE
                )
                return True

            field.fill(str(YEARS_OF_EXPERIENCE))
            field.press("Tab")
            page.wait_for_timeout(300)

            print(
                "Java experience filled:",
                YEARS_OF_EXPERIENCE
            )
            return True

    except Exception as e:
        print("Could not fill Java experience:", e)

    print("Java experience field not found on this page.")
    return False


def find_next_button(page):
    """
    Find Next/Continue/Review ONLY inside Easy Apply.

    This deliberately ignores LinkedIn carousel controls.
    """

    dialog = find_application_dialog(page)

    if dialog is None:
        print(
            "Easy Apply dialog not identified; "
            "refusing to click a global Next button."
        )
        return None

    patterns = [
        r"^Next$",
        r"^Continue$",
        r"^Review$",
        r"^Next:.*",
    ]

    for pattern in patterns:

        try:
            buttons = dialog.get_by_role(
                "button",
                name=re.compile(pattern, re.I)
            )

            for i in range(buttons.count()):

                button = buttons.nth(i)

                if not is_visible(button):
                    continue

                testid = (
                    safe_attribute(button, "data-testid")
                    or ""
                )

                if "carousel" in testid.lower():
                    continue

                return button

        except Exception:
            continue

    return None


def find_submit_button(page):

    dialog = find_application_dialog(page)

    if dialog is None:
        return None

    patterns = [
        r"^Submit application$",
        r"^Submit$",
    ]

    for pattern in patterns:

        try:

            buttons = dialog.get_by_role(
                "button",
                name=re.compile(pattern, re.I)
            )

            for i in range(buttons.count()):

                button = buttons.nth(i)

                if not is_visible(button):
                    continue

                testid = (
                    safe_attribute(button, "data-testid")
                    or ""
                )

                if "carousel" in testid.lower():
                    continue

                return button

        except Exception:
            continue

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

    # Handle only explicitly configured questions.
    fill_known_application_questions(page)

    # Keep the Java-specific handler for forms that expose the exact field.
    fill_java_experience(page)

    inspect_radio_buttons(page)

    inspect_checkboxes(page)

    inspect_dropdowns(page)

    detect_questions(page)

    empty_required = check_required_fields(page)

    return empty_required



def mark_application_submitted():
    """
    Explicit submission marker.

    This function intentionally does nothing unless the caller has actually
    reached and clicked the final Submit button. It prevents application
    status from being treated as APPLIED merely because the form was opened.
    """
    return True


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

        # Keep the required-field result. Never submit while an unsupported
        # required field is empty.
        empty_required = prepare_application_page(page)

        if empty_required:
            print("\nRequired fields are still empty after preparation.")
            print("The application will NOT be submitted.")
            print("Returning a safe skip status for this job.")
            return "SKIPPED_REQUIRED_UNKNOWN"

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

                page.wait_for_timeout(3500)

                # Do not trust the click alone. LinkedIn can close or
                # re-render the form without actually confirming submission.
                confirmation_text = normalize(
                    safe_inner_text(page.locator("body"))
                )

                confirmation_patterns = (
                    "application submitted",
                    "application was submitted",
                    "application has been submitted",
                    "you've applied",
                    "you have applied",
                    "application sent",
                    "your application was sent",
                )

                confirmed = any(
                    phrase in confirmation_text
                    for phrase in confirmation_patterns
                )

                if confirmed:
                    print(
                        "Application submission confirmed."
                    )
                    return "SUBMITTED"

                print(
                    "Submit was clicked, but LinkedIn did not expose "
                    "a recognizable submission confirmation."
                )
                print(
                    "Application will NOT be marked APPLIED."
                )
                return "SUBMIT_UNCONFIRMED"

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

                print(
                    "\nAPPLICATION STATUS: READY_FOR_REVIEW"
                )

                return "READY_FOR_REVIEW"

            return "SUBMITTED"

        # ----------------------------------------------------
        # Find next button
        # ----------------------------------------------------

        # Verify required fields before attempting navigation.
        current_empty_required = check_required_fields(page)

        if current_empty_required:
            print(
                "\nRequired fields are still empty."
            )
            print(
                "Unknown/unsupported required question detected."
            )
            print(
                "UNKNOWN_QUESTIONS_POLICY = SKIP"
            )
            print(
                "Skipping this job safely; no application will be submitted."
            )
            return "SKIPPED_REQUIRED_UNKNOWN"

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

            before_body = page.locator("body").inner_text()

            # Read the progress before clicking.
            before_match = re.search(
                r"\b(\d+)\s*/\s*(\d+)\s+pages?\b",
                before_body,
                re.IGNORECASE
            )
            before_step = (
                (int(before_match.group(1)), int(before_match.group(2)))
                if before_match
                else None
            )

            next_button.click(
                timeout=10000
            )

            advanced = False

            # Wait for a real application transition.
            for _ in range(20):
                page.wait_for_timeout(400)

                after_body = page.locator("body").inner_text()

                after_match = re.search(
                    r"\b(\d+)\s*/\s*(\d+)\s+pages?\b",
                    after_body,
                    re.IGNORECASE
                )

                after_step = (
                    (int(after_match.group(1)), int(after_match.group(2)))
                    if after_match
                    else None
                )

                if before_step and after_step:
                    if (
                        after_step[1] == before_step[1]
                        and after_step[0] > before_step[0]
                    ):
                        advanced = True
                        print(
                            "\nMoved to next application page."
                        )
                        print(
                            f"New application step: "
                            f"{after_step[0]}/{after_step[1]}"
                        )
                        break

                # If progress text is temporarily unavailable, require a
                # substantial body change before treating the click as success.
                if (
                    not before_step
                    and after_body != before_body
                    and len(after_body) > 100
                ):
                    advanced = True
                    print(
                        "\nApplication form content changed."
                    )
                    break

            if not advanced:
                print(
                    "\nNext click did not advance the application page."
                )
                if before_step:
                    print(
                        f"Still at {before_step[0]}/{before_step[1]}."
                    )
                print(
                    "Stopping safely."
                )
                break

            page_number += 1

        except Exception as e:

            print(
                "\nNext button click failed:"
            )

            print(e)

            print(
                "Stopping safely; no force-click will be used."
            )

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

    return "STOPPED"
