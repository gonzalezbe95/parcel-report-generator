import requests
from bs4 import BeautifulSoup
from scraper.base import CountyScraper

class KingScraper(CountyScraper):
    def __init__(self, parcel_number):
        self.parcel_number = parcel_number
        super().__init__(parcel_number)

    def scrape(self):
        base_url = "https://blue.kingcounty.com/Assessor/eRealProperty/Detail.aspx?ParcelNbr="
        url = f"{base_url}{self.parcel}"  # self.parcel comes from base class

        # Map the field label in the page to the desired output field name
        field_names = {
            "Parcel": "Parcel",
            "Name": "Taxpayer Name",
            "Predominant Use": "Land Use Description",
            "Acres": "Land Acres",
            "Site Address": "Site Address"
        }

        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        data = {}

        # Extract each field's value and map to desired key name
        for field in field_names.keys():
            element = soup.find("td", string=field)
            if element and element.find_next("td"):
                data[field_names[field]] = element.find_next("td").get_text(strip=True)
            else:
                data[field_names[field]] = None

        # Extract Legal Description separately by its span ID
        legal_desc_span = soup.find("span", id="cphContent_FormViewLegalDescription_LabelLegalDescription")
        if legal_desc_span:
            data["Legal Description"] = legal_desc_span.get_text(strip=True)
        else:
            data["Legal Description"] = None

        # Check if parcel exist in assessor page
        self.checkParcel(data, "King")

        return data
