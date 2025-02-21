import requests
from bs4 import BeautifulSoup
from src.graph_final import drug_development_researcher_graph

def scrape_dailymed_label_by_sectioncode(setid: str) -> dict:
    """
    Scrapes a DailyMed drug label by setid, returning sections based on data-sectioncode attributes,
    plus a 'product_info_str' key that captures the tables under 'Ingredients and Appearance'.
    """
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

    # Prepare an output dictionary, including our new "product_info_str"
    label_data = {v: "" for v in SECTIONCODE_MAP.values()}
    label_data["product_info_str"] = ""
    # (Optional) store the entire HTML if you want
    # label_data["raw_html"] = ""

    base_url = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid="
    url = base_url + setid
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError(f"Failed to retrieve page. Status code: {r.status_code}")

    # Parse HTML
    soup = BeautifulSoup(r.text, "html.parser")

    # 1) Extract main sections by data-sectioncode
    section_divs = soup.find_all("div", class_="Section", attrs={"data-sectioncode": True})
    for div in section_divs:
        section_code = div.get("data-sectioncode", "")
        if section_code in SECTIONCODE_MAP:
            section_key = SECTIONCODE_MAP[section_code]
            text_content = div.get_text(separator="\n", strip=True)
            # If repeated codes appear, either concatenate or skip as needed:
            if label_data[section_key]:
                label_data[section_key] += "\n\n" + text_content
            else:
                label_data[section_key] = text_content

    # 2) Capture the product information tables (“Ingredients and Appearance”) 
    #    by searching for divs with class="DataElementsTables"
    product_info_divs = soup.find_all("div", class_="DataElementsTables")
    all_tables_text = []
    for div in product_info_divs:
        # You can decide whether you want plain text or HTML.
        # Plain text:
        table_text = div.get_text(separator="\n", strip=True)
        # If you want the HTML instead:
        # table_text = str(div)
        all_tables_text.append(table_text)

    # Combine them into a single string
    if all_tables_text:
        label_data["product_info_str"] = "\n\n".join(all_tables_text)

    return label_data

if __name__ == "__main__":
    # Example usage with a known setid
    test_setid = "9333c79b-d487-4538-a9f0-71b91a02b287"
    #results = scrape_dailymed_label_by_sectioncode(test_setid)
    #for k, v in results.items():
        #print(f"\n=== {k.upper()} ===\n{v}\n")

    import os
    from IPython.display import Image
    from pathlib import Path

    # Definir ruta de salida
    output_dir = os.getcwd()
    output_filename = "graph.png"
    output_path = os.path.join(output_dir, output_filename)

    # Crear el directorio si no existe
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Obtener la imagen en bytes
    image_bytes = drug_development_researcher_graph.get_graph().draw_mermaid_png()

    # Guardar la imagen en disco
    with open(output_path, "wb") as f:
        f.write(image_bytes)

    print(f"Imagen guardada en: {output_path}")

