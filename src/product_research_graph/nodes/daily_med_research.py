import logging
import requests
from urllib.parse import urljoin, urlparse, parse_qs, quote
from bs4 import BeautifulSoup
from typing import List
from pydantic import BaseModel, Field

from langchain_core.runnables import RunnableConfig

# Example import from your own code
from src.product_research_graph.state import DailyMedResearchGraphState
from src.state import PotentialRLD  # typed data model

class DailyMedResearch(BaseModel):
    """
    DailyMed Research Node that returns only 'potentialRLDs' with:
    - title
    - image_url
    - setid
    """
    def __init__(self):
        pass

    def build_advanced_search_url(self, search_name: str, dosage_form: str) -> str:
        """
        Builds the advanced search URL for DailyMed by injecting
        {search_name} and {dosage_form} into the query. We also use
        urllib.parse.quote to properly URL-encode parentheses, spaces, etc.

        Base pattern:
          https://dailymed.nlm.nih.gov/dailymed/search.cfm?adv=1&labeltype=all&pagesize=200&page=1&query=
          NAME%3A%28{search_name}%29+AND+43678-2%3A%28{dosage_form}%29*
        """
        search_name_encoded = quote(search_name)
        dosage_form_encoded = quote(dosage_form)

        base_url = (
            "https://dailymed.nlm.nih.gov/dailymed/"
            "search.cfm?adv=1&labeltype=all&pagesize=200&page=1&query="
        )

        # Example: "NAME%3A%28aspirin%29+AND+43678-2%3A%28tablet%29+"
        query_str = f"NAME%3A%28{search_name_encoded}%29+AND+43678-2%3A%28{dosage_form_encoded}%29*"
        return base_url + query_str

    def parse_search_results(self, html: str, api_name: str, brand_name, manufacturer) -> List[PotentialRLD]:
        """
        Given the HTML of the advanced search results page,
        returns a list of PotentialRLD objects, each containing:
          title, image_url, setid
        """
        soup = BeautifulSoup(html, "html.parser")
        # Collect all <article> tags representing search results
        # Then slice to keep only the first 10
        articles = soup.find_all("article", {"class": ["row", "odd", "even"]})[:10]

        potential_rlds: List[PotentialRLD] = []

        for art in articles:
            # 1) Extract the link with class="drug-info-link"
            link = art.select_one("a.drug-info-link")
            if not link:
                continue

            full_title = link.get_text(strip=True)

            # href might look like: "/dailymed/drugInfo.cfm?setid=0cb2ee04-8581-46c8-a781-7be170ab5c86"
            href = link.get("href", "")
            setid_value = ""
            if "setid=" in href:
                parsed = urlparse(href)
                qs = parse_qs(parsed.query)
                setid_value = qs.get("setid", [""])[0]

            # 2) Find the first product image in this <article>
            img_tag = art.select_one("img.package-photo")
            if img_tag:
                src = img_tag.get("src", "")
                image_url = urljoin("https://dailymed.nlm.nih.gov", src)
            else:
                image_url = ""

            # Create the typed PotentialRLD object
            potential_rld = PotentialRLD(
                api_name = api_name,
                brand_name = brand_name,
                manufacturer = manufacturer,
                title=full_title,
                image_url=image_url,
                setid=setid_value
            )
            potential_rlds.append(potential_rld)

        return potential_rlds

    def run(self, state: DailyMedResearchGraphState, config: RunnableConfig):
        """
        1) Retrieves brand_name and rld_dosage_form from RLD in the state.
        2) If brand_name is empty, fallback to the first API name.
        3) Builds the advanced search URL (with URL-encoding), requests the HTML, parses results.
        4) Returns 'potentialRLDs' as a list[PotentialRLD].
        """
        try:      
            rld_obj = state["RLD"]      
            brand_name = (rld_obj.brand_name or "").strip()
            manufacturer = (rld_obj.manufacturer or "").strip()
            dosage_form = (rld_obj.rld_dosage_form or "").strip()

            # Fallback to API name if brand_name is missing
            if not brand_name:
                if "+" in rld_obj.api_name:
                    # If combination, use the first API
                    brand_name = rld_obj.api_name.split("+")[0].strip()
                else:
                    brand_name = rld_obj.api_name.strip()

            if not brand_name or not dosage_form:
                logging.warning("No brand_name or dosage_form found. Returning empty list.")
                return {"potential_RLDs": PotentialRLD(api_name=rld_obj.api_name, brand_name = rld_obj.api_name, manufacturer = "", title="", image_url="", setid="")}

            # 1) Build the advanced search URL with quote
            adv_search_url = self.build_advanced_search_url(brand_name, dosage_form)
            logging.info(f"DailyMed advanced search URL: {adv_search_url}")

            # 2) Fetch the page
            try:
                resp = requests.get(adv_search_url, timeout=15)
                resp.raise_for_status()
            except Exception as e:
                logging.error(f"Failed to retrieve DailyMed page: {e}")
                return {"potential_RLDs": PotentialRLD(api_name=rld_obj.api_name, brand_name = rld_obj.api_name, manufacturer = "", title="", image_url="", setid="")}

            # 3) Parse the search results into typed PotentialRLD objects
            potential_rlds = self.parse_search_results(html = resp.text, api_name = rld_obj.api_name, brand_name = brand_name, manufacturer = manufacturer)

            # 4) Return them in the 'potentialRLDs' key
            return {"potential_RLDs": [potential_rlds]}

        except Exception as exc:
            logging.error(f"DailyMedResearch node failed: {exc}", exc_info=True)
            rld_obj = state["RLD"]
            return {"potential_RLDs": PotentialRLD(api_name=rld_obj.api_name, brand_name = rld_obj.api_name, manufacturer = "", title="", image_url="", setid="")}
