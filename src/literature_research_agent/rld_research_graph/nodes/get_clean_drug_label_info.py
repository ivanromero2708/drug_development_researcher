import logging
import requests
import pdfplumber
import re
from io import BytesIO
from pydantic import BaseModel
from src.literature_research_agent.rld_research_graph.state import DrugLabelDoc, RLDResearchGraphState
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration

###############################################################################
# Helper Functions
###############################################################################

def get_spl_setid(product_name: str) -> str:
    """
    Queries the DailyMed API for the specified product name and returns the first SPL setid.
    """
    url = f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name={product_name}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to retrieve data from DailyMed API.")
    data = response.json()
    if 'data' not in data or len(data['data']) == 0:
        raise Exception("No SPL found for the product.")
    spl = data['data'][0]
    setid = spl.get("setid") or spl.get("setId")
    if not setid:
        raise Exception("No SET ID found in SPL data.")
    return setid

def download_pdf(setid: str) -> BytesIO:
    """
    Given a setid from DailyMed, downloads the corresponding PDF file.
    """
    pdf_url = f"https://dailymed.nlm.nih.gov/dailymed/downloadpdffile.cfm?setId={setid}"
    response = requests.get(pdf_url)
    if response.status_code != 200:
        raise Exception("Failed to download PDF file.")
    return BytesIO(response.content)

def extract_text_and_append_tables(pdf_file: BytesIO) -> str:
    """
    Extracts all page text from the PDF and appends table data at the end of the document.
    Returns a single combined string.

    NOTE: If the table content is also recognized as normal text by pdfplumber,
    you might see it twice (once in the main text, once appended as table data).
    """
    all_text = []
    tables_text = []
    with pdfplumber.open(pdf_file) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            # 1. Extract normal text
            page_text = page.extract_text() or ""
            all_text.append(page_text)

            # 2. Extract tables
            page_tables = page.extract_tables()
            for table_index, table in enumerate(page_tables, start=1):
                table_snippet = [f"[Table {table_index} on page {page_number}]"]
                for row in table:
                    row_str = " | ".join(cell if cell else "" for cell in row)
                    table_snippet.append(row_str)
                tables_text.append("\n".join(table_snippet))

    # Combine normal text
    main_text_str = "\n".join(all_text).strip()
    # Combine table text
    tables_str = "\n\n=== TABLES AT END ===\n\n" + "\n\n".join(tables_text).strip()
    return f"{main_text_str}"

def split_pdf_sections(full_text: str) -> dict[str, str]:
    """
    1. Optionally remove everything before 'FULL PRESCRIBING INFORMATION'
       (to skip table of contents).
    2. Split by known section headers.
    3. Return dict: {header -> text}
    """
    marker = "FULL PRESCRIBING INFORMATION"
    marker_index = full_text.find(marker)
    if marker_index != -1:
        text_for_splitting = full_text[marker_index:]
    else:
        text_for_splitting = full_text

    section_headers = [
        "1 INDICATIONS AND USAGE",
        "2 DOSAGE AND ADMINISTRATION",
        "3 DOSAGE FORMS AND STRENGTHS",
        "4 CONTRAINDICATIONS",
        "5 WARNINGS AND PRECAUTIONS",
        "6 ADVERSE REACTIONS",
        "7 DRUG INTERACTIONS",
        "8 USE IN SPECIFIC_POPULATIONS",
        "10 OVERDOSAGE",
        "11 DESCRIPTION",
        "12 CLINICAL PHARMACOLOGY",
        "13 NONCLINICAL TOXICOLOGY",
        "14 CLINICAL STUDIES",
        "16 HOW SUPPLIED/STORAGE AND HANDLING",
        "17 PATIENT COUNSELING INFORMATION"
    ]
    pattern = "(" + "|".join([re.escape(header) for header in section_headers]) + ")"
    parts = re.split(pattern, text_for_splitting)

    sections = {}
    current_header = None
    for part in parts:
        stripped_part = part.strip()
        if stripped_part in section_headers:
            current_header = stripped_part
            sections[current_header] = ""
        else:
            if current_header:
                sections[current_header] += part

    # Remove empty sections
    cleaned_sections = {}
    for header, content in sections.items():
        c = content.strip()
        if c:
            cleaned_sections[header] = c
    return cleaned_sections

###############################################################################
# The Node-Class
###############################################################################

