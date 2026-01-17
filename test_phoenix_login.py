#!/usr/bin/env python3
"""
Phoenix Login Test - בדיקת התחברות בלבד
סקריפט פשוט לבדיקה שההתחברות עובדת

Usage:
    python test_phoenix_login.py
"""
import asyncio
from pathlib import Path

# Configuration - הפרטים שלך
USER_ID = "303084305"
PHONE = "0544731650"

# Output directory
OUTPUT_DIR = Path(__file__).parent / "test_output"
OUTPUT_DIR.mkdir(exist_ok=True)


async def test_login():
    """Test Phoenix login flow"""

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Playwright לא מותקן!")
        print("הרץ: pip install playwright && playwright install chromium")
        return False

    print("="*60)
    print("🧪 בדיקת התחברות לאתר הפניקס")
    print("="*60)
    print(f"📋 ת.ז.: {USER_ID}")
    print(f"📱 טלפון: {PHONE}")
    print(f"📁 תיקייה: {OUTPUT_DIR}")
    print("="*60)

    async with async_playwright() as p:
        # Launch browser - NOT headless so you can see what happens
        print("\n🌐 פותח דפדפן...")
        browser = await p.chromium.launch(
            headless=False,  # תראה את הדפדפן
            slow_mo=1000     # האטה כדי לראות מה קורה
        )

        context = await browser.new_context(
            locale='he-IL',
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()

        try:
            # Step 1: Navigate to Phoenix
            print("\n📍 שלב 1: ניווט לאתר הפניקס...")
            await page.goto("https://my.fnx.co.il", wait_until='networkidle', timeout=30000)
            await page.screenshot(path=str(OUTPUT_DIR / "1_homepage.png"))
            print(f"   ✅ הגענו ל: {page.url}")
            print(f"   📸 צילום מסך: 1_homepage.png")

            # Step 2: Find and analyze the page
            print("\n📍 שלב 2: מנתח את הדף...")

            # Find all inputs
            inputs = await page.query_selector_all('input')
            print(f"   🔍 נמצאו {len(inputs)} שדות קלט:")
            for inp in inputs:
                inp_type = await inp.get_attribute('type') or 'text'
                inp_name = await inp.get_attribute('name') or ''
                inp_id = await inp.get_attribute('id') or ''
                inp_placeholder = await inp.get_attribute('placeholder') or ''
                is_visible = await inp.is_visible()
                if is_visible:
                    print(f"      • type='{inp_type}' name='{inp_name}' id='{inp_id}' placeholder='{inp_placeholder}'")

            # Find all buttons
            buttons = await page.query_selector_all('button')
            print(f"   🔍 נמצאו {len(buttons)} כפתורים:")
            for btn in buttons:
                text = (await btn.inner_text()).strip()[:40]
                is_visible = await btn.is_visible()
                if is_visible and text:
                    print(f"      • '{text}'")

            # Step 3: Try to find ID input
            print("\n📍 שלב 3: מחפש שדה תעודת זהות...")
            id_selectors = [
                'input[type="text"]',
                'input[type="tel"]',
                'input[name*="id"]',
                'input[name*="Id"]',
                'input[placeholder*="זהות"]',
                'input[placeholder*="תעודת"]',
                '#idNumber',
                '#userId',
                '#tz',
            ]

            id_input = None
            for selector in id_selectors:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    id_input = element
                    print(f"   ✅ נמצא שדה עם: {selector}")
                    break

            if not id_input:
                print("   ❌ לא נמצא שדה תעודת זהות!")
                print("   💡 שמור את הדף ובדוק ידנית")
                html = await page.content()
                with open(OUTPUT_DIR / "page_source.html", 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"   💾 HTML נשמר: page_source.html")

                input("\n⏎ לחץ Enter לסגירת הדפדפן...")
                return False

            # Step 4: Fill ID
            print("\n📍 שלב 4: מזין תעודת זהות...")
            await id_input.fill(USER_ID)
            await asyncio.sleep(1)
            await page.screenshot(path=str(OUTPUT_DIR / "2_id_filled.png"))
            print(f"   ✅ הוזן: {USER_ID}")
            print(f"   📸 צילום מסך: 2_id_filled.png")

            # Step 5: Find and click submit button
            print("\n📍 שלב 5: מחפש כפתור שליחה...")
            submit_selectors = [
                'button[type="submit"]',
                'button:has-text("שלח")',
                'button:has-text("המשך")',
                'button:has-text("כניסה")',
                'button:has-text("התחבר")',
                'input[type="submit"]',
            ]

            submit_btn = None
            for selector in submit_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        submit_btn = element
                        btn_text = await element.inner_text()
                        print(f"   ✅ נמצא כפתור: '{btn_text.strip()}'")
                        break
                except:
                    continue

            if submit_btn:
                print("   🖱️ לוחץ על הכפתור...")
                await submit_btn.click()
            else:
                print("   ⚠️ לא נמצא כפתור, מנסה Enter...")
                await id_input.press("Enter")

            # Wait for OTP page
            await asyncio.sleep(3)
            await page.screenshot(path=str(OUTPUT_DIR / "3_after_submit.png"))
            print(f"   📸 צילום מסך: 3_after_submit.png")
            print(f"   📍 URL נוכחי: {page.url}")

            # Step 6: Get OTP
            print("\n📍 שלב 6: ממתין לקוד OTP...")
            print("="*60)
            otp = input("📱 הזן את הקוד שקיבלת ב-SMS: ").strip()
            print("="*60)

            if not otp:
                print("   ❌ לא הוזן קוד")
                return False

            # Find OTP input
            print("\n📍 שלב 7: מזין קוד OTP...")
            otp_selectors = [
                'input[type="tel"]',
                'input[type="text"]',
                'input[name*="otp"]',
                'input[name*="code"]',
                'input[placeholder*="קוד"]',
            ]

            otp_input = None
            inputs = await page.query_selector_all('input')
            for inp in inputs:
                if await inp.is_visible():
                    otp_input = inp
                    break

            if otp_input:
                await otp_input.fill(otp)
                print(f"   ✅ הוזן קוד OTP")
                await page.screenshot(path=str(OUTPUT_DIR / "4_otp_filled.png"))
            else:
                print("   ❌ לא נמצא שדה OTP")
                return False

            # Step 8: Submit OTP
            print("\n📍 שלב 8: שולח קוד...")
            await otp_input.press("Enter")
            await asyncio.sleep(5)

            await page.screenshot(path=str(OUTPUT_DIR / "5_after_login.png"))
            print(f"   📸 צילום מסך: 5_after_login.png")
            print(f"   📍 URL נוכחי: {page.url}")

            # Check success
            if "login" not in page.url.lower():
                print("\n✅ נראה שההתחברות הצליחה!")

                # Save dashboard HTML
                html = await page.content()
                with open(OUTPUT_DIR / "dashboard.html", 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"   💾 HTML נשמר: dashboard.html")
            else:
                print("\n⚠️ נראה שעדיין בדף התחברות")

            # Keep browser open
            print("\n" + "="*60)
            print("🔍 הדפדפן פתוח - תוכל לבדוק ידנית")
            input("⏎ לחץ Enter לסגירת הדפדפן...")

            return True

        except Exception as e:
            print(f"\n❌ שגיאה: {e}")
            import traceback
            traceback.print_exc()
            await page.screenshot(path=str(OUTPUT_DIR / "error.png"))
            input("\n⏎ לחץ Enter לסגירת הדפדפן...")
            return False

        finally:
            await browser.close()


if __name__ == "__main__":
    print("\n🏥 Phoenix Insurance - Login Test\n")
    result = asyncio.run(test_login())
    print("\n" + "="*60)
    if result:
        print("✅ הבדיקה הסתיימה בהצלחה!")
    else:
        print("❌ הבדיקה נכשלה")
    print("="*60)
