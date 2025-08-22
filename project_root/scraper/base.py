import requests

class CountyScraper:
    def __init__(self, parcel, session=None):
        self.parcel = parcel.strip()
        self.session = session or requests.Session()
        # polite default UA
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; ParcelScraper/1.0; +https://github.com/yourusername/yourrepo)"
        })

    def fetch(self, url, method="GET", **kwargs):
        resp = self.session.request(method, url, timeout=15, **kwargs)
        resp.raise_for_status()
        return resp.text

    def scrape(self):
        """Return dict or {'error': 'msg'}"""
        raise NotImplementedError

    def checkParcel(self, parsed_data, county_name):
        """
        Checks if the parcel exists in the scraped data.
        Raises a ValueError with a friendly message if not found.
        """
        # If parsed_data is empty or indicates "not found", raise error
        if all(v is None for v in parsed_data.values()):
            raise ValueError(f"Parcel Number not found in {county_name} County's Assessor Page!")


        # If parcel exists, do nothing (method returns None)
        return
