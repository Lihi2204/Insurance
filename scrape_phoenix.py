#!/usr/bin/env python3
"""
Phoenix Insurance Scraper - Test Script
הורדת פוליסות מהפניקס

Usage:
    python scrape_phoenix.py

Requirements:
    pip install playwright
    playwright install chromium
"""
import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from services.scrapers.phoenix_scraper import PhoenixScraper


# ============== CONFIGURATION ==============
# הגדרות - שנה לפי הפרטים שלך

USER_ID = "303084305"  # תעודת זהות
PHONE = "0544731650"    # טלפון

# תיקיית נתונים
DATA_DIR = Path(__file__).parent / "data" / "users" / USER_ID

# ============================================


def get_otp_from_user() -> str:
    """מבקש קוד OTP מהמשתמש"""
    print("\n" + "="*50)
    print("📱 קוד OTP נשלח לטלפון שלך!")
    print("="*50)
    otp = input("\n🔑 הזן את הקוד שקיבלת: ").strip()
    return otp


def progress_callback(message: str):
    """הדפסת התקדמות"""
    print(f"\n{message}")


async def main():
    """Main function"""
    print("="*60)
    print("🏥 הפניקס - הורדת פוליסות וביטוחים")
    print("="*60)
    print(f"\n📋 תעודת זהות: {USER_ID}")
    print(f"📱 טלפון: {PHONE}")
    print(f"📁 תיקיית נתונים: {DATA_DIR}")

    # Create data directory
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Create scraper
    scraper = PhoenixScraper(USER_ID, DATA_DIR.parent, PHONE)

    try:
        # Run scraping
        print("\n🚀 מתחיל תהליך סקרייפינג...")

        results = await scraper.scrape_all(
            otp_callback=get_otp_from_user,
            progress_callback=progress_callback
        )

        # Print results
        print("\n" + "="*60)
        print("📊 תוצאות:")
        print("="*60)

        if results:
            print(f"✅ חברה: {results.get('company_name', 'N/A')}")
            print(f"📅 תאריך: {results.get('scrape_date', 'N/A')}")
            print(f"📄 פוליסות: {len(results.get('policies', []))}")

            for policy in results.get('policies', []):
                print(f"\n  📋 פוליסה: {policy.get('number', 'N/A')}")
                print(f"     סוג: {policy.get('type', 'N/A')}")
                print(f"     מסמכים: {len(policy.get('documents', []))}")

                for doc in policy.get('documents', []):
                    print(f"       - {doc.get('filename', 'N/A')} ({doc.get('type', 'N/A')})")

            print(f"\n💾 הנתונים נשמרו ב: {DATA_DIR}")

        else:
            print("❌ לא התקבלו תוצאות")

    except Exception as e:
        print(f"\n❌ שגיאה: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await scraper.close()

    print("\n" + "="*60)
    print("✅ הסתיים!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
