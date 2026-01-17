"""
Phoenix Insurance Scraper - הפניקס
Handles login via OTP and downloads policies and attachments
"""
from pathlib import Path
from typing import Callable, List, Dict, Any, Optional
import asyncio
import json
import re
from datetime import datetime

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from .base_scraper import BaseInsuranceScraper


class PhoenixScraper(BaseInsuranceScraper):
    """
    Scraper לאתר הפניקס
    תומך בהתחברות באמצעות ת"ז + OTP
    """

    COMPANY_NAME = "הפניקס"
    COMPANY_CODE = "phoenix"
    BASE_URL = "https://my.fnx.co.il"

    # Selectors - יעודכנו בהתאם למבנה האתר האמיתי
    SELECTORS = {
        # Login page
        "id_input": 'input[type="text"], input[name*="id"], input[placeholder*="זהות"], #idNumber, #userId',
        "send_otp_button": 'button[type="submit"], button:has-text("שלח"), button:has-text("המשך"), .send-otp-btn',
        "otp_input": 'input[type="tel"], input[name*="otp"], input[name*="code"], input[placeholder*="קוד"], #otpCode',
        "login_button": 'button[type="submit"], button:has-text("כניסה"), button:has-text("התחבר"), .login-btn',

        # Main page / Dashboard
        "policies_menu": 'a:has-text("פוליסות"), a:has-text("הביטוחים שלי"), [data-menu="policies"]',
        "policy_cards": '.policy-card, .policy-item, .insurance-card, [data-policy], tr[data-id]',

        # Policy page
        "policy_number": '.policy-number, [data-policy-number], .מספר-פוליסה',
        "policy_type": '.policy-type, [data-policy-type], .סוג-ביטוח',
        "documents_tab": 'a:has-text("מסמכים"), button:has-text("מסמכים"), [data-tab="documents"]',
        "document_links": 'a[href*=".pdf"], a:has-text("הורד"), button:has-text("הורד"), .download-btn',

        # Specific document types
        "annual_report": 'a:has-text("דוח שנתי"), button:has-text("דוח שנתי")',
        "policy_copy": 'a:has-text("העתק פוליסה"), a:has-text("תעודת ביטוח"), button:has-text("העתק")',
        "appendix": 'a:has-text("נספח"), button:has-text("נספח")',
    }

    def __init__(self, user_id: str, data_dir: Path, phone: str = ""):
        super().__init__(user_id, data_dir)
        self.phone = phone
        self.playwright = None

    async def _init_browser(self, headless: bool = True):
        """Initialize Playwright browser"""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright is not installed. Run: pip install playwright && playwright install chromium")

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=['--lang=he-IL']
        )
        self.context = await self.browser.new_context(
            locale='he-IL',
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.page = await self.context.new_page()

        # Set download behavior
        await self.page.set_extra_http_headers({
            'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7'
        })

    async def login(self, otp_callback: Callable[[], str]) -> bool:
        """
        התחברות לאתר הפניקס

        Args:
            otp_callback: פונקציה שמחזירה את קוד ה-OTP

        Returns:
            True אם ההתחברות הצליחה
        """
        try:
            await self._init_browser(headless=False)  # Non-headless for debugging

            print(f"🌐 מנווט ל-{self.BASE_URL}...")
            await self.page.goto(self.BASE_URL, wait_until='networkidle', timeout=30000)

            # Wait for page to load
            await asyncio.sleep(2)

            # Take screenshot for debugging
            await self.page.screenshot(path=str(self.data_dir / "01_login_page.png"))
            print("📸 צילום מסך נשמר: 01_login_page.png")

            # Find and fill ID input
            print(f"🔍 מחפש שדה תעודת זהות...")
            id_input = await self._find_element(self.SELECTORS["id_input"])

            if id_input:
                await id_input.fill(self.user_id)
                print(f"✅ הוזנה תעודת זהות: {self.user_id[:3]}***")
            else:
                print("❌ לא נמצא שדה תעודת זהות")
                await self._save_page_html("login_page")
                return False

            # Click send OTP button
            print("🔍 מחפש כפתור שליחת קוד...")
            send_btn = await self._find_element(self.SELECTORS["send_otp_button"])

            if send_btn:
                await send_btn.click()
                print("✅ נשלחה בקשה לקוד OTP")
            else:
                print("⚠️ לא נמצא כפתור שליחה, מנסה Enter...")
                await id_input.press("Enter")

            # Wait for OTP page
            await asyncio.sleep(3)
            await self.page.screenshot(path=str(self.data_dir / "02_otp_page.png"))
            print("📸 צילום מסך נשמר: 02_otp_page.png")

            # Get OTP from user
            print("\n📱 קוד OTP נשלח לטלפון שלך!")
            otp_code = otp_callback()

            if not otp_code:
                print("❌ לא התקבל קוד OTP")
                return False

            # Find and fill OTP input
            print("🔍 מחפש שדה קוד אימות...")
            otp_input = await self._find_element(self.SELECTORS["otp_input"])

            if otp_input:
                await otp_input.fill(otp_code)
                print(f"✅ הוזן קוד OTP")
            else:
                print("❌ לא נמצא שדה קוד אימות")
                await self._save_page_html("otp_page")
                return False

            # Click login button
            print("🔍 מחפש כפתור כניסה...")
            login_btn = await self._find_element(self.SELECTORS["login_button"])

            if login_btn:
                await login_btn.click()
                print("✅ לחיצה על כפתור כניסה")
            else:
                print("⚠️ לא נמצא כפתור כניסה, מנסה Enter...")
                await otp_input.press("Enter")

            # Wait for dashboard
            await asyncio.sleep(5)
            await self.page.screenshot(path=str(self.data_dir / "03_dashboard.png"))
            print("📸 צילום מסך נשמר: 03_dashboard.png")

            # Check if login succeeded
            current_url = self.page.url
            print(f"🔗 URL נוכחי: {current_url}")

            if "login" in current_url.lower() or "error" in current_url.lower():
                print("❌ נראה שההתחברות נכשלה")
                await self._save_page_html("login_failed")
                return False

            print("✅ ההתחברות הצליחה!")
            return True

        except Exception as e:
            print(f"❌ שגיאה בהתחברות: {e}")
            if self.page:
                await self.page.screenshot(path=str(self.data_dir / "error_screenshot.png"))
                await self._save_page_html("error_page")
            return False

    async def get_policies(self) -> List[Dict[str, Any]]:
        """קבלת רשימת פוליסות"""
        policies = []

        try:
            print("\n📋 מחפש פוליסות...")

            # Try to navigate to policies section
            policies_menu = await self._find_element(self.SELECTORS["policies_menu"])
            if policies_menu:
                await policies_menu.click()
                await asyncio.sleep(3)

            await self.page.screenshot(path=str(self.data_dir / "04_policies_page.png"))
            print("📸 צילום מסך נשמר: 04_policies_page.png")

            # Save page HTML for analysis
            await self._save_page_html("policies_page")

            # Find policy cards
            policy_elements = await self.page.query_selector_all(self.SELECTORS["policy_cards"])

            if not policy_elements:
                print("⚠️ לא נמצאו כרטיסי פוליסות, מחפש בטבלה...")
                policy_elements = await self.page.query_selector_all('tr[data-id], .policy-row, tbody tr')

            print(f"🔍 נמצאו {len(policy_elements)} פוליסות פוטנציאליות")

            for i, element in enumerate(policy_elements):
                try:
                    policy_text = await element.inner_text()
                    policy_html = await element.inner_html()

                    # Extract policy number
                    policy_number = self._extract_policy_number(policy_text)

                    # Extract policy type
                    policy_type = self._extract_policy_type(policy_text)

                    # Get link if exists
                    link = await element.query_selector('a')
                    href = await link.get_attribute('href') if link else None

                    policy = {
                        "index": i,
                        "number": policy_number or f"policy_{i+1}",
                        "type": policy_type,
                        "text": policy_text[:200],
                        "url": href,
                        "element_id": await element.get_attribute('id') or await element.get_attribute('data-id')
                    }

                    policies.append(policy)
                    print(f"  📄 פוליסה {i+1}: {policy['number']} ({policy['type']})")

                except Exception as e:
                    print(f"  ⚠️ שגיאה בפוליסה {i+1}: {e}")

            if not policies:
                print("⚠️ לא נמצאו פוליסות. בודק את מבנה הדף...")
                # Save full page content for debugging
                content = await self.page.content()
                with open(self.data_dir / "full_page.html", 'w', encoding='utf-8') as f:
                    f.write(content)

        except Exception as e:
            print(f"❌ שגיאה בקבלת פוליסות: {e}")

        return policies

    async def download_policy_documents(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """הורדת מסמכי פוליסה"""
        result = {
            "number": policy["number"],
            "type": policy["type"],
            "documents": []
        }

        policy_dir = self.data_dir / f"policy_{policy['number']}"
        policy_dir.mkdir(exist_ok=True)

        try:
            print(f"\n📥 מוריד מסמכים לפוליסה {policy['number']}...")

            # Navigate to policy page if URL exists
            if policy.get("url"):
                await self.page.goto(policy["url"], wait_until='networkidle')
                await asyncio.sleep(2)

            # Try to click on documents tab
            docs_tab = await self._find_element(self.SELECTORS["documents_tab"])
            if docs_tab:
                await docs_tab.click()
                await asyncio.sleep(2)

            # Take screenshot
            await self.page.screenshot(path=str(policy_dir / "policy_page.png"))

            # Find all downloadable documents
            doc_links = await self.page.query_selector_all(self.SELECTORS["document_links"])
            print(f"  🔍 נמצאו {len(doc_links)} מסמכים להורדה")

            for i, link in enumerate(doc_links):
                try:
                    link_text = await link.inner_text()
                    doc_type = self._classify_document(link_text)

                    print(f"    📄 מוריד: {link_text[:50]}...")

                    # Download the file
                    async with self.page.expect_download(timeout=60000) as download_info:
                        await link.click()

                    download = await download_info.value
                    filename = download.suggested_filename or f"document_{i+1}.pdf"
                    filepath = policy_dir / filename

                    await download.save_as(str(filepath))

                    result["documents"].append({
                        "type": doc_type,
                        "filename": filename,
                        "path": str(filepath),
                        "original_text": link_text[:100]
                    })

                    print(f"    ✅ נשמר: {filename}")

                except Exception as e:
                    print(f"    ⚠️ שגיאה בהורדה: {e}")

        except Exception as e:
            print(f"❌ שגיאה בהורדת מסמכים: {e}")

        # Save policy metadata
        with open(policy_dir / "info.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return result

    async def _find_element(self, selectors: str):
        """
        מחפש אלמנט לפי רשימת סלקטורים

        Args:
            selectors: סלקטורים מופרדים בפסיקים

        Returns:
            אלמנט או None
        """
        for selector in selectors.split(", "):
            selector = selector.strip()
            try:
                element = await self.page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    if is_visible:
                        return element
            except:
                continue
        return None

    async def _save_page_html(self, name: str):
        """שמירת HTML של הדף לניתוח"""
        try:
            content = await self.page.content()
            filepath = self.data_dir / f"{name}.html"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"💾 HTML נשמר: {filepath}")
        except Exception as e:
            print(f"⚠️ שגיאה בשמירת HTML: {e}")

    def _extract_policy_number(self, text: str) -> Optional[str]:
        """חילוץ מספר פוליסה מטקסט"""
        # Look for 7-12 digit numbers
        matches = re.findall(r'\b\d{7,12}\b', text)
        return matches[0] if matches else None

    def _extract_policy_type(self, text: str) -> str:
        """חילוץ סוג פוליסה"""
        text_lower = text.lower()
        if any(word in text for word in ["בריאות", "רפואי", "רפואה"]):
            return "health"
        elif any(word in text for word in ["חיים", "ריסק"]):
            return "life"
        elif any(word in text for word in ["רכב", "מכונית", "אוטו"]):
            return "car"
        elif any(word in text for word in ["דירה", "בית", "מבנה", "תכולה"]):
            return "home"
        elif any(word in text for word in ["פנסיה", "גמל", "השתלמות"]):
            return "pension"
        return "other"

    def _classify_document(self, text: str) -> str:
        """סיווג סוג מסמך"""
        if any(word in text for word in ["דוח שנתי", "דו\"ח שנתי"]):
            return "annual_report"
        elif any(word in text for word in ["העתק", "תעודה", "פוליסה"]):
            return "policy_copy"
        elif "נספח" in text:
            return "appendix"
        elif any(word in text for word in ["אישור", "certificate"]):
            return "certificate"
        return "document"

    async def close(self):
        """סגירת הדפדפן"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


# Convenience function for testing
async def scrape_phoenix(user_id: str, data_dir: Path, otp_callback: Callable[[], str]):
    """
    פונקציה נוחה לסקרייפינג של הפניקס

    Args:
        user_id: תעודת זהות
        data_dir: תיקיית נתונים
        otp_callback: פונקציה לקבלת OTP

    Returns:
        תוצאות הסקרייפינג
    """
    scraper = PhoenixScraper(user_id, data_dir)
    return await scraper.scrape_all(otp_callback, progress_callback=print)
