#!/usr/bin/env python3
"""
Phoenix Website Explorer
סקריפט אינטראקטיבי לחקירת אתר הפניקס ומציאת הסלקטורים הנכונים

Usage:
    python explore_phoenix.py
"""
import asyncio
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Playwright not installed!")
    print("Run: pip install playwright && playwright install chromium")
    exit(1)


# Configuration
USER_ID = "303084305"
DATA_DIR = Path(__file__).parent / "data" / "exploration"
DATA_DIR.mkdir(parents=True, exist_ok=True)


async def explore():
    """Interactive exploration of Phoenix website"""
    print("🔍 Phoenix Website Explorer")
    print("="*50)

    async with async_playwright() as p:
        # Launch browser (non-headless for visual exploration)
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=500  # Slow down for visibility
        )

        context = await browser.new_context(
            locale='he-IL',
            viewport={'width': 1280, 'height': 720}
        )

        page = await context.new_page()

        try:
            # Navigate to Phoenix
            print("\n🌐 Opening https://my.fnx.co.il ...")
            await page.goto("https://my.fnx.co.il", wait_until='networkidle')

            # Take screenshot
            await page.screenshot(path=str(DATA_DIR / "01_initial.png"))
            print(f"📸 Screenshot saved: {DATA_DIR / '01_initial.png'}")

            # Save HTML
            html = await page.content()
            with open(DATA_DIR / "01_initial.html", 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"💾 HTML saved: {DATA_DIR / '01_initial.html'}")

            # Print page info
            print(f"\n📍 Current URL: {page.url}")
            print(f"📋 Title: {await page.title()}")

            # Find input fields
            print("\n🔍 Looking for input fields...")
            inputs = await page.query_selector_all('input')
            print(f"Found {len(inputs)} input fields:")
            for inp in inputs:
                inp_type = await inp.get_attribute('type') or 'text'
                inp_name = await inp.get_attribute('name') or ''
                inp_id = await inp.get_attribute('id') or ''
                inp_placeholder = await inp.get_attribute('placeholder') or ''
                print(f"  - type={inp_type}, name={inp_name}, id={inp_id}, placeholder={inp_placeholder}")

            # Find buttons
            print("\n🔍 Looking for buttons...")
            buttons = await page.query_selector_all('button')
            print(f"Found {len(buttons)} buttons:")
            for btn in buttons:
                btn_text = await btn.inner_text()
                btn_type = await btn.get_attribute('type') or ''
                print(f"  - '{btn_text.strip()[:30]}' (type={btn_type})")

            # Interactive mode
            print("\n" + "="*50)
            print("📝 INTERACTIVE MODE")
            print("="*50)
            print("The browser is now open. You can:")
            print("  1. Manually interact with the page")
            print("  2. Inspect elements with DevTools (F12)")
            print("  3. Note the selectors you find")
            print("\nWhen ready, enter ID number and I'll try to login...")

            # Enter ID
            input(f"\n⏎ Press Enter to fill ID ({USER_ID})...")

            # Try to find and fill ID input
            id_selectors = [
                'input[type="text"]',
                'input[name*="id"]',
                'input[placeholder*="זהות"]',
                '#idNumber',
                '#userId',
                'input[name="userId"]'
            ]

            for selector in id_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        await element.fill(USER_ID)
                        print(f"✅ Filled ID using selector: {selector}")
                        break
                except:
                    continue

            await page.screenshot(path=str(DATA_DIR / "02_id_filled.png"))

            # Wait for user to click send
            input("\n⏎ Now click the 'Send OTP' button manually, then press Enter...")

            await page.screenshot(path=str(DATA_DIR / "03_otp_requested.png"))

            # Save OTP page HTML
            html = await page.content()
            with open(DATA_DIR / "03_otp_page.html", 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"💾 OTP page HTML saved")

            # Find OTP input
            print("\n🔍 Looking for OTP input field...")
            inputs = await page.query_selector_all('input')
            for inp in inputs:
                inp_type = await inp.get_attribute('type') or 'text'
                inp_name = await inp.get_attribute('name') or ''
                inp_id = await inp.get_attribute('id') or ''
                if inp_type in ['text', 'tel', 'number'] or 'otp' in inp_name.lower() or 'code' in inp_name.lower():
                    print(f"  📱 Possible OTP input: type={inp_type}, name={inp_name}, id={inp_id}")

            # Get OTP from user
            otp = input("\n🔑 Enter OTP code: ").strip()

            if otp:
                # Try to find and fill OTP
                otp_selectors = [
                    'input[type="tel"]',
                    'input[name*="otp"]',
                    'input[name*="code"]',
                    'input[placeholder*="קוד"]',
                    '#otpCode'
                ]

                for selector in otp_selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element and await element.is_visible():
                            await element.fill(otp)
                            print(f"✅ Filled OTP using selector: {selector}")
                            break
                    except:
                        continue

                await page.screenshot(path=str(DATA_DIR / "04_otp_filled.png"))

                # Wait for user to click login
                input("\n⏎ Now click the 'Login' button manually, then press Enter...")

                # Wait for navigation
                await asyncio.sleep(3)

                await page.screenshot(path=str(DATA_DIR / "05_after_login.png"))
                print(f"\n📍 Current URL: {page.url}")

                # Save dashboard HTML
                html = await page.content()
                with open(DATA_DIR / "05_dashboard.html", 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"💾 Dashboard HTML saved")

                # Explore dashboard
                print("\n🔍 Exploring dashboard...")
                links = await page.query_selector_all('a')
                print(f"Found {len(links)} links:")
                for link in links[:20]:  # First 20
                    text = await link.inner_text()
                    href = await link.get_attribute('href') or ''
                    if text.strip():
                        print(f"  - '{text.strip()[:30]}' -> {href[:50]}")

            # Keep browser open for manual exploration
            print("\n" + "="*50)
            print("🔍 Browser is still open for exploration")
            print("Press Enter to close...")
            input()

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()

    print("\n✅ Exploration complete!")
    print(f"📁 All files saved to: {DATA_DIR}")


if __name__ == "__main__":
    asyncio.run(explore())
