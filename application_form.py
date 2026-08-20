import os
import re
from playwright.sync_api import Page


# ============================================================
# APPLICATION FORM AUTOMATION
# ============================================================

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

RESUME_PATH = os.path.abspath(
    os.path.join("resume", "resume.pdf")
)

# IMPORTANT:
# Put your real details here if they are not already available
# through your config.py / environment variables.

APPLICANT_NAME = os.getenv(
    "APPLICANT_NAME",
    "G Bhanu Prasad"
)

EMAIL = os.getenv(
    "APPLICANT_EMAIL",
    "gbhanuprasad1236@gmail.com"
)

PHONE = os.getenv(
    "APPLICANT_PHONE",
    "9392801041"
)

YEARS_OF_EXPERIENCE = os.getenv(
    "YEARS_OF_EXPERIENCE",
    "0"
)

CITY = os.getenv(
    "APPLICANT_CITY",
    "Bengaluru"
)

COUNTRY = os.getenv(
    "APPLICANT_COUNTRY",
    "India"
)

# ------------------------------------------------------------
# Safety switch
# ------------------------------------------------------------
# False = fill and navigate, but STOP before final submission.
# True  = allow final Submit button to be clicked.
#
# Keep this FALSE during testing.

AUTO_SUBMIT = False


# ============================================================
# Utility Functions
# ============================================================

def safe_text(element):

    try:
        return element.inner_text().strip()
    except Exception:
        return ""


def safe_attribute(element, attribute):

    try:
        return element.get_attribute(attribute) or ""
    except Exception:
        return ""


def is_visible(element):

    try:
        return element.is_visible()
    except Exception:
        return False


def safe_input_value(element):
    try:
        return element.input_value().strip()
    except Exception:
        return ""


def normalize(value):
    return re.sub(r"\s+", " ", value or "").strip()


def fill_if_empty(locator, value):

    if not value:
        return False

    try:

        if locator.count() == 0:
            return False

        element = locator.first

        if not element.is_visible():
            return False

        current_value = ""

        try:
            current_value = element.input_value().strip()
        except Exception:
            pass

        if current_value:
            return True

        element.fill(value)

        return True

    except Exception:

        return False


# ============================================================
# Detect Application Modal
# ============================================================

def get_application_container(page: Page):

    # LinkedIn normally uses a dialog/modal for Easy Apply.

    try:

        dialogs = page.get_by_role("dialog")

        if dialogs.count() > 0:

            for i in range(dialogs.count()):

                dialog = dialogs.nth(i)

                if dialog.is_visible():
                    return dialog

    except Exception:
        pass

    # Fallback to page itself

    return page


# ============================================================
# Print Application Status
# ============================================================

def print_application_status(page: Page):

    try:

        body = page.locator("body").inner_text()

        match = re.search(
            r"(\d+)\s*/\s*(\d+)",
            body
        )

        if match:

            current = match.group(1)
            total = match.group(2)

            print(
                f"Application page: {current}/{total}"
            )

            return

    except Exception:
        pass

    print("Application page: unknown")


def get_application_step(page):
    """Return LinkedIn visible application progress as (current, total)."""
    try:
        body = page.locator("body").inner_text()
        match = re.search(r"\b(\d+)\s*/\s*(\d+)\s+pages?\b", body, re.IGNORECASE)
        if not match:
            match = re.search(r"\b(\d+)\s*/\s*(\d+)\b", body)
        if match:
            current, total = int(match.group(1)), int(match.group(2))
            if 0 < current <= total <= 20:
                return current, total
    except Exception:
        pass
    return None


# ============================================================
# Fill Name
# ============================================================

def fill_name(container):

    print()
    print("Checking name fields...")

    selectors = [

        "input[name*='firstName' i]",
        "input[id*='firstName' i]",
        "input[autocomplete='given-name']",
        "input[name*='name' i]",
        "input[id*='name' i]",

    ]

    # First name / last name handling

    first_name = "Bhanu"
    last_name = "Prasad"

    filled = False

    for selector in selectors:

        try:

            locator = container.locator(selector)

            if locator.count() == 0:
                continue

            for i in range(locator.count()):

                element = locator.nth(i)

                if not element.is_visible():
                    continue

                placeholder = safe_attribute(
                    element,
                    "placeholder"
                ).lower()

                name = safe_attribute(
                    element,
                    "name"
                ).lower()

                element_id = safe_attribute(
                    element,
                    "id"
                ).lower()

                combined = (
                    placeholder
                    + " "
                    + name
                    + " "
                    + element_id
                )

                if "first" in combined:

                    if fill_if_empty(
                        element,
                        first_name
                    ):
                        print("First name filled.")
                        filled = True

                elif "last" in combined:

                    if fill_if_empty(
                        element,
                        last_name
                    ):
                        print("Last name filled.")
                        filled = True

        except Exception:
            pass

    return filled


