import traceback
from config import load_config, park_name_to_id, BROWSER_DATA_DIR
from browser import chrome_driver
from reservation import log_in, select_party, select_date, select_park

def main():
    config = load_config()

    park_id = park_name_to_id.get(config['park'])
    if not park_id:
        raise ValueError(f"[!] Unknown park name in config.ini: {config['park']}")
    
    driver = chrome_driver(BROWSER_DATA_DIR)

    try:
        log_in(driver, config['email'], config['password'])
        select_party(driver, config['guest_list'])
        select_date(driver, config['date'])
        select_park(driver, park_id)

    except Exception:
        traceback.print_exc()

    finally:
        input('Press Enter to quit\n')
        driver.quit()


if __name__ == '__main__':
    main()