class GetCleanDrugLabelInfo:
    def __init__(self):
        self.configurable = None

    def get_clean_drug_label_info(self, state: RLDResearchGraphState, config: RunnableConfig) -> DrugLabelDoc:
        """
        1. Retrieve product_name from state.
        2. Download PDF from DailyMed.
        3. Extract text + tables in one string.
        4. If 'PRINCIPAL DISPLAY PANEL' is found, cut that portion out of the main text
           and re-append it at the end of product_info_str.
        5. Split the main text by standard Rx headings.
        6. Populate each recognized field in DrugLabelDoc. Everything else remains in product_info_str.
        """
        try:
            product_name = state.get("brand_name", None)
            if not product_name:
                raise ValueError("No 'brand_name' found in state.")
            
            # 1. Download
            setid = get_spl_setid(product_name)
            pdf_file = download_pdf(setid)
            
            # 2. Extract text + tables
            final_text = extract_text_and_append_tables(pdf_file)
            
            product_info_str = ""
            # 3. If "PRINCIPAL DISPLAY PANEL" is found, cut it from the main text and store it for later
            pdp_marker = "PRINCIPAL DISPLAY PANEL"
            pdp_index = final_text.find(pdp_marker)
            if pdp_index != -1:
                product_info_str = final_text[pdp_index:].strip()
                # remove it from the main text portion
                final_text = final_text[:pdp_index].strip()

            # 4. Now do normal section splitting on final_text (the portion before PDP)
            splitted_sections = split_pdf_sections(final_text)

            # 5. Prepare a dict with default empty strings
            label_data = {
                "indications_usage": "",
                "dosage_administration": "",
                "dosage_forms_strengths": "",
                "contraindications": "",
                "warnings_precautions": "",
                "adverse_reactions": "",
                "drug_interactions": "",
                "use_specific_populations": "",
                "overdosage": "",
                "description": "",
                "clinical_pharmacology": "",
                "nonclinical_toxicology": "",
                "clinical_studies": "",
                "how_supplied_storage_handling": "",
                "patient_counseling": "",
                # Start product_info_str with the main text that is not recognized as a standard section
                "product_info_str": product_info_str,
            }

            # 6. Map known headers -> fields
            header_to_field = {
                "1 INDICATIONS AND USAGE": "indications_usage",
                "2 DOSAGE AND ADMINISTRATION": "dosage_administration",
                "3 DOSAGE FORMS AND STRENGTHS": "dosage_forms_strengths",
                "4 CONTRAINDICATIONS": "contraindications",
                "5 WARNINGS AND PRECAUTIONS": "warnings_precautions",
                "6 ADVERSE REACTIONS": "adverse_reactions",
                "7 DRUG INTERACTIONS": "drug_interactions",
                "8 USE IN SPECIFIC_POPULATIONS": "use_specific_populations",
                "10 OVERDOSAGE": "overdosage",
                "11 DESCRIPTION": "description",
                "12 CLINICAL PHARMACOLOGY": "clinical_pharmacology",
                "13 NONCLINICAL TOXICOLOGY": "nonclinical_toxicology",
                "14 CLINICAL STUDIES": "clinical_studies",
                "16 HOW SUPPLIED/STORAGE AND HANDLING": "how_supplied_storage_handling",
                "17 PATIENT COUNSELING INFORMATION": "patient_counseling",
            }

            for header, text_content in splitted_sections.items():
                field_name = header_to_field.get(header)
                if field_name:
                    label_data[field_name] = text_content

            return {"drug_label_doc": DrugLabelDoc(**label_data)}

        except Exception as e:
            logging.error(f"Error in get_clean_drug_label_info: {str(e)}")
            return {"drug_label_doc": DrugLabelDoc(
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
            )}

    def run(self, state: RLDResearchGraphState, config: RunnableConfig) -> dict:
        """
        Called by the pipeline. 
        Returns the Pydantic model as a dict (or you can return the model object).
        """
        return self.get_clean_drug_label_info(state, config)

###############################################################################
# Example Usage (Standalone)
###############################################################################

if __name__ == "__main__":
    class DummyState(dict):
        def get(self, key, default=None):
            return super().get(key, default)

    dummy_state = DummyState({"brand_name": "KEYTRUDA"})
    node = GetCleanDrugLabelInfo()
    result = node.run(dummy_state, config={})
    print("\n=== PRODUCT INFO STR (including appended PDP portion) ===\n")
    print(result)