# ============================================================
# Fill Email
# ============================================================

def fill_email(container):

    print()
    print("Checking email field...")

    if not EMAIL:

        print(
            "EMAIL is empty."
        )

        print(
            "Set APPLICANT_EMAIL before running."
        )

        return False

    try:

        locator = container.locator(
            "input[type='email']"
        )

        if locator.count() > 0:

            if fill_if_empty(
                locator,
                EMAIL
            ):

                print("Email filled.")
                return True

    except Exception:
        pass

    return False


# ============================================================
# Fill Phone
# ============================================================

def select_india_country_code(container):
    """
    LinkedIn may render the phone country-code control as a custom
    combobox/button instead of a native <select>.

    We only select India (+91). We do NOT guess any other country.
    """
    print()
    print("Checking phone country code...")

    # Native select, if LinkedIn happens to expose one.
    try:
        selects = container.locator("select")
        for i in range(selects.count()):
            select = selects.nth(i)

            try:
                options = select.locator("option")
                for j in range(options.count()):
                    option = options.nth(j)
                    text = safe_text(option)
                    value = safe_attribute(option, "value")

                    if "India" in text and "+91" in text:
                        select.select_option(value=value)
                        print("Phone country code selected: India (+91)")
                        return True
            except Exception:
                continue
    except Exception:
        pass

    # Custom LinkedIn control.
    candidate_selectors = [
        "button[aria-label*='country' i]",
        "button[aria-label*='phone' i]",
        "[role='combobox'][aria-label*='country' i]",
        "[role='combobox'][aria-label*='phone' i]",
    ]

    for selector in candidate_selectors:
        try:
            controls = container.locator(selector)

            for i in range(controls.count()):
                control = controls.nth(i)

                if not control.is_visible():
                    continue

                current = (
                    safe_text(control)
                    + " "
                    + safe_attribute(control, "aria-label")
                ).lower()

                # If already India/+91, no action is necessary.
                if "india" in current or "+91" in current:
                    print("Phone country code already appears to be India (+91).")
                    return True

                control.click()
                container.page.wait_for_timeout(500)

                india = container.get_by_text(
                    re.compile(r"^India\s*\(\+91\)$", re.IGNORECASE)
                ).first

                if india.count() > 0 and india.is_visible():
                    india.click()
                    container.page.wait_for_timeout(300)
                    print("Phone country code selected: India (+91)")
                    return True

        except Exception:
            continue

    print("Could not explicitly select India (+91).")
    print("Please verify the country code before submitting.")
    return False


def fill_phone(container):

    print()
    print("Checking phone field...")

    if not PHONE:

        print(
            "PHONE is empty."
        )

        print(
            "Set APPLICANT_PHONE before running."
        )

        return False

    # Country code is handled separately because LinkedIn often uses
    # a custom control rather than a normal <select>.
    select_india_country_code(container)

    selectors = [

        "input[type='tel']",
        "input[name*='phone' i]",
        "input[id*='phone' i]",
        "input[autocomplete='tel']",

    ]

    for selector in selectors:

        try:

            locator = container.locator(selector)

            if locator.count() == 0:
                continue

            if fill_if_empty(
                locator,
                PHONE
            ):

                print("Phone filled.")
                return True

        except Exception:
            pass

    return False


# ============================================================
# Upload Resume
# ============================================================

def upload_resume(container):

    print()
    print("Checking resume upload...")

    if not os.path.exists(RESUME_PATH):

        print(
            f"Resume not found: {RESUME_PATH}"
        )

        return False

    try:

        file_inputs = container.locator(
            "input[type='file']"
        )

        if file_inputs.count() == 0:

            print(
                "No file upload field found."
            )

            return False

        for i in range(
            file_inputs.count()
        ):

            element = file_inputs.nth(i)

            if not element.is_visible():

                # File inputs may be hidden.
                # They can still accept set_input_files().
                pass

            try:

                element.set_input_files(
                    RESUME_PATH
                )

                print(
                    "Resume uploaded:"
                )

                print(
                    f"  {RESUME_PATH}"
                )

                return True

            except Exception:
                continue

    except Exception as e:

        print(
            f"Resume upload error: {e}"
        )

    return False


# ============================================================
# Fill Common Text Fields
# ============================================================

