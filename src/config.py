import os
import configparser

CONFIG_FILE = 'config.ini'
BROWSER_DATA_DIR = os.path.join(os.getcwd(), "browser-data")

park_name_to_id = {
    "Disney's Animal Kingdom": "WDW_AK_DAILY",
    "EPCOT": "WDW_EP_DAILY",
    "Magic Kingdom": "WDW_MK_DAILY",
    "Disney's Hollywood Studios": "WDW_HS_DAILY"
}


def create_default_config():
    if not os.path.exists(BROWSER_DATA_DIR):
        os.makedirs(BROWSER_DATA_DIR)
        print(f"[+] Created browser data directory at {BROWSER_DATA_DIR}")

    park_options = '\n'.join(f'# {name}' for name in park_name_to_id)
    config_text = f"""# Available Parks:
{park_options}

[reservation]
guest_list = John Doe, Jane Doe
date = 2025-04-25
park = EPCOT
email = example@gmail.com
password = disney_account_password
"""
    with open(CONFIG_FILE, 'w') as f:
        f.write(config_text)
    print(f'[+] Created default {CONFIG_FILE}. Please edit it and re-run the script.')


def load_config():
    if not os.path.exists(CONFIG_FILE):
        create_default_config()
        raise SystemExit("[!] Please edit config.ini and re-run this script.")

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    section = config['reservation']
    return {
        'guest_list': [name.strip() for name in section.get('guest_list', '').split(',')],
        'date': section.get('date'),
        'park': section.get('park'),
        'email': section.get('email'),
        'password': section.get('password')
    }
