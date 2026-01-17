"""
Scraper Factory - Creates scrapers based on insurance company
"""
from enum import Enum
from pathlib import Path
from typing import Dict, List

from .phoenix_scraper import PhoenixScraper
from .base_scraper import BaseInsuranceScraper


class InsuranceCompany(Enum):
    PHOENIX = "phoenix"
    CLAL = "clal"
    MIGDAL = "migdal"
    HAREL = "harel"
    MENORA = "menora"
    AYALON = "ayalon"


COMPANY_DISPLAY_NAMES = {
    InsuranceCompany.PHOENIX: "הפניקס",
    InsuranceCompany.CLAL: "כלל",
    InsuranceCompany.MIGDAL: "מגדל",
    InsuranceCompany.HAREL: "הראל",
    InsuranceCompany.MENORA: "מנורה",
    InsuranceCompany.AYALON: "איילון",
}

SUPPORTED_COMPANIES = {
    InsuranceCompany.PHOENIX: True,   # Pilot
    InsuranceCompany.CLAL: False,     # Coming soon
    InsuranceCompany.MIGDAL: False,   # Coming soon
    InsuranceCompany.HAREL: False,    # Coming soon
    InsuranceCompany.MENORA: False,   # Coming soon
    InsuranceCompany.AYALON: False,   # Coming soon
}


class ScraperFactory:
    """
    Factory ליצירת Scraper לפי חברת ביטוח
    """

    _scrapers = {
        InsuranceCompany.PHOENIX: PhoenixScraper,
        # InsuranceCompany.CLAL: ClalScraper,
        # InsuranceCompany.MIGDAL: MigdalScraper,
    }

    @classmethod
    def create(cls, company: InsuranceCompany, user_id: str,
               data_dir: Path) -> BaseInsuranceScraper:
        """
        יצירת Scraper לפי חברת ביטוח

        Args:
            company: חברת הביטוח
            user_id: תעודת זהות
            data_dir: נתיב לתיקיית הנתונים

        Returns:
            Scraper מתאים
        """
        if company not in cls._scrapers:
            raise ValueError(f"Scraper for {company} not implemented yet")

        if not SUPPORTED_COMPANIES.get(company, False):
            raise ValueError(f"{COMPANY_DISPLAY_NAMES[company]} not supported yet")

        scraper_class = cls._scrapers[company]
        return scraper_class(user_id, data_dir)

    @classmethod
    def get_supported_companies(cls) -> List[Dict]:
        """רשימת חברות נתמכות"""
        return [
            {
                "code": company.value,
                "name": COMPANY_DISPLAY_NAMES[company],
                "supported": supported
            }
            for company, supported in SUPPORTED_COMPANIES.items()
        ]

    @classmethod
    def is_supported(cls, company_code: str) -> bool:
        """בדיקה אם חברה נתמכת"""
        try:
            company = InsuranceCompany(company_code)
            return SUPPORTED_COMPANIES.get(company, False)
        except ValueError:
            return False