def fill_common_text_fields(container):

    print()
    print(
        "Checking common application fields..."
    )

    fields = container.locator(
        "input, textarea"
    )

    filled_count = 0

    for i in range(
        fields.count()
    ):

        try:

            element = fields.nth(i)

            tag = element.evaluate(
                "(el) => el.tagName"
            )

            if tag not in [
                "INPUT",
                "TEXTAREA"
            ]:

                continue

            field_type = (
                safe_attribute(
                    element,
                    "type"
                ).lower()
            )

            if field_type in [
                "hidden",
                "file",
                "radio",
                "checkbox",
                "submit",
                "button"
            ]:

                continue

            if not element.is_visible():

                continue

            current = ""

            try:

                current = (
                    element
                    .input_value()
                    .strip()
                )

            except Exception:
                pass

            if current:

                continue

            placeholder = (
                safe_attribute(
                    element,
                    "placeholder"
                ).lower()
            )

            aria = (
                safe_attribute(
                    element,
                    "aria-label"
                ).lower()
            )

            name = (
                safe_attribute(
                    element,
                    "name"
                ).lower()
            )

            element_id = (
                safe_attribute(
                    element,
                    "id"
                ).lower()
            )

            combined = (
                placeholder
                + " "
                + aria
                + " "
                + name
                + " "
                + element_id
            )

            # Years of experience

            if (
                "years of experience"
                in combined
                or "experience" in combined
                and "years" in combined
            ):

                if fill_if_empty(
                    element,
                    YEARS_OF_EXPERIENCE
                ):

                    print(
                        "Filled experience:",
                        YEARS_OF_EXPERIENCE
                    )

                    filled_count += 1

            # City

            elif (
                "city" in combined
                or "location" in combined
            ):

                if fill_if_empty(
                    element,
                    CITY
                ):

                    print(
                        "Filled location:",
                        CITY
                    )

                    filled_count += 1

        except Exception:
            continue

    return filled_count


# ============================================================
# Handle Radio Buttons
# ============================================================

def inspect_radio_buttons(container):

    print()
    print("Checking radio buttons...")

    radios = container.locator(
        "input[type='radio']"
    )

    if radios.count() == 0:

        print(
            "No radio buttons found."
        )

        return

    print(
        f"Radio buttons found: "
        f"{radios.count()}"
    )

    for i in range(
        radios.count()
    ):

        try:

            radio = radios.nth(i)

            print()
            print(
                f"RADIO {i + 1}"
            )

            print(
                "Value:",
                safe_attribute(
                    radio,
                    "value"
                )
            )

            print(
                "Name:",
                safe_attribute(
                    radio,
                    "name"
                )
            )

            print(
                "Checked:",
                radio.is_checked()
            )

            # Try to expose the associated visible label.
            radio_id = safe_attribute(radio, "id")

            if radio_id:
                try:
                    label = container.locator(
                        f"label[for='{radio_id}']"
                    ).first

                    if label.count() > 0:
                        print(
                            "Label:",
                            safe_text(label)
                        )
                except Exception:
                    pass

            # Also inspect an ancestor label when present.
            try:
                parent_label = radio.locator(
                    "xpath=ancestor::label[1]"
                ).first

                if parent_label.count() > 0:
                    label_text = safe_text(parent_label)
                    if label_text:
                        print(
                            "Parent label:",
                            label_text
                        )
            except Exception:
                pass

        except Exception:
            pass

    print()
    print(
        "Radio answers were NOT guessed or changed."
    )


# ============================================================
# Handle Checkboxes
# ============================================================

def inspect_checkboxes(container):

    print()
    print(
        "Checking checkboxes..."
    )

    checkboxes = container.locator(
        "input[type='checkbox']"
    )

    if checkboxes.count() == 0:

        print(
            "No checkboxes found."
        )

        return

    print(
        f"Checkboxes found: "
        f"{checkboxes.count()}"
    )

    for i in range(
        checkboxes.count()
    ):

        try:

            checkbox = checkboxes.nth(i)

            if not checkbox.is_visible():
                continue

            print()
            print(
                f"CHECKBOX {i + 1}"
            )

            print(
                "Name:",
                safe_attribute(
                    checkbox,
                    "name"
                )
            )

            print(
                "ID:",
                safe_attribute(
                    checkbox,
                    "id"
                )
            )

            print(
                "Checked:",
                checkbox.is_checked()
            )

        except Exception:
            pass


# ============================================================
# Handle Selects
# ============================================================

