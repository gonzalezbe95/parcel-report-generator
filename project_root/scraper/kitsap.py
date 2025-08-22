import requests
from bs4 import BeautifulSoup
from scraper.base import CountyScraper

class KitsapScraper(CountyScraper):
    def __init__(self, parcel_number):
        super().__init__(parcel_number)
        self.urls = {
            "general": f"https://psearch.kitsap.gov/pdetails/Details?parcel={parcel_number}&page=general",
            "legal": f"https://psearch.kitsap.gov/pdetails/Details?parcel={parcel_number}&page=taxdescription",
            "land": f"https://psearch.kitsap.gov/pdetails/Details?parcel={parcel_number}&page=landlocation"
        }

    def _fetch_soup(self, url):
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            return BeautifulSoup(resp.content, "html.parser")
        except requests.RequestException as e:
            print(f"[KitsapScraper] Fetch error for {url}: {e}")
            return None

    def _extract_from_table(self, soup, label):
        """Finds text in a cell based on label in a <strong> element."""
        if soup:
            strong = soup.find("strong", string=label)
            if strong:
                td = strong.find_parent("td").find_next_sibling("td")
                if td:
                    return td.get_text(strip=True)
        return None

    def scrape(self):
        # Map the field label in the page to the desired output field name
        field_names = {
            "Name": "Taxpayer Name",
            "Property Class": "Land Use Description",
            "Acres": "Land Acres",
        }

        data = {}

        # General Info
        general_soup = self._fetch_soup(self.urls["general"])
        fields_general = ["Taxpayer Name", "Parcel", "Site Address", "Property Class"]
        for label in fields_general:
            data[label] = self._extract_from_table(general_soup, label)

        # Legal Description
        legal_soup = self._fetch_soup(self.urls["legal"])
        data["Legal Description"] = None
        if legal_soup:
            divs = legal_soup.select("div.col-xs-12.col-sm-6.col-md-6.col-lg-8")
            for div in divs:
                blk = div.find("blockquote")
                if blk:
                    data["Legal Description"] = blk.get_text(strip=True)
                    break

        # Land Info
        land_soup = self._fetch_soup(self.urls["land"])
        fields_land = ["Acres", "Land Use Description"]
        for label in fields_land:
            data[label] = self._extract_from_table(land_soup, label)

        # Check if parcel exists in assessor page
        self.checkParcel(data, "Kitsap")

        return data
