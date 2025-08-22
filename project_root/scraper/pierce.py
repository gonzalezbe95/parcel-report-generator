from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraper.base import CountyScraper
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os


class PierceScraper(CountyScraper):
    def __init__(self, parcel):
        super().__init__(parcel)  # base class stores self.parcel
        self.driver = self.init_driver()

    def init_driver(self):
        """Initialize Chrome WebDriver in headless mode."""

        # Prefer using chromedriver from PATH or environment variable
        chromedriver_path = os.getenv("CHROMEDRIVER_PATH", "chromedriver")

        chrome_options = Options()
        chrome_options.add_argument("--headless")  # headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        service = Service(chromedriver_path)
        return webdriver.Chrome(service=service, options=chrome_options)

    def get_td_value(self, label, timeout=10):
        """Helper to grab a <td> value based on its label."""
        try:
            elem = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"//td[normalize-space()='{label}']/following-sibling::td")
                )
            )
            return elem.text.strip()
        except:
            return None

    def scrape_summary(self):
        """Scrape parcel summary info from Pierce County site."""
        url = f"https://atip.piercecountywa.gov/app/v2/propertyDetail/{self.parcel}/summary"
        self.driver.get(url)
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//td[normalize-space()='Parcel Number']"))
        )

        summary_labels = ['Parcel Number', 'Site Address', 'Use Code', 'Taxpayer Name']
        fields = {
            'Use Code': 'Land Use Description',
            'Parcel Number': 'Parcel'
        }

        data = {}
        for label in summary_labels:
            value = self.get_td_value(label)
            data[fields.get(label, label)] = value

        # Scrape Legal Description
        try:
            legal_elem = self.driver.find_element(
                By.XPATH,
                "//div[contains(@class,'panel') and .//div[contains(@class,'panel-title') and contains(text(),'Tax Description')]]//div[contains(@class,'panel-body')]/div"
            )
            data["Legal Description"] = legal_elem.text.strip() if legal_elem else None
        except:
            data["Legal Description"] = None

        # Related Parcels
        try:
            links = self.driver.find_elements(
                By.XPATH,
                "//td[normalize-space()='Group Account Number']/following-sibling::td/a"
            )
            related_list = [f"Group Account Number {link.text.strip()}" for link in links if link.text.strip()]
            data["Related Parcels"] = related_list if related_list else None
        except:
            data["Related Parcels"] = None

        return data

    def scrape_exemptions(self):
        self.driver.get(f"https://atip.piercecountywa.gov/app/v2/propertyDetail/{self.parcel}/taxes")
        return self.get_td_value("Type")

    def scrape_acres(self):
        self.driver.get(f"https://atip.piercecountywa.gov/app/v2/propertyDetail/{self.parcel}/land")
        return self.get_td_value("Acres")

    def scrape(self):
        """Master scrape routine for Pierce County parcels."""
        try:
            data = {}
            data.update(self.scrape_summary())
            data["Exemptions"] = self.scrape_exemptions()
            data["Land Acres"] = self.scrape_acres()

            # Validate parcel exists
            self.checkParcel(data, "Pierce")

            return data
        except (TimeoutException, NoSuchElementException):
            raise ValueError(f"Parcel Number not found in Pierce County's Assessor Page!")
        finally:
            self.driver.quit()