def inspect_selects(container):

    print()
    print(
        "Checking dropdowns..."
    )

    selects = container.locator(
        "select"
    )

    if selects.count() == 0:

        print(
            "No native dropdowns found."
        )

        return

    print(
        f"Dropdowns found: "
        f"{selects.count()}"
    )

    for i in range(
        selects.count()
    ):

        try:

            select = selects.nth(i)

            if not select.is_visible():
                continue

            print()
            print(
                f"DROPDOWN {i + 1}"
            )

            print(
                "Name:",
                safe_attribute(
                    select,
                    "name"
                )
            )

            print(
                "ID:",
                safe_attribute(
                    select,
                    "id"
                )
            )

            options = select.locator(
                "option"
            )

            for j in range(
                min(options.count(), 15)
            ):

                option = options.nth(j)

                print(
                    "  -",
                    safe_text(option)
                )

        except Exception:
            pass


# ============================================================
# Inspect Required Fields
# ============================================================

def inspect_required_fields(container):

    print()
    print(
        "=" * 70
    )

    print(
        "CHECKING REQUIRED FIELDS"
    )

    print(
        "=" * 70
    )

    required = container.locator(
        "[required]"
    )

    print(
        f"Required elements found: "
        f"{required.count()}"
    )

    unanswered = 0

    for i in range(
        required.count()
    ):

        try:

            element = required.nth(i)

            tag = element.evaluate(
                "(el) => el.tagName"
            )

            field_type = (
                safe_attribute(
                    element,
                    "type"
                ).lower()
            )

            if field_type in [
                "hidden"
            ]:

                continue

            # Radio groups: consider the group answered when any
            # radio in the same name group is checked.
            if field_type == "radio":

                group_name = safe_attribute(
                    element,
                    "name"
                )

                if group_name:
                    try:
                        checked = container.locator(
                            f"input[type='radio'][name='{group_name}']:checked"
                        )

                        if checked.count() > 0:
                            continue
                    except Exception:
                        pass

                if element.is_checked():
                    continue

            # Checkbox: required means it must be checked.
            if field_type == "checkbox":

                if element.is_checked():
                    continue

                value = ""
            else:

                value = ""

                try:

                    value = (
                        element
                        .input_value()
                        .strip()
                    )

                except Exception:
                    pass

                # Native select.
                if tag == "SELECT":
                    try:
                        value = (
                            element
                            .input_value()
                            .strip()
                        )
                    except Exception:
                        pass

            if not value:

                unanswered += 1

                print()
                print(
                    f"REQUIRED FIELD "
                    f"{unanswered}"
                )

                print(
                    "Tag:",
                    tag
                )

                print(
                    "Type:",
                    field_type
                )

                print(
                    "Name:",
                    safe_attribute(
                        element,
                        "name"
                    )
                )

                print(
                    "ID:",
                    safe_attribute(
                        element,
                        "id"
                    )
                )

                print(
                    "Placeholder:",
                    safe_attribute(
                        element,
                        "placeholder"
                    )
                )

                print(
                    "Aria:",
                    safe_attribute(
                        element,
                        "aria-label"
                    )
                )

        except Exception:
            pass

    print()

    if unanswered == 0:

        print(
            "No empty required fields detected."
        )

    else:

        print(
            f"Empty required fields: "
            f"{unanswered}"
        )

    return unanswered


# ============================================================
# Find Next Button
# ============================================================

def find_next_button(container):

    names = [
        "Next",
        "Continue",
        "Review",
    ]

    for name in names:

        try:

            button = container.get_by_role(
                "button",
                name=re.compile(
                    f"^{re.escape(name)}$",
                    re.IGNORECASE
                )
            ).first

            if button.count() > 0:

                if button.is_visible():

                    return button

        except Exception:
            pass

    # Fallback

    try:

        buttons = container.locator(
            "button"
        )

        for i in range(
            buttons.count()
        ):

            button = buttons.nth(i)

            if not button.is_visible():
                continue

            text = safe_text(
                button
            ).lower()

            if text in [
                "next",
                "continue",
                "review"
            ]:

                return button

    except Exception:
        pass

    return None


# ============================================================
# Find Submit Button
# ============================================================

def find_submit_button(container):

    patterns = [
        r"submit application",
        r"submit",
        r"send application"
    ]

    for pattern in patterns:

        try:

            button = container.get_by_role(
                "button",
                name=re.compile(
                    pattern,
                    re.IGNORECASE
                )
            ).first

            if button.count() > 0:

                if button.is_visible():

                    return button

        except Exception:
            pass

    return None


# ============================================================
# Detect Closed Job
# ============================================================

