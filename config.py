"""
Configuration for Insurance Policy Scraper
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
USERS_DIR = DATA_DIR / "users"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
USERS_DIR.mkdir(exist_ok=True)

# Database
DATABASE_PATH = DATA_DIR / "insurance_bot.db"

# Security
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")

# Scraping settings
SCRAPE_TIMEOUT = 60  # seconds
DOWNLOAD_TIMEOUT = 120  # seconds

# Supported companies
SUPPORTED_COMPANIES = {
    "phoenix": {
        "name": "הפניקס",
        "base_url": "https://my.fnx.co.il",
        "login_url": "https://my.fnx.co.il",
        "supported": True
    },
    "clal": {
        "name": "כלל",
        "base_url": "https://www.clalbit.co.il",
        "supported": False
    },
    "migdal": {
        "name": "מגדל",
        "base_url": "https://www.migdal.co.il",
        "supported": False
    },
    "harel": {
        "name": "הראל",
        "base_url": "https://www.harel-group.co.il",
        "supported": False
    },
}
