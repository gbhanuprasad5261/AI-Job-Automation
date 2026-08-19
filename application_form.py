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
# Detect Application Questions
# ============================================================

def detect_application_questions(container):
    """Inspect and print visible application questions without guessing answers."""

    print()
    print("=" * 70)
    print("APPLICATION QUESTION DETECTION")
    print("=" * 70)

    questions_found = []
    seen = set()

    selectors = [
        "fieldset",
        "[role='group']",
        ".jobs-easy-apply-form-section__grouping",
        ".fb-dash-form-element",
    ]

    for selector in selectors:
        try:
            groups = container.locator(selector)

            for i in range(groups.count()):
                group = groups.nth(i)

                if not group.is_visible():
                    continue

                text = safe_text(group)

                if not text or len(text) > 1200:
                    continue

                controls = group.locator(
                    "input, textarea, select, "
                    "[role='radio'], [role='checkbox'], [role='combobox']"
                )

                if controls.count() == 0:
                    continue

                normalized = re.sub(r"\s+", " ", text).strip()

                if normalized and normalized not in seen:
                    seen.add(normalized)
                    questions_found.append(normalized)

        except Exception:
            continue

    if not questions_found:
        try:
            labels = container.locator(
                "label, legend, [data-test-form-element-label]"
            )

            for i in range(labels.count()):
                label = labels.nth(i)

                if not label.is_visible():
                    continue

                text = safe_text(label)
                normalized = re.sub(r"\s+", " ", text).strip()

                if normalized and normalized not in seen:
                    seen.add(normalized)
                    questions_found.append(normalized)

        except Exception:
            pass

    if not questions_found:
        print()
        print("No application questions detected.")
    else:
        for index, question in enumerate(questions_found, start=1):
            print()
            print(f"QUESTION {index}")
            print("-" * 50)
            print(question)

        print()
        print("=" * 70)
        print(f"QUESTIONS FOUND: {len(questions_found)}")
        print("=" * 70)

    return questions_found


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
    # Application questions
    # --------------------------------------------------------

    detect_application_questions(
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

    container = get_application_container(
        page
    )

    button = find_next_button(
        container
    )

    if button is None:

        print()
        print(
            "Next/Continue/Review button "
            "not found."
        )

        return False

    try:

        print()
        print(
            "Next button found."
        )

        button.scroll_into_view_if_needed()

        page.wait_for_timeout(
            500
        )

        button.click()

        page.wait_for_timeout(
            2000
        )

        print(
            "Moved to next application page."
        )

        return True

    except Exception as e:

        print(
            f"Could not move to next page: {e}"
        )

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

    max_pages = 10

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