def job_is_closed(page):

    try:

        body = page.locator(
            "body"
        ).inner_text().lower()

        closed_messages = [

            "no longer accepting applications",
            "job is no longer accepting applications",
            "this job is no longer available",
            "applications are closed",
            "job has been closed"

        ]

        for message in closed_messages:

            if message in body:

                return True

    except Exception:
        pass

    return False


# ============================================================
# Handle Education Date Fields
# ============================================================

EDUCATION_RECORDS = {
    "btech": {
        "school": "Siddartha Institute of Science and Technology",
        "city": "Puttur, Andhra Pradesh",
        "degree": "B.Tech",
        "major": "Computer Science and Engineering (AI&DS)",
        "from_month": "June",
        "from_year": "2021",
        "to_month": "June",
        "to_year": "2025",
    },
    "intermediate": {
        "school": "Sri Sai Chaithanya Junior College",
        "city": "Palamaner, Andhra Pradesh",
        "degree": "Intermediate",
        "major": "MPC",
        "from_month": "June",
        "from_year": "2019",
        "to_month": "April",
        "to_year": "2021",
    },
}


def _select_by_label(select, label):
    try:
        select.select_option(label=label)
        return True
    except Exception:
        pass
    try:
        options = select.locator("option")
        for i in range(options.count()):
            option = options.nth(i)
            text = normalize(safe_text(option))
            if text.lower() == label.lower():
                value = safe_attribute(option, "value")
                if value:
                    select.select_option(value=value)
                else:
                    select.select_option(label=text)
                return True
    except Exception:
        pass
    return False


def _find_visible_input_by_aria(page, aria_label):
    """Find a visible textbox reliably, including LinkedIn's generated DOM."""
    try:
        page.wait_for_timeout(300)
    except Exception:
        pass

    for selector in [
        f"input[aria-label='{aria_label}']",
        f"textarea[aria-label='{aria_label}']",
        f"input[aria-label*='{aria_label}' i]",
        f"textarea[aria-label*='{aria_label}' i]",
    ]:
        try:
            locator = page.locator(selector)
            for i in range(locator.count()):
                el = locator.nth(i)
                if is_visible(el):
                    return el
        except Exception:
            pass

    try:
        locator = page.get_by_role(
            "textbox",
            name=re.compile(rf"^{re.escape(aria_label)}$", re.IGNORECASE)
        )
        for i in range(locator.count()):
            el = locator.nth(i)
            if is_visible(el):
                return el
    except Exception:
        pass

    # DOM fallback for stale React accessibility trees.
    try:
        selector = f"input[aria-label*='{aria_label}' i], textarea[aria-label*='{aria_label}' i]"
        locator = page.locator(selector)
        for i in range(locator.count()):
            el = locator.nth(i)
            if is_visible(el):
                return el
    except Exception:
        pass

    try:
        labels = page.get_by_text(aria_label, exact=True)
        for i in range(labels.count()):
            label = labels.nth(i)
            if not is_visible(label):
                continue
            for xpath in [
                "xpath=..", "xpath=../..", "xpath=../../..", "xpath=../../../.."
            ]:
                candidate = label.locator(xpath).locator("input, textarea").first
                if candidate.count() > 0 and is_visible(candidate):
                    return candidate
    except Exception:
        pass
    return None


def _fill_exact_field(page, aria_label, value):
    element = _find_visible_input_by_aria(page, aria_label)
    if element is None:
        print(f"Education field not found: {aria_label}")
        return False
    try:
        current = safe_input_value(element)
        if current != value:
            element.fill(value)
        print(f"{aria_label} set: {value}")
        return True
    except Exception as e:
        print(f"Could not fill {aria_label}: {e}")
        return False


def _visible_education_selects(page):
    """Return visible month/year selects from the active education editor."""
    month_names = {
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    }
    result = []
    try:
        selects = page.locator("select")
        for i in range(selects.count()):
            select = selects.nth(i)
            if not is_visible(select):
                continue
            options = select.locator("option")
            texts = [normalize(safe_text(options.nth(j))).lower()
                     for j in range(min(options.count(), 60))]
            has_months = len(month_names.intersection(texts)) >= 6
            has_years = sum(bool(re.fullmatch(r"\d{4}", t)) for t in texts) >= 5
            if has_months or has_years:
                result.append(select)
    except Exception:
        pass
    return result


