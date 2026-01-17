# 🏥 Phoenix Insurance Scraper

סקריפט להורדת פוליסות וביטוחים מהאזור האישי של הפניקס.

## 📋 דרישות

- Python 3.10+
- Playwright + Chromium

## 🚀 התקנה

```bash
# Clone or download the project
cd Insurance

# Run setup script
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install playwright requests beautifulsoup4 aiohttp
playwright install chromium
```

## 📱 שימוש

```bash
# Activate virtual environment
source venv/bin/activate

# Run the scraper
python scrape_phoenix.py
```

הסקריפט:
1. יפתח דפדפן ויגש לאתר הפניקס
2. יזין את תעודת הזהות שלך
3. ישלח קוד OTP לטלפון
4. יבקש ממך להזין את הקוד
5. יוריד את כל הפוליסות והנספחים

## 📁 מבנה הנתונים

```
data/
└── users/
    └── {תעודת_זהות}/
        └── phoenix/
            ├── metadata.json
            ├── 01_login_page.png
            ├── 02_otp_page.png
            ├── 03_dashboard.png
            └── policy_{מספר}/
                ├── info.json
                └── *.pdf
```

## ⚙️ הגדרות

ערוך את הקובץ `scrape_phoenix.py` ושנה:

```python
USER_ID = "123456789"  # תעודת זהות שלך
PHONE = "054XXXXXXX"    # טלפון שלך
```

## 🔧 פתרון בעיות

### הדפדפן לא נפתח
```bash
playwright install chromium
playwright install-deps chromium
```

### שגיאות SSL
נסה להריץ עם headless=False בקובץ `phoenix_scraper.py`

### האתר נחסם
ייתכן שהאתר חוסם אוטומציה. נסה:
- לא להריץ יותר מדי פעמים ברצף
- להשתמש בהפסקות ארוכות יותר

## 📞 תמיכה

בבעיות עם האתר עצמו: 3455*
