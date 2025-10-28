# Disney Bot

Automates checking and booking Disney parks reservations using Selenium.

---

## 📦 Requirements

- Python 3.10+
- Google Chrome
- ChromeDriver (installed automatically via `webdriver-manager`)

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

All runtime settings are stored in config.ini.

Before running the bot, update your Disney account credentials, guest list, date, and park.

Example:

```ini
# Available Parks:
# Disney's Animal Kingdom
# EPCOT
# Magic Kingdom
# Disney's Hollywood Studios

[reservation]
guest_list = John Doe, Jane Doe
date = 2025-04-25
park = EPCOT
email = example@gmail.com
password = disney_account_password
```

## 🚀 Usage

Run the bot from the root project directory:

```py
py src/main.py
```

- If you already have an active session, the bot will automatically skip login.
- You may be prompted for 2FA (email OTP) during login.

## Disclaimer

This project is strictly for educational purposes. Use responsibly and at your own risk.