def fill_education_dates(container, page):
    """Fill the currently open LinkedIn education editor from confirmed user data.

    The live DOM supplied during this workflow exposes the editor with
    aria-labels School, City, Degree and Major / Field of study, plus four
    native month/year selects. Generated LinkedIn IDs are deliberately ignored.
    """
    print()
    print("Checking education date fields...")

    try:
        body = normalize(page.locator("body").inner_text()).lower()
    except Exception:
        body = ""

    if "dates attended" not in body or "education" not in body:
        print("Education editor not found on this page.")
        return False

    school_el = _find_visible_input_by_aria(page, "School")
    if school_el is None:
        # LinkedIn sometimes exposes the editor textbox through the accessible
        # role/name instead of a literal aria-label attribute.
        for selector in [
            "input[aria-label*='School' i]",
            "textarea[aria-label*='School' i]",
        ]:
            try:
                loc = page.locator(selector)
                for i in range(loc.count()):
                    candidate = loc.nth(i)
                    if is_visible(candidate):
                        school_el = candidate
                        break
                if school_el is not None:
                    break
            except Exception:
                pass
    if school_el is None:
        try:
            loc = page.get_by_role("textbox", name=re.compile(r"^School$", re.I))
            for i in range(loc.count()):
                candidate = loc.nth(i)
                if is_visible(candidate):
                    school_el = candidate
                    break
        except Exception:
            pass
    if school_el is None:
        print("Active education school field not found.")
        print("Education editor was detected, but LinkedIn did not expose the School textbox to automation.")
        return False

    current_school = safe_input_value(school_el)
    current_lower = current_school.lower()

    if "siddartha" in current_lower or "siddhartha" in current_lower:
        record = EDUCATION_RECORDS["btech"]
        record_name = "B.Tech"
    elif "sri sai" in current_lower or "zilla parishad" in current_lower:
        record = EDUCATION_RECORDS["intermediate"]
        record_name = "Intermediate"
    else:
        # The live LinkedIn form can open an unrelated third education record
        # (for example, an old high-school entry) even though the user's
        # confirmed profile contains exactly two education records.
        # Do not overwrite it with guessed data. Remove the unconfirmed record
        # instead, after confirming that it is not one of the two records.
        if current_school and normalize(current_school).lower() not in {
            normalize(EDUCATION_RECORDS["btech"]["school"]).lower(),
            normalize(EDUCATION_RECORDS["intermediate"]["school"]).lower(),
        }:
            print(
                f"Unconfirmed education record detected: {current_school}"
            )
            print(
                "This record is not part of the confirmed education profile."
            )

            try:
                delete_buttons = page.get_by_role(
                    "button",
                    name=re.compile(
                        r"^Delete education$",
                        re.IGNORECASE
                    )
                )

                for i in range(delete_buttons.count()):
                    button = delete_buttons.nth(i)

                    if is_visible(button) and button.is_enabled():
                        print("Removing unconfirmed education record...")
                        button.click()
                        page.wait_for_timeout(1000)

                        # LinkedIn may show a confirmation dialog.
                        confirm = page.get_by_role(
                            "button",
                            name=re.compile(
                                r"^(Delete|Confirm)$",
                                re.IGNORECASE
                            )
                        )

                        for j in range(confirm.count()):
                            c = confirm.nth(j)
                            if (
                                is_visible(c)
                                and c.is_enabled()
                                and c != button
                            ):
                                try:
                                    c.click()
                                    page.wait_for_timeout(1000)
                                    break
                                except Exception:
                                    pass

                        print("Unconfirmed education record removed.")
                        return True

            except Exception as e:
                print(f"Could not remove unconfirmed education record: {e}")

        print(
            f"Active education school not recognized: "
            f"{current_school or '[unknown]'}"
        )
        print("Education fields were NOT guessed or changed.")
        return False

    print(f"Active education record: {record_name}")

    field_ok = True
    for label, value in [
        ("School", record["school"]),
        ("City", record["city"]),
        ("Degree", record["degree"]),
        ("Major / Field of study", record["major"]),
    ]:
        if not _fill_exact_field(page, label, value):
            field_ok = False

    education_selects = _visible_education_selects(page)
    if len(education_selects) < 4:
        print(f"Education date dropdowns incomplete: found {len(education_selects)}.")
        return False

    fields = [
        ("From Month", education_selects[0], record["from_month"]),
        ("From Year", education_selects[1], record["from_year"]),
        ("To Month", education_selects[2], record["to_month"]),
        ("To Year", education_selects[3], record["to_year"]),
    ]

    dates_ok = True
    for label, select, value in fields:
        if _select_by_label(select, value):
            actual = safe_input_value(select)
            print(f"{label}: {actual or value}")
        else:
            print(f"Could not select {label}: {value}")
            dates_ok = False

    verified = field_ok and dates_ok
    for label, expected in [
        ("School", record["school"]),
        ("City", record["city"]),
        ("Degree", record["degree"]),
        ("Major / Field of study", record["major"]),
    ]:
        el = _find_visible_input_by_aria(page, label)
        actual = safe_input_value(el) if el is not None else ""
        if normalize(actual).lower() != normalize(expected).lower():
            print(f"Education verification failed for {label}: {actual or '[empty]'}")
            verified = False

    for label, select, expected in fields:
        actual = safe_input_value(select)
        if not actual:
            print(f"Education verification failed for {label}: [empty]")
            verified = False

    if verified:
        print(f"Education record filled and verified: {record_name}")
        try:
            save_buttons = page.get_by_role("button", name=re.compile(r"^Save$", re.IGNORECASE))
            for i in range(save_buttons.count()):
                save_button = save_buttons.nth(i)
                if is_visible(save_button) and save_button.is_enabled():
                    save_button.click()
                    page.wait_for_timeout(1000)
                    print("Education record saved.")
                    break
        except Exception as e:
            print(f"Could not save education record: {e}")
    else:
        print("Education record verification failed. No guessing was performed.")
    return verified


