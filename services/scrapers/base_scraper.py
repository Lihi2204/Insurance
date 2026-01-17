"""
Base Scraper - Abstract base class for all insurance company scrapers
"""
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, List, Dict, Any
import json
import asyncio


class BaseInsuranceScraper(ABC):
    """
    מחלקת בסיס לכל ה-Scrapers
    כל חברת ביטוח תירש ממחלקה זו
    """

    COMPANY_NAME: str = ""
    COMPANY_CODE: str = ""
    BASE_URL: str = ""

    def __init__(self, user_id: str, data_dir: Path):
        """
        Initialize the scraper

        Args:
            user_id: תעודת זהות
            data_dir: נתיב לתיקיית הנתונים של המשתמש
        """
        self.user_id = user_id
        self.data_dir = data_dir / self.COMPANY_CODE
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.page = None
        self.browser = None
        self.context = None

    @abstractmethod
    async def login(self, otp_callback: Callable[[], str]) -> bool:
        """
        התחברות לאתר

        Args:
            otp_callback: פונקציה שמחזירה את קוד ה-OTP מהמשתמש

        Returns:
            True אם ההתחברות הצליחה
        """
        pass

    @abstractmethod
    async def get_policies(self) -> List[Dict[str, Any]]:
        """
        קבלת רשימת פוליסות

        Returns:
            רשימת פוליסות
        """
        pass

    @abstractmethod
    async def download_policy_documents(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """
        הורדת מסמכי פוליסה

        Args:
            policy: מידע על הפוליסה

        Returns:
            מידע על המסמכים שהורדו
        """
        pass

    async def scrape_all(self,
                         otp_callback: Callable[[], str],
                         progress_callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
        """
        תהליך סקרייפינג מלא

        Args:
            otp_callback: פונקציה לקבלת קוד OTP
            progress_callback: פונקציה לעדכון התקדמות
        """
        try:
            # 1. התחברות
            if progress_callback:
                progress_callback(f"🔐 מתחבר ל{self.COMPANY_NAME}...")

            success = await self.login(otp_callback)
            if not success:
                raise Exception("Login failed")

            # 2. קבלת פוליסות
            if progress_callback:
                progress_callback("📋 מחפש פוליסות...")

            policies = await self.get_policies()

            if progress_callback:
                progress_callback(f"📋 נמצאו {len(policies)} פוליסות")

            # 3. הורדת מסמכים לכל פוליסה
            results = {
                "company": self.COMPANY_CODE,
                "company_name": self.COMPANY_NAME,
                "scrape_date": datetime.now().isoformat(),
                "user_id": self.user_id,
                "policies": []
            }

            for i, policy in enumerate(policies):
                if progress_callback:
                    progress_callback(f"📥 מוריד פוליסה {i+1}/{len(policies)}: {policy.get('number', 'unknown')}")

                policy_data = await self.download_policy_documents(policy)
                results["policies"].append(policy_data)

            # 4. שמירת metadata
            self._save_metadata(results)

            if progress_callback:
                progress_callback(f"✅ הסתיים! הורדו {len(policies)} פוליסות")

            return results

        finally:
            await self.close()

    async def close(self):
        """סגירת הדפדפן"""
        if self.browser:
            await self.browser.close()

    def _save_metadata(self, data: Dict[str, Any]):
        """שמירת מטא-דאטה"""
        metadata_file = self.data_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # שמירת תאריך עדכון
        last_scrape_file = self.data_dir / "last_scrape.txt"
        last_scrape_file.write_text(datetime.now().isoformat())

    def _save_document(self, content: bytes, filename: str, subdir: str = "") -> Path:
        """
        שמירת מסמך

        Args:
            content: תוכן הקובץ
            filename: שם הקובץ
            subdir: תת-תיקייה

        Returns:
            נתיב לקובץ שנשמר
        """
        if subdir:
            target_dir = self.data_dir / subdir
        else:
            target_dir = self.data_dir

        target_dir.mkdir(parents=True, exist_ok=True)
        filepath = target_dir / filename

        with open(filepath, 'wb') as f:
            f.write(content)

        return filepath
