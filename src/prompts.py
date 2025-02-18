PROMPT_EXTRACT_INPUT_INFORMATION = """
You are an expert pharmaceutical researcher. Below is a detailed text containing product information for a pharmaceutical product. Your task is to extract the following information and return it as a JSON object with exactly these keys (if a field cannot be determined, return an empty string):

"APIs": A list of active pharmaceutical ingredients. Each element must be an object with the key "API_name" (e.g., [{{"API_name": "Acetazolamide"}}]).
"product_name": The full product name, including active ingredients and dosage form.
"product_type": The pharmaceutical product type (e.g., OTC, RX, Nutraceutical, Cosmetic).
"generic_name": The generic or brand name.
"product_strength": Details on the active ingredients and their respective strengths.
"product_dosage_form": The dosage form (e.g., tablets, softgels, syrup).
"route_of_administration": The route of administration (e.g., oral, topical, nasal).
"product_dose": The desired dose, or a note if not available (e.g., "According to physician's prescription").
"physical_characteristics": The desired physical characteristics (e.g., color, shape, printing).
"packaging_type": The secondary packaging specifications.
"commercial_presentations": Details on the commercial presentation (e.g., "Box of 30 tablets").
"required_expiration_time": The required expiration time in months or years.
"observations": Any additional observations.
NOTE: The extraction must capture specific numerical data (e.g., concentrations, dosages, durations) and direct research details. Use precise technical language in {language_for_extraction}.

Text:
<product_input_information>
{product_input_information}
</product_input_information>
"""

PROMPT_EXTRACT_API_INFORMATION = """
You are an expert pharmaceutical researcher. Below is a detailed text containing exact information about active pharmaceutical ingredients, and their desired dosage forms for a pharmaceutical product. Your task is to extract the following information and return it as a JSON object with exactly these keys (if a field cannot be determined, return an empty string):

"APIs": A list of active pharmaceutical ingredients. Each element must be an object with the key "API_name" (e.g., [{{"API_name": "Acetazolamide", "desired_dosage_form": "CAPSULE"}}]).
NOTE: The extraction must capture specific numerical data (e.g., concentrations, dosages, durations) and direct research details. Use precise technical language in english.

Active Pharmaceutical Ingredients Text Information:
<apis_text_information>
{apis_text_information}
</apis_text_information>
"""