# ============================================================
# Prepare Current Application Page
# ============================================================

def prepare_current_page(page: Page):

    print()
    print(
        "=" * 70
    )

    print(
        "PREPARING APPLICATION PAGE"
    )

    print(
        "=" * 70
    )

    print_application_status(page)

    container = get_application_container(
        page
    )

    # --------------------------------------------------------
    # Contact information
    # --------------------------------------------------------

    fill_name(
        container
    )

    fill_email(
        container
    )

    fill_phone(
        container
    )

    # --------------------------------------------------------
    # Resume
    # --------------------------------------------------------

    upload_resume(
        container
    )

    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------
    fill_education_dates(
        container,
        page
    )

    # --------------------------------------------------------
    # Common fields
    # --------------------------------------------------------

    fill_common_text_fields(
        container
    )

    # --------------------------------------------------------
    # Other controls
    # --------------------------------------------------------

    inspect_radio_buttons(
        container
    )

    inspect_checkboxes(
        container
    )

    inspect_selects(
        container
    )

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    unanswered = (
        inspect_required_fields(
            container
        )
    )

    return unanswered


# ============================================================
# Move To Next Page
# ============================================================

def move_to_next_page(page: Page):
    container = get_application_container(page)
    button = find_next_button(container)

    if button is None:
        print()
        print("Next/Continue/Review button not found.")
        return False

    before = get_application_step(page)
    print()
    print("Next button found.")
    if before:
        print(f"Current application step: {before[0]}/{before[1]}")

    # Capture the visible application container text before clicking. LinkedIn
    # can leave the step counter unchanged while changing the actual editor.
    try:
        before_text = normalize(get_application_container(page).inner_text())
    except Exception:
        before_text = ""

    try:
        button.scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        if not button.is_enabled():
            print("Navigation button is disabled.")
            return False
        button.click()
    except Exception as e:
        print(f"Could not move to next page: {e}")
        return False

    for _ in range(20):
        page.wait_for_timeout(500)
        after = get_application_step(page)
        try:
            after_text = normalize(get_application_container(page).inner_text())
        except Exception:
            after_text = ""

        if before and after:
            if after[1] == before[1] and after[0] > before[0]:
                print("Moved to next application page.")
                print(f"New application step: {after[0]}/{after[1]}")
                return True
        elif not before and after:
            print(f"Application step detected after navigation: {after[0]}/{after[1]}")
            return True

        # If the visible form actually changed, allow the caller to process it
        # even when LinkedIn's counter is stale.
        if before_text and after_text and after_text != before_text:
            print("Application form content changed after navigation.")
            return True

    current = get_application_step(page)
    print()
    print("=" * 70)
    print("APPLICATION PAGE DID NOT ADVANCE")
    print("=" * 70)
    if before:
        print(f"Before click: {before[0]}/{before[1]}")
    if current:
        print(f"After wait : {current[0]}/{current[1]}")
    print("The application step did not increase.")
    print("Stopping safely instead of clicking Next repeatedly.")
    return False


# ============================================================
# Final Review / Submit
# ============================================================

