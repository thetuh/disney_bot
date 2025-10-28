from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from browser import find_element_in_shadow_quick, wait_for_shadow_element

def log_in(driver, email, password):
    driver.get("https://disneyworld.disney.go.com/entry-reservation/add/select-party/")

    wait = WebDriverWait(driver, 10)
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'oneid-iframe')))

    email_input = None
    attempts = 0

    while not email_input and attempts < 10:
        driver.switch_to.default_content()
        if find_element_in_shadow_quick(driver, [
            "body > tnp-reservations-spa",
            "#currentPage > tnp-add-reservation-select-party-page",
            "#partySelector"
        ]):
            print('[+] Detected active session, skipping login')
            return

        try:
            driver.switch_to.frame(driver.find_element(By.ID, 'oneid-iframe'))
            email_input = driver.find_element(By.ID, 'InputIdentityFlowValue')
        except NoSuchElementException:
            pass

        attempts += 1
        sleep(0.5)

    if not email_input:
        raise Exception('[!] Email input not found')

    email_input.send_keys(email)

    continue_button = wait.until(EC.presence_of_element_located((By.ID, 'BtnSubmit')))
    continue_button.click()
    password_input = wait.until(EC.presence_of_element_located((By.ID, 'InputPassword')))
    password_input.send_keys(password)
    continue_button = wait.until(EC.presence_of_element_located((By.ID, 'BtnSubmit')))
    continue_button.click()

    attempts = 0
    submitted_otp = False

    while attempts != 10:
        attempts += 1
        sleep(0.5)
        if driver.find_elements(By.CSS_SELECTOR, "form.otp-prompt-redeem") and not submitted_otp:
            otp_code = input('[!] Email 2FA required. Please input 6-digit code\n').strip()

            otp_container = driver.find_element(By.ID, "InputRedeemOTP")
            otp_inputs = otp_container.find_elements(By.CSS_SELECTOR, "input.field")

            if len(otp_code) != len(otp_inputs):
                raise ValueError("[!] Entered code doesn't match the number of input boxes")

            for digit, input_field in zip(otp_code, otp_inputs):
                input_field.send_keys(digit)

            continue_button = wait.until(EC.presence_of_element_located((By.ID, 'BtnSubmit')))
            continue_button.click()
            submitted_otp = True
            attempts = 0
        elif driver.find_elements(By.CSS_SELECTOR, "form.otp-request-lockout"):
            raise Exception('Email 2FA lockout')
        elif find_element_in_shadow_quick(driver, [
            "body > tnp-reservations-spa",
            "#currentPage > tnp-add-reservation-select-party-page",
            "#partySelector"
        ]):
            break

    if attempts >= 10:
        raise Exception('Failed to log in, max attempts reached')


def select_party(driver, name_list):
    party_selector_shadow = wait_for_shadow_element(driver, [
        "body > tnp-reservations-spa",
        "#currentPage > tnp-add-reservation-select-party-page",
        "#partySelector"
    ])
    if not party_selector_shadow:
        raise Exception("[!] Failed to find party selector shadow")
    
    lower_names = {n.lower() for n in name_list}
    selected_names = set()

    for list_id in ["#TICKETGuestList", "#MEPGuestList"]:
        try:
            guest_list_container = party_selector_shadow.find_element(By.CSS_SELECTOR, list_id)
            guest_list_ul = guest_list_container.find_element(By.CSS_SELECTOR, "ul.guestList")
            guests = guest_list_ul.find_elements(By.CSS_SELECTOR, "li.listItem")

            for guest in guests:
                try:
                    checkbox_container = guest.find_element(By.CSS_SELECTOR, "div.checkboxContainer")
                    pass_card = checkbox_container.find_element(By.CSS_SELECTOR, "tnp-pass-card")
                    pass_card_shadow = driver.execute_script("return arguments[0].shadowRoot", pass_card)

                    name_el = pass_card_shadow.find_element(
                        By.CSS_SELECTOR, "div > div.passDetails > div.guestName.guestSensitiveHigh > h3"
                    )
                    name = name_el.text.strip()
                    name_lower = name.lower()

                    if name_lower in lower_names:
                        selected_names.add(name_lower)
                        com_checkbox = checkbox_container.find_element(By.CSS_SELECTOR, "com-checkbox")
                        checkbox_shadow = driver.execute_script("return arguments[0].shadowRoot", com_checkbox)
                        actual_checkbox = checkbox_shadow.find_element(By.CSS_SELECTOR, "#checkbox")

                        is_checked = driver.execute_script(
                            "return arguments[0].checked || arguments[0].getAttribute('aria-checked') === 'true';",
                            actual_checkbox
                        )

                        if not is_checked:
                            driver.execute_script("arguments[0].click();", actual_checkbox)
                            print(f"[+] Selected guest: {name}")
                        else:
                            print(f"[+] Guest already selected: {name}")

                except Exception as e:
                    print(f"[!] Could not process guest element: {e}")

        except Exception:
            pass

    missing = lower_names - selected_names
    if missing:
        print(f"[!] The following guest(s) were not found: {', '.join(missing)}")

    dock_bar_shadow = find_element_in_shadow_quick(driver, [
        "body > tnp-reservations-spa",
        "#currentPage > tnp-add-reservation-select-party-page",
        "#reservationPageDockBar"
    ])
    next_button = WebDriverWait(dock_bar_shadow, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#nextButton"))
    )
    driver.execute_script("arguments[0].click();", next_button)


def select_date(driver, date_str):
    try:
        calendar_shadow = wait_for_shadow_element(driver, [
            "body > tnp-reservations-spa",
            "#currentPage > tnp-add-reservation-select-date-page",
            "#ticketsReservationsCalendar"
        ])
        if not calendar_shadow:
            raise Exception("[!] Failed to find calendar shadow")

        date_selector = f'com-calendar-date[date="{date_str}"]'
        date_element = WebDriverWait(calendar_shadow, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, date_selector))
        )

        date_class = date_element.get_attribute('class')
        if 'all-gtg' in date_class:
            print(f"[+] No reservation required for {date_str}")
            driver.execute_script("arguments[0].click();", date_element)
        elif 'all' in date_class:
            print(f"[+] All parks available for {date_str}")
            driver.execute_script("arguments[0].click();", date_element)
        elif 'primary' in date_class:
            print(f"[-] Some parks may not be available for {date_str}")
            driver.execute_script("arguments[0].click();", date_element)
        else:
            print(f"[!] Unknown date class for {date_str}")

    except TimeoutException:
        print(f"[!] Date '{date_str}' not found on the calendar")


def select_park(driver, park_id):
    try:
        park_selector_shadow = find_element_in_shadow_quick(driver, [
            "body > tnp-reservations-spa",
            "#currentPage > tnp-add-reservation-select-date-page",
            "#timeslotsContainer > div > div > tnp-park-type"
        ])

        park_button = park_selector_shadow.find_element(By.CSS_SELECTOR, f"#{park_id}")
        aria_disabled = park_button.get_attribute("aria-disabled")
        if aria_disabled == "true":
            raise Exception('park not available')
        else:
            driver.execute_script("arguments[0].click();", park_button)
            print(f"[+] Selected park: {park_id}")

        dock_bar_shadow = find_element_in_shadow_quick(driver, [
            "body > tnp-reservations-spa",
            "#currentPage > tnp-add-reservation-select-date-page",
            "#reservationPageDockBar"
        ])
        next_button = dock_bar_shadow.find_element(By.CSS_SELECTOR, "#nextButton")
        driver.execute_script("arguments[0].click();", next_button)

    except Exception as e:
        print(f"[!] Could not select park '{park_id}': {e}")
