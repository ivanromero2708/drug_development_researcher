import logging
import requests
import re
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

from bs4 import BeautifulSoup

from langchain_core.runnables import RunnableConfig

from src.product_research_graph.product_enrichment_graph.state import (
    ProductEnrichmentGraphState,
    DrugLabelDoc,
)

from src.state import RLD

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

class GetCleanDrugLabelInfo:
    def __init__(self):
        self.configurable = None

    ##########################
    # 1) WEB-SCRAPING instead of PDF
    ##########################
    
    def scrape_dailymed_label_html(self, setid: str) -> dict:
        """
        Scrapes a DailyMed drug label page by setid, returning:
         - The main label sections based on data-sectioncode attributes
         - A 'product_info_str' capturing "Ingredients and Appearance" tables
        """
        # This dictionary maps known data-sectioncode values to your doc fields.
        # Adjust codes for your label as needed.
        SECTIONCODE_MAP = {
            "34067-9": "indications_usage",
            "34068-7": "dosage_administration",
            "43678-2": "dosage_forms_strengths",
            "34070-3": "contraindications",
            "43685-7": "warnings_precautions",
            "34084-4": "adverse_reactions",
            "34073-7": "drug_interactions",
            "43684-0": "use_specific_populations",
            "34088-5": "overdosage",
            "34089-3": "description",
            "43680-8": "nonclinical_toxicology",
            "34092-7": "clinical_studies",
            "34069-5": "how_supplied_storage_handling",
            "34076-0": "patient_counseling",
        }

        # Initialize result with empty strings
        label_data = {v: "" for v in SECTIONCODE_MAP.values()}
        label_data["product_info_str"] = ""  # for the "Ingredients and Appearance" data

        base_url = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid="
        url = base_url + setid
        resp = requests.get(url)
        if resp.status_code != 200:
            raise ValueError(f"Failed to retrieve page. Status code: {resp.status_code}")

        soup = BeautifulSoup(resp.text, "html.parser")

        # 1) Extract main sections by data-sectioncode
        section_divs = soup.find_all("div", class_="Section", attrs={"data-sectioncode": True})
        for div in section_divs:
            section_code = div.get("data-sectioncode", "")
            if section_code in SECTIONCODE_MAP:
                section_key = SECTIONCODE_MAP[section_code]
                text_content = div.get_text(separator="\n", strip=True)
                if label_data[section_key]:
                    label_data[section_key] += "\n\n" + text_content
                else:
                    label_data[section_key] = text_content

        # 2) Capture the product information tables (Ingredients and Appearance) from <div class="DataElementsTables">
        product_info_divs = soup.find_all("div", class_="DataElementsTables")
        all_tables_text = []
        for div in product_info_divs:
            table_text = div.get_text(separator="\n", strip=True)
            all_tables_text.append(table_text)

        if all_tables_text:
            label_data["product_info_str"] = "\n\n".join(all_tables_text)

        return label_data

    ##########################
    # 2) Main run
    ##########################
    def run(self, state: ProductEnrichmentGraphState, config: RunnableConfig) -> ProductEnrichmentGraphState:
        """
        1) Attempt to use brand_name from RLD to get setid from DailyMed.
        2) If that fails, fallback to the first API name.
        3) If setid found, do web-scraping of HTML to get label sections + product info.
        4) Return the structured DrugLabelDoc or empty if not found.
        """
        try:
            # Retrieve the RLD object from state
            rld_obj = state["selected_RLD"]
            api_name = rld_obj.api_name
            title = rld_obj.title
            setid = rld_obj.setid
            image_url = rld_obj.image_url
            
            if not setid:
                logging.warning("No setid found. Using empty doc.")
                return {
                    "drug_label_doc": DrugLabelDoc(
                        indications_usage="",
                        dosage_administration="",
                        dosage_forms_strengths="",
                        contraindications="",
                        warnings_precautions="",
                        adverse_reactions="",
                        drug_interactions="",
                        use_specific_populations="",
                        overdosage="",
                        description="",
                        clinical_pharmacology="",
                        nonclinical_toxicology="",
                        clinical_studies="",
                        how_supplied_storage_handling="",
                        patient_counseling="",
                        product_info_str=""
                    )
                }
            
            # 3) Web-scrape the HTML
            label_data = self.scrape_dailymed_label_html(setid)

            # 4) Build the final doc model. 
            #    Map from label_data to your standard 14 fields + product_info_str.
            #    Note that label_data keys match the ones we assigned in scrape_dailymed_label_html.
            #    If a key is missing, default to empty string.
            doc_kwargs = {
                "indications_usage": label_data.get("indications_usage", ""),
                "dosage_administration": label_data.get("dosage_administration", ""),
                "dosage_forms_strengths": label_data.get("dosage_forms_strengths", ""),
                "contraindications": label_data.get("contraindications", ""),
                "warnings_precautions": label_data.get("warnings_precautions", ""),
                "adverse_reactions": label_data.get("adverse_reactions", ""),
                "drug_interactions": label_data.get("drug_interactions", ""),
                "use_specific_populations": label_data.get("use_specific_populations", ""),
                "overdosage": label_data.get("overdosage", ""),
                "description": label_data.get("description", ""),
                "clinical_pharmacology": label_data.get("clinical_pharmacology", ""),
                "nonclinical_toxicology": label_data.get("nonclinical_toxicology", ""),
                "clinical_studies": label_data.get("clinical_studies", ""),
                "how_supplied_storage_handling": label_data.get("how_supplied_storage_handling", ""),
                "patient_counseling": label_data.get("patient_counseling", ""),
                "product_info_str": label_data.get("product_info_str", ""),
            }
            drug_label_doc = DrugLabelDoc(**doc_kwargs)

            return {"drug_label_doc": drug_label_doc}

        except Exception as e:
            logging.error(f"Error in get_clean_drug_label_info: {str(e)}")
            # Return empty doc if anything fails
            return {
                "drug_label_doc": DrugLabelDoc(
                    indications_usage="",
                    dosage_administration="",
                    dosage_forms_strengths="",
                    contraindications="",
                    warnings_precautions="",
                    adverse_reactions="",
                    drug_interactions="",
                    use_specific_populations="",
                    overdosage="",
                    description="",
                    clinical_pharmacology="",
                    nonclinical_toxicology="",
                    clinical_studies="",
                    how_supplied_storage_handling="",
                    patient_counseling="",
                    product_info_str=""
                )
            }




