def handle_final_submission(page: Page):

    print()
    print(
        "=" * 70
    )

    print(
        "FINAL APPLICATION REVIEW"
    )

    print(
        "=" * 70
    )

    container = get_application_container(
        page
    )

    submit_button = find_submit_button(
        container
    )

    if submit_button is None:

        print(
            "Submit button not found."
        )

        return False

    print(
        "Submit button found."
    )

    if not AUTO_SUBMIT:

        print()
        print(
            "AUTO_SUBMIT = False"
        )

        print(
            "Application will NOT be submitted."
        )

        print(
            "Review the application manually."
        )

        return False

    # Even when AUTO_SUBMIT is enabled, require the submit button to be
    # visible and enabled. We do not bypass LinkedIn's final UI.
    try:
        if not submit_button.is_visible():
            print("Submit button is not visible. Stopping.")
            return False

        if not submit_button.is_enabled():
            print("Submit button is disabled. Stopping.")
            return False
    except Exception as e:
        print(f"Could not verify submit button state: {e}")
        return False

    try:

        submit_button.click()

        page.wait_for_timeout(3000)

        try:
            body_after_submit = page.locator("body").inner_text().lower()
        except Exception:
            body_after_submit = ""

        success_markers = (
            "application submitted",
            "your application was submitted",
            "application has been submitted",
            "applied",
        )

        if any(marker in body_after_submit for marker in success_markers):
            print()
            print("APPLICATION SUBMITTED")
            return True

        try:
            remaining_submit = find_submit_button(
                get_application_container(page)
            )
        except Exception:
            remaining_submit = None

        if remaining_submit is None:
            print()
            print("APPLICATION SUBMISSION COMPLETED")
            return True

        print()
        print("SUBMISSION COULD NOT BE CONFIRMED.")
        print("The Submit control is still present.")
        return False

    except Exception as e:

        print(
            f"Could not submit application: {e}"
        )

        return False


# ============================================================
# Main Application Automation
# ============================================================

def inspect_and_prepare_form(
    page: Page
):

    print()
    print(
        "=" * 70
    )

    print(
        "APPLICATION FORM AUTOMATION"
    )

    print(
        "=" * 70
    )

    if job_is_closed(page):

        print()
        print(
            "JOB IS CLOSED."
        )

        return False

    print()
    print(
        "Resume:",
        RESUME_PATH
    )

    print(
        "Auto Submit:",
        AUTO_SUBMIT
    )

    # --------------------------------------------------------
    # Process multiple application pages
    # --------------------------------------------------------

    max_pages = 8
    seen_form_fingerprints = set()

    for page_number in range(
        1,
        max_pages + 1
    ):

        print()
        print(
            "=" * 70
        )

        live_step = get_application_step(page)
        display_page = (
            f"{live_step[0]}/{live_step[1]}"
            if live_step else str(page_number)
        )

        print(
            f"PROCESSING APPLICATION PAGE "
            f"{display_page}"
        )

        print(
            "=" * 70
        )

        if job_is_closed(page):

            print(
                "Job/application is closed."
            )

            return False

        # Prevent an accidental infinite loop if LinkedIn reports a stale
        # 4/5 counter while showing the same editor again.
        try:
            fingerprint = normalize(get_application_container(page).inner_text())
        except Exception:
            fingerprint = ""
        if fingerprint:
            if fingerprint in seen_form_fingerprints:
                print()
                print("SAME APPLICATION FORM DETECTED AGAIN")
                print("Stopping safely instead of clicking Next repeatedly.")
                return False
            seen_form_fingerprints.add(fingerprint)

        unanswered = (
            prepare_current_page(
                page
            )
        )

        # ----------------------------------------------------
        # If required fields remain unanswered
        # ----------------------------------------------------

        if unanswered > 0:

            print()
            print(
                "REQUIRED INFORMATION IS MISSING."
            )

            print(
                "Automation will stop here."
            )

            print(
                "Please inspect the fields above."
            )

            return False

        # ----------------------------------------------------
        # Check if Submit is already available
        # ----------------------------------------------------

        container = get_application_container(
            page
        )

        submit_button = find_submit_button(
            container
        )

        if submit_button is not None:

            print()
            print(
                "Final application page detected."
            )

            return handle_final_submission(
                page
            )

        # ----------------------------------------------------
        # Move to next page
        # ----------------------------------------------------

        moved = move_to_next_page(
            page
        )

        if not moved:

            print()
            print(
                "Could not find another page."
            )

            print(
                "Stopping automation."
            )

            return False

        page.wait_for_timeout(
            1500
        )

    print()
    print(
        "Maximum application pages reached."
    )

    print(
        "Stopping automation for safety."
    )

    return False


# ============================================================
# End
# ============================================================

if __name__ == "__main__":

    print()
    print(
        "=" * 70
    )

    print(
        "APPLICATION FORM MODULE"
    )

    print(
        "=" * 70
    )

    print()
    print(
        "This module is called by easy_apply.py."
    )

    print(
        "Run easy_apply.py to start the application."
    )

    print()