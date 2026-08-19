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

def _radio_label_text(container, radio):
    """Return the most useful visible answer label for a radio input."""
    radio_id = safe_attribute(radio, "id")

    if radio_id:
        try:
            label = container.locator(f"label[for='{radio_id}']").first
            if label.count() > 0:
                text = safe_text(label)
                if text:
                    return text
        except Exception:
            pass

    try:
        parent = radio.locator("xpath=ancestor::label[1]").first
        if parent.count() > 0:
            text = safe_text(parent)
            if text:
                return text
    except Exception:
        pass

    try:
        # LinkedIn sometimes puts the visible answer text in a sibling/span.
        text = radio.locator("xpath=following-sibling::*[1]").first.inner_text().strip()
        if text:
            return text
    except Exception:
        pass

    return ""


def _radio_question_text(container, radio):
    """Find nearby text that represents the question for a radio group."""
    try:
        fieldset = radio.locator("xpath=ancestor::fieldset[1]").first
        if fieldset.count() > 0:
            legend = fieldset.locator("legend").first
            if legend.count() > 0:
                text = safe_text(legend)
                if text:
                    return text
            text = safe_text(fieldset)
            if text:
                return text
    except Exception:
        pass

    # Walk upward through a few likely LinkedIn question containers.
    for xpath in [
        "xpath=ancestor::*[self::div or self::li][.//input[@type='radio']][1]",
        "xpath=ancestor::*[self::div or self::section][.//input[@type='radio']][1]",
    ]:
        try:
            parent = radio.locator(xpath).first
            if parent.count() == 0:
                continue
            text = safe_text(parent)
            if text:
                # Keep it bounded so debug output remains readable.
                return text[:1200]
        except Exception:
            continue

    return ""


def _choose_safe_radio_answer(question, answers):
    """Return a safe answer label for common factual application questions.

    We only answer questions that can be derived from this applicant's configured
    profile. Unknown questions are deliberately left unresolved.
    """
    q = (question or "").lower()
    normalized = [(a, (a or "").strip().lower()) for a in answers]

    def find(*terms):
        for label, low in normalized:
            if all(term in low for term in terms):
                return label
        return None

    # Work authorization / sponsorship questions.
    if any(x in q for x in [
        "authorized to work", "legally authorized", "right to work",
        "eligible to work", "work authorization"
    ]):
        if any(x in q for x in ["sponsor", "sponsorship", "visa"]):
            return find("no") or find("not")
        return find("yes")

    if any(x in q for x in [
        "require sponsorship", "need sponsorship", "future sponsorship",
        "visa sponsorship"
    ]):
        return find("no") or find("not")

    # Experience questions.  The configured value is 0, so only select an
    # exact zero/entry-level answer; never fabricate experience.
    if any(x in q for x in [
        "years of experience", "years experience", "professional experience"
    ]):
        for label, low in normalized:
            if re.search(r"(^|\D)0(\D|$)", low) or "no experience" in low or "fresher" in low:
                return label

    return None


def inspect_radio_buttons(container):
    """Inspect radio groups and safely answer only known questions.

    Returns the number of unresolved radio groups. A non-zero value prevents
    navigation/submission so the automation never guesses an application answer.
    """
    print()
    print("Checking radio buttons...")

    radios = container.locator("input[type='radio']")
    total = radios.count()

    if total == 0:
        print("No radio buttons found.")
        return 0

    # Group by name; LinkedIn normally gives all answers in a question the same name.
    groups = {}
    unnamed = []

    for i in range(total):
        try:
            radio = radios.nth(i)
            if not radio.is_visible():
                continue
            name = safe_attribute(radio, "name").strip()
            if name:
                groups.setdefault(name, []).append(radio)
            else:
                unnamed.append(radio)
        except Exception:
            continue

    for radio in unnamed:
        groups.setdefault(f"__unnamed_{len(groups)}", []).append(radio)

    unresolved = 0

    print(f"Radio groups found: {len(groups)}")

    for group_index, group in enumerate(groups.values(), start=1):
        try:
            first = group[0]
            question = _radio_question_text(container, first)
            answers = [_radio_label_text(container, r) for r in group]
            answers = [a for a in answers if a]

            print()
            print(f"RADIO GROUP {group_index}")
            print("Question:", question or "Unknown")
            print("Answers:")
            for n, answer in enumerate(answers, start=1):
                print(f"  {n}. {answer}")

            chosen = _choose_safe_radio_answer(question, answers)

            if chosen:
                # Find the actual radio whose label matched the chosen answer.
                clicked = False
                for radio in group:
                    label = _radio_label_text(container, radio)
                    if label.strip().lower() == chosen.strip().lower():
                        try:
                            radio.check(force=True)
                            clicked = True
                            break
                        except Exception:
                            try:
                                radio.click(force=True)
                                clicked = True
                                break
                            except Exception:
                                pass

                if clicked:
                    print("Selected safe answer:", chosen)
                    continue

            # Never accept an unexplained/default checked answer as a safe answer.
            checked = any(radio.is_checked() for radio in group)
            if checked:
                print("WARNING: A radio option is already selected, but the question was not safely recognized.")
            else:
                print("WARNING: No radio option selected.")

            print("This radio question requires manual review.")
            unresolved += 1

        except Exception as e:
            print(f"Could not inspect radio group: {e}")
            unresolved += 1

    print()
    if unresolved == 0:
        print("All radio questions were answered safely.")
    else:
        print(f"Unresolved radio groups: {unresolved}")
        print("Automation will stop before continuing.")

    return unresolved


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

    unresolved_radios = inspect_radio_buttons(
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

    # Treat unresolved radio questions as blocking issues.
    if unresolved_radios > 0:
        unanswered += unresolved_radios

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