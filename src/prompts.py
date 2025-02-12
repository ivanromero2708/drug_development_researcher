PROMPT_EXTRACT_INPUT_INFORMATION = """
You are an expert pharmaceutical researcher. Below is a detailed text containing product information for a pharmaceutical product. Your task is to extract the following information and return it as a JSON object exactly with these keys:

- "APIs": A list of active pharmaceutical ingredients. Each element should be an object with the key "API_name" (e.g., [{{"API_name": "Acetazolamide"}}]).
- "product_name": The full product name, including the active ingredients and the dosage form.
- "product_type": The type of the pharmaceutical product (e.g., OTC, RX, Nutraceutic, Cosmetic, etc.).
- "generic_name": The generic or brand name.
- "product_strength": Details about the active ingredients and their respective strengths.
- "product_dosage_form": The dosage form (e.g., tablets, softgels, syrup, etc.).
- "route_of_administration": The route of administration (e.g., oral, topical, nasal, etc.).
- "product_dose": The desired dose or a note if not available.
- "physical_characteristics": The desired physical characteristics (e.g., color, shape, printing).
- "packaging_type": The secondary packaging specifications.
- "commercial_presentations": Details on the commercial presentation (e.g., Box of 30 tablets).
- "required_expiration_time": The required expiration time in months or years.
- "observations": Any additional observations.

Extract specific numerical data (for example, concentrations, dosages, durations) and direct research details whenever possible. If a field cannot be determined, return an empty string for that field.


NOTE: It is important that the language of the extraction information is in {language_for_extraction}

Text:
<product_input_information>
{product_input_information}
</product_input_information>
"""