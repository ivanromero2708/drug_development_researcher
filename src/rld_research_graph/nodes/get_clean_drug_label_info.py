import logging
import requests
import pdfplumber
import re
from io import BytesIO
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableConfig
from src.rld_research_graph.state import (
    RLDResearchGraphState, 
    DrugLabelDoc
)
from src.state import RLD
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

class GetCleanDrugLabelInfo:
    def __init__(self):
        self.configurable = None

    ##########################
    # 1) LLM logic for title check
    ##########################
    def call_llm_for_title_check(
        self,
        title: str,
        brand_name: str,
        api_names: List[str],
        dosage_form: str,
        is_combination: bool,
        config: RunnableConfig,
    ) -> bool:
        """
        A short LLM-based check that returns True if `title` 
        corresponds to the desired brand, dosage form, 
        and single/combo logic.
        """

        class LabelTitleCheck(BaseModel):
            logic_check: Literal["YES", "NO"] = Field(
                ...,
                description="A short LLM-based check that returns YES if title is correct for brand/dosage_form and single/combination logic."
            )

        system_msg = SystemMessage(content=(
            "You are a classification assistant that decides whether a drug label title matches "
            "the user’s brand, dosage form, and single- or combination-API criteria. "
            "Output only 'YES' or 'NO'."
        ))

        user_prompt = f"""
We have a drug label title: "{title}"
Brand name to match: "{brand_name}"
API names: {api_names}
Desired dosage form: "{dosage_form}"
is_combination: {is_combination}

Rules:
- If is_combination=True, the label must mention multiple distinct APIs or synonyms, or indicate multiple active ingredients.
- If is_combination=False, it must only mention a single API or synonyms, and must not mention multiple distinct actives.
- The dosage form (e.g., 'tablet', 'capsule') should be compatible with or at least not conflict with the label title.

Do we accept this title as a correct match for brand/dosage_form and single/combination logic?
Answer 'YES' or 'NO' only.
""".strip()

        user_msg = HumanMessage(content=user_prompt)

        # Use an LLM from configuration
        from src.configuration import Configuration
        cfg = Configuration.from_runnable_config(config)
        llm = ChatOpenAI(model=cfg.gpt4o, temperature=0.0)
        structured_llm = llm.with_structured_output(LabelTitleCheck)

        response = structured_llm.invoke([system_msg, user_msg])
        return (response.logic_check == "YES")

    ##########################
    # 2) Query DailyMed to find setid
    ##########################
    def get_spl_setid(
        self,
        search_name: str,
        api_names: List[str],
        dosage_form: str,
        is_combination: bool,
        config: RunnableConfig
    ) -> Optional[str]:
        """
        1. Queries the DailyMed API with `search_name` (which could be brand or API).
        2. For each entry in the 'data' array, calls LLM check to confirm single/combo logic + dosage form.
        3. Picks the entry with highest spl_version among those that pass.
        """
        url = f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name={search_name}"
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
        except Exception as e:
            logging.error(f"Failed to retrieve data from DailyMed for '{search_name}': {e}")
            return None

        data_json = response.json()
        entries = data_json.get("data", [])
        if not entries:
            logging.warning(f"No SPL found for '{search_name}'.")
            return None

        accepted = []
        for entry in entries:
            title = entry.get("title", "")
            if not title:
                continue

            # Then do LLM check
            is_ok = self.call_llm_for_title_check(
                title=title,
                brand_name=search_name,
                api_names=api_names,
                dosage_form=dosage_form,
                is_combination=is_combination,
                config=config
            )
            if is_ok:
                accepted.append(entry)

        if not accepted:
            logging.warning(f"No entries passed LLM filter for '{search_name}'.")
            return None

        # Among accepted, pick highest spl_version
        best_entry = max(accepted, key=lambda x: x.get("spl_version", 0))
        return best_entry.get("setid")

    ##########################
    # 3) Download PDF
    ##########################
    def download_pdf(self, setid: str) -> BytesIO:
        pdf_url = f"https://dailymed.nlm.nih.gov/dailymed/downloadpdffile.cfm?setId={setid}"
        response = requests.get(pdf_url)
        if response.status_code != 200:
            raise Exception(f"Failed to download PDF for setid {setid}. Status {response.status_code}")
        return BytesIO(response.content)

    ##########################
    # 4) Extract text + tables
    ##########################
    def extract_text_and_append_tables(self, pdf_file: BytesIO) -> str:
        all_text = ""
        tables_text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text() or ""
                all_text += page_text + "\n"
                page_tables = page.extract_tables()
                for t_idx, table in enumerate(page_tables, start=1):
                    tables_text += f"\n[Table {t_idx} on page {page_number}]\n"
                    for row in table:
                        row_str = " | ".join(cell if cell else "" for cell in row)
                        tables_text += row_str + "\n"

        final_text = all_text.strip() + "\n\n=== TABLES AT END ===\n\n" + tables_text.strip()
        return final_text

    ##########################
    # 5) Split PDF into known sections
    ##########################
    def split_pdf_sections(self, full_text: str) -> dict:
        marker = "FULL PRESCRIBING INFORMATION"
        idx = full_text.find(marker)
        if idx != -1:
            text_for_splitting = full_text[idx:]
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
        pattern = "(" + "|".join([re.escape(h) for h in section_headers]) + ")"
        parts = re.split(pattern, text_for_splitting)

        sections = {}
        current_header = None
        for part in parts:
            stripped = part.strip()
            if stripped in section_headers:
                current_header = stripped
                sections[current_header] = ""
            else:
                if current_header:
                    sections[current_header] += part

        cleaned = {}
        for header, content in sections.items():
            c = content.strip()
            if c:
                cleaned[header] = c
        return cleaned

    ##########################
    # 6) Main run
    ##########################
    def run(self, state: RLDResearchGraphState, config: RunnableConfig) -> RLDResearchGraphState:
        """
        1) Attempt to use brand_name from RLD to get setid from DailyMed.
        2) If that fails, fallback to the first API name.
        3) Validate single/combination logic, dosage form, etc.
        4) Download and parse the PDF from DailyMed if found.
        5) Return the structured DrugLabelDoc or empty if not found.
        """
        try:
            # Retrieve the RLD object from state
            rld_obj = state["RLD"]
            brand_name = (rld_obj.brand_name or "").strip()
            dosage_form = (rld_obj.rld_dosage_form or "").strip()
            is_combination = (state.get("is_rld_combination","N") == "Y")

            # Parse api_name => list
            if "+" in rld_obj.api_name:
                api_names = [x.strip() for x in rld_obj.api_name.split("+")]
            else:
                api_names = [rld_obj.api_name.strip()]

            # 1) First try brand_name
            setid = None
            if brand_name:
                setid = self.get_spl_setid(
                    search_name=brand_name,
                    api_names=api_names,
                    dosage_form=dosage_form,
                    is_combination=is_combination,
                    config=config
                )
            else:
                logging.warning("No brand_name found in RLD; skipping brand-based search.")

            # 2) If brand_name gave no results, fallback to first API name
            if not setid:
                logging.warning("No setid found for brand. Attempting fallback with API name.")
                setid = self.get_spl_setid(
                    search_name=api_names[0],
                    api_names=api_names,
                    dosage_form=dosage_form,
                    is_combination=is_combination,
                    config=config
                )
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

            # 3) Download PDF
            pdf_file = self.download_pdf(setid)

            # 4) Extract text + tables
            full_text = self.extract_text_and_append_tables(pdf_file)

            # 5) If "PRINCIPAL DISPLAY PANEL" found, separate it
            pdp_marker = "PRINCIPAL DISPLAY PANEL"
            pdp_idx = full_text.find(pdp_marker)
            product_info_str = ""
            if pdp_idx != -1:
                product_info_str = full_text[pdp_idx:].strip()
                full_text = full_text[:pdp_idx].strip()

            # 6) Split PDF sections
            splitted = self.split_pdf_sections(full_text)

            # 7) Map to fields
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
                "product_info_str": product_info_str,
            }

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

            for header, txt in splitted.items():
                f = header_to_field.get(header)
                if f:
                    label_data[f] = txt.strip()

            # 8) Build doc model
            return {"drug_label_doc": DrugLabelDoc(**label_data)}

        except Exception as e:
            logging.error(f"Error in get_clean_drug_label_info: {str(e)}")
            # Return empty doc
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
