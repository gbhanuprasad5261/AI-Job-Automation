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

    first_name = "G"
    last_name = "Bhanu Prasad"

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

EDUCATION_DATES = {
    "high_school": {
        "from_month": "June",
        "from_year": "2019",
        "to_month": "April",
        "to_year": "2021",
    },
    "btech": {
        "from_month": "November",
        "from_year": "2021",
        "to_month": "May",
        "to_year": "2025",
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


def fill_education_dates(container, page):
    """Fill dates only when the active LinkedIn education record is known.

    LinkedIn may place the editable education form outside the application
    container returned by get_application_container(). We therefore use the
    full page for education-field discovery while keeping the container for
    the other application controls.
    """
    print()
    print("Checking education date fields...")

    try:
        body = normalize(safe_text(container)).lower()
    except Exception:
        body = ""
    if "dates attended" not in body:
        return False

    school = ""
    try:
        fields = page.locator("input")
        for i in range(fields.count()):
            el = fields.nth(i)
            if safe_attribute(el, "aria-label").strip().lower() == "school":
                school = safe_input_value(el)
                break
    except Exception:
        pass

    school_l = school.lower()
    if "siddhartha" in school_l:
        record = EDUCATION_DATES["btech"]
        record_name = "B.Tech"
    elif "zilla parishad" in school_l or "sri sai" in school_l:
        record = EDUCATION_DATES["high_school"]
        record_name = "High School"
    else:
        print(f"Education record not recognized: {school or '[unknown]'}")
        print("Education dates were NOT guessed or changed.")
        return False

    # The education editor is rendered in the page DOM, but it may be
    # outside the application container. Search the full page here.
    selects = page.locator("select")
    visible_selects = []
    for i in range(selects.count()):
        try:
            select = selects.nth(i)
            if is_visible(select):
                visible_selects.append(select)
        except Exception:
            pass

    # On the education editor LinkedIn exposes four date selects followed by
    # the application language select. Use the first four visible selects
    # belonging to the editor. We identify them by their option contents.
    month_names = {
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    }

    education_selects = []
    for select in visible_selects:
        try:
            option_texts = []
            options = select.locator("option")
            for j in range(min(options.count(), 50)):
                option_texts.append(normalize(safe_text(options.nth(j))).lower())

            has_months = len(month_names.intersection(option_texts)) >= 6
            has_years = sum(1 for text in option_texts if re.fullmatch(r"\d{4}", text)) >= 5

            if has_months or has_years:
                education_selects.append(select)
        except Exception:
            continue

    if len(education_selects) < 4:
        print(
            f"Education date dropdowns incomplete: found {len(education_selects)} education dropdown(s)."
        )
        return False

    empty = []
    for select in education_selects[:4]:
        try:
            if not safe_input_value(select):
                empty.append(select)
        except Exception:
            pass
    for i in range(selects.count()):
        try:
            s = selects.nth(i)
            if is_visible(s) and not safe_input_value(s):
                empty.append(s)
        except Exception:
            pass

    if len(empty) < 4:
        print(f"Education date dropdowns incomplete: found {len(empty)} empty dropdown(s).")
        return False

    fields = [
        ("From Month", empty[0], record["from_month"]),
        ("From Year", empty[1], record["from_year"]),
        ("To Month", empty[2], record["to_month"]),
        ("To Year", empty[3], record["to_year"]),
    ]

    print(f"Education record: {record_name} ({school})")
    for label, select, value in fields:
        if _select_by_label(select, value):
            print(f"{label} selected: {value}")
        else:
            print(f"Could not select {label}: {value}")

    verified = 0
    for label, select, expected in fields:
        actual = safe_input_value(select)
        print(f"{label}: {actual or '[empty]'}")
        if actual:
            verified += 1

    if verified == 4:
        print("Education dates filled and verified.")
        return True
    print(f"Education date verification failed: {verified}/4 fields filled.")
    return False


# ============================================================
# Job-specific application questions
# ============================================================

APPLICATION_ANSWERS = {
    "java_experience": "0",
    "spring_boot_experience": "0",
    "atg_commerce_experience": "0",
    "onsite_comfort": "Yes",
    "cloud_production": "Yes",
    "rest_microservices_production": "Yes",
    "public_facing": "No",
    "current_salary": "0",
    "expected_salary": "5 LPA",
}


def _element_context(element):
    """Return nearby visible text used to identify a LinkedIn form field."""
    texts = []
    try:
        texts.append(safe_text(element))
    except Exception:
        pass

    for xpath in [
        "xpath=ancestor::fieldset[1]",
        "xpath=ancestor::div[.//label][1]",
        "xpath=ancestor::div[.//input][1]",
        "xpath=ancestor::li[1]",
    ]:
        try:
            loc = element.locator(xpath).first
            if loc.count() and is_visible(loc):
                txt = safe_text(loc)
                if txt:
                    texts.append(txt)
        except Exception:
            pass

    return normalize(" ".join(texts)).lower()


def _click_radio_by_question_text(page, question_pattern, answer):
    """
    Answer a radio question by locating the radio group whose nearby DOM
    text contains the question. This is designed for LinkedIn's custom
    radio controls where input value/name labels may be empty.
    """
    try:
        radios = page.locator("input[type='radio']")
        count = radios.count()

        for i in range(count):
            radio = radios.nth(i)
            try:
                if not radio.is_visible():
                    # LinkedIn can hide the actual input behind a styled label;
                    # still allow it if its DOM ancestor is visible.
                    pass

                context = radio.evaluate(
                    """el => {
                        let parts = [];
                        let node = el;
                        for (let i = 0; node && i < 8; i++, node = node.parentElement) {
                            if (node.innerText) parts.push(node.innerText);
                        }
                        return parts.join("\\n");
                    }"""
                ) or ""

                if not re.search(question_pattern, context, re.IGNORECASE):
                    continue

                group_name = radio.get_attribute("name") or ""
                if not group_name:
                    continue

                group = page.locator(
                    "input[type='radio'][name='" +
                    group_name.replace("'", "\\'") +
                    "']"
                )

                if group.count() < 2:
                    continue

                # For the current LinkedIn form the two options are rendered
                # in visible order: Yes, then No.
                index = 0 if answer.lower() == "yes" else 1

                # First try clicking the visible label/text associated with
                # the selected radio.
                candidate = group.nth(index)
                rid = candidate.get_attribute("id") or ""

                if rid:
                    labels = page.locator(f"label[for='{rid}']")
                    for j in range(labels.count()):
                        label = labels.nth(j)
                        if label.is_visible():
                            label.click()
                            page.wait_for_timeout(300)
                            if candidate.is_checked():
                                print(f"Answered: {answer}")
                                return True

                # Fallback: directly check the input.
                candidate.check(force=True)
                page.wait_for_timeout(300)

                if candidate.is_checked():
                    print(f"Answered: {answer}")
                    return True

            except Exception:
                continue

    except Exception:
        pass

    print(f"Could not identify the radio buttons for: {answer}")
    return False


def _click_radio_by_context(container, keywords, answer):
    """Find a radio group whose surrounding question matches keywords."""
    radios = container.locator("input[type='radio']")
    for i in range(radios.count()):
        radio = radios.nth(i)
        if not is_visible(radio):
            continue

        context = _element_context(radio)
        if not all(keyword.lower() in context for keyword in keywords):
            continue

        group_name = safe_attribute(radio, "name")
        group = (
            container.locator(
                f"input[type='radio'][name='{group_name}']"
            )
            if group_name
            else radios
        )

        for j in range(group.count()):
            candidate = group.nth(j)
            candidate_context = _element_context(candidate)
            value = (
                safe_attribute(candidate, "value")
                + " "
                + candidate_context
            ).lower()

            if answer.lower() not in value:
                continue

            try:
                candidate.check(force=True)
                print(f"Answered: {answer}")
                return True
            except Exception:
                pass

            # LinkedIn often uses a label around the radio.
            try:
                rid = safe_attribute(candidate, "id")
                if rid:
                    label = container.locator(
                        f"label[for='{rid}']"
                    ).first
                    if label.count() and is_visible(label):
                        label.click()
                        print(f"Answered: {answer}")
                        return True
            except Exception:
                pass

        # Also try visible Yes/No labels inside the same group.
        try:
            parent = radio.locator("xpath=ancestor::fieldset[1]").first
            if parent.count():
                labels = parent.locator("label")
                for j in range(labels.count()):
                    label = labels.nth(j)
                    if not is_visible(label):
                        continue
                    label_text = normalize(safe_text(label)).lower()
                    if label_text == answer.lower():
                        label.click()
                        print(f"Answered: {answer}")
                        return True
        except Exception:
            pass

    return False


def _fill_text_by_context(container, keywords, value, display_name):
    """Fill an empty text/number field whose nearby question matches keywords."""
    fields = container.locator("input, textarea")
    for i in range(fields.count()):
        field = fields.nth(i)
        if not is_visible(field):
            continue

        field_type = safe_attribute(field, "type").lower()
        if field_type in {
            "hidden", "file", "radio", "checkbox",
            "button", "submit"
        }:
            continue

        context = _element_context(field)
        if not all(keyword.lower() in context for keyword in keywords):
            continue

        if fill_if_empty(field, value):
            print(f"{display_name}: {value}")
            return True

    return False


def fill_known_application_questions(container, page=None):
    """
    Fill only the application questions for which the user supplied explicit
    answers. No experience, salary, cloud, or production claims are guessed.
    """
    print()
    print("=" * 70)
    print("FILLING KNOWN APPLICATION QUESTIONS")
    print("=" * 70)

    filled = 0

    # Experience questions: the user has hands-on/training experience, not
    # professional years of employment, so both are explicitly 0.
    if _fill_text_by_context(
        container,
        ["java", "experience"],
        APPLICATION_ANSWERS["java_experience"],
        "Java experience",
    ):
        filled += 1

    if _fill_text_by_context(
        container,
        ["spring", "boot", "experience"],
        APPLICATION_ANSWERS["spring_boot_experience"],
        "Spring Boot experience",
    ):
        filled += 1

    # Current Diligente Technologies question:
    # "Are you comfortable working in an onsite setting?" -> Yes.
    if page is not None and _click_radio_by_question_text(
        page,
        r"Are you comfortable working in an onsite setting\?",
        APPLICATION_ANSWERS["onsite_comfort"],
    ):
        filled += 1

    # ATG Commerce professional experience -> 0 years.
    # Hands-on/training experience is not counted as professional employment.
    if _fill_text_by_context(
        container,
        ["atg", "commerce", "experience"],
        APPLICATION_ANSWERS["atg_commerce_experience"],
        "ATG Commerce experience",
    ):
        filled += 1

    # Yes/No production questions.
    if _click_radio_by_context(
        container,
        ["cloud", "production"],
        APPLICATION_ANSWERS["cloud_production"],
    ):
        filled += 1

    if _click_radio_by_context(
        container,
        ["rest", "microservices", "production"],
        APPLICATION_ANSWERS["rest_microservices_production"],
    ):
        filled += 1

    if _click_radio_by_context(
        container,
        ["public", "facing"],
        APPLICATION_ANSWERS["public_facing"],
    ):
        filled += 1

    # Salary questions. Use "current" and "salary/compensation", and
    # "expected" and "salary/compensation", so unrelated numeric fields are
    # not touched.
    if _fill_text_by_context(
        container,
        ["current", "salary"],
        APPLICATION_ANSWERS["current_salary"],
        "Current salary",
    ):
        filled += 1

    if _fill_text_by_context(
        container,
        ["expected", "salary"],
        APPLICATION_ANSWERS["expected_salary"],
        "Expected salary",
    ):
        filled += 1

    print(f"Known application answers filled: {filled}")
    return filled

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
    # Explicit application answers supplied by the user
    # --------------------------------------------------------

    fill_known_application_questions(
        container,
        page
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

    before_text = ""
    try:
        before_text = normalize(
            get_application_container(page).inner_text()
        )
    except Exception:
        pass

    for _ in range(20):
        page.wait_for_timeout(500)
        after = get_application_step(page)

        if before and after:
            if after[1] == before[1] and after[0] > before[0]:
                print("Moved to next application page.")
                print(f"New application step: {after[0]}/{after[1]}")
                return True

        elif not before and after:
            print(
                f"Application step detected after navigation: "
                f"{after[0]}/{after[1]}"
            )
            return True

        # LinkedIn can temporarily keep the progress indicator at 3/4.
        # Detect actual modal content replacement as a fallback.
        try:
            after_text = normalize(
                get_application_container(page).inner_text()
            )
            if (
                before_text
                and after_text
                and after_text != before_text
                and len(after_text) > 20
            ):
                print("Application form content changed.")
                if after:
                    print(f"Current application step: {after[0]}/{after[1]}")
                return True
        except Exception:
            pass

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

        page.wait_for_timeout(
            3000
        )

        print()
        print(
            "APPLICATION SUBMITTED"
        )

        return True

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

    max_pages = 6

    for page_number in range(
        1,
        max_pages + 1
    ):

        print()
        print(
            "=" * 70
        )

        print(
            f"PROCESSING APPLICATION PAGE "
            f"{page_number}"
        )

        print(
            "=" * 70
        )

        if job_is_closed(page):

            print(
                "Job/application is closed."
            )

            return False

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