from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def chrome_driver(browser_data_dir):
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={browser_data_dir}")
    options.add_argument("--profile-directory=Default")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def find_element_in_shadow_quick(driver, selectors):
    try:
        current = driver
        for selector in selectors:
            host = current.find_element(By.CSS_SELECTOR, selector)
            current = driver.execute_script("return arguments[0].shadowRoot", host)
        return current
    except Exception:
        return None


def wait_for_shadow_element(driver, selectors, timeout=10):
    attempts = 0
    while attempts < timeout:
        element = find_element_in_shadow_quick(driver, selectors)
        if element:
            return element
        attempts += 1
        sleep(1)
    return None
