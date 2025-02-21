PROMPT_GENERATE_SUB_QUESTIONS = """
Generate one concise search query for each of the following API property aspects, ensuring that the query is specifically tailored to uncover comprehensive and precise information for that property in the context of the given API. For each aspect, first provide a brief reasoning or contextual analysis (in plain language) on what specific information, including values, methods, and references, should be captured. Then list the final search query. Do not include any conclusions in the reasoning section.

Properties:
1. Polymorphic forms of the active pharmaceutical ingredient.
2. Degradation mechanism for the active pharmaceutical ingredient.
3. Forced degradation of the active pharmaceutical ingredient.
4. Impurities of the active pharmaceutical ingredient.
5. Biopharmaceutical classification (BCS) for the active pharmaceutical ingredient.
6. Hygroscopicity Data on the Active Pharmaceutical Ingredient.
7. Chirality or specific optical rotation Data for the Active Pharmaceutical Ingredient.
8. Glass transition temperature for the Active Pharmaceutical Ingredient.
9. Degradation temperature for the Active Pharmaceutical Ingredient.

Inputs:
Active Pharmaceutical Ingredient (API) to be investigated: {API}
Product route of administration: {route_of_administration}

Output Format:
A JSON object with one key “queries” whose value is an array of strings (the search queries). Do not include markdown formatting or code block markers in the output.

Begin your answer with the reasoning for each property, then at the end provide the final JSON output.
"""

PROMPT_EXTRACT_INFORMATION = """
You are an expert pharmaceutical researcher specializing in pharmaceutical chemistry and technology. Analyze the consolidated research report provided below and extract all relevant data points into a structured JSON object that adheres exactly to the schema defined by APILiteratureData. Your extraction must include:

- The property values (e.g., numerical values, units)
- The experimental or extraction methods used to determine these values
- All literature or web references (as URL links) cited in the report

The data fields to extract are:
1. api_name: The official name of the API as indicated in the report header.
2. cas_number: The unique Chemical Abstracts Service (CAS) number in the format XXXX-XX-X.
3. description: A detailed physical description of the API (e.g., appearance, texture) presented as bullet points, including any reference URLs.
4. solubility: A comprehensive summary of the API’s solubility in various solvents, including quantitative data and conditions.
5. melting_point: The melting point, in the format “value ± deviation °C” with measurement conditions.
6. chemical_names: The complete IUPAC name of the API.
7. molecular_formula: The molecular formula in Hill notation.
8. molecular_weight: The molecular weight in g/mol.
9. log_p: The octanol-water partition coefficient, with relevant measurement details.
10. boiling_point: The boiling point including temperature and pressure conditions.
11. polymorphs: A thorough description of the API’s polymorphic forms including the number of forms, crystal systems, melting points, density differences, thermodynamic data, and literature references.
scheme_of_degradation_route: A detailed explanation of the degradation pathways, including conditions (e.g., UV, pH), mechanisms, degradation products, kinetic parameters, and reference URLs.
12. stability_indicators: An exhaustive description of the API’s stability data, including recovery percentages, assay results (e.g., from stability-indicating HPLC), observed trends under stress conditions, and citations.
13. impurities: Detailed information on impurities, including CAS numbers, chemical formulas, molecular weights, measured levels, and whether they are synthetic byproducts, degradation products, or metabolites, with reference URLs.
14. biopharmaceutical_classification: A detailed classification based on physicochemical properties and permeability, including experimental correlations and citations.
15. hygroscopicity: Detailed data on moisture absorption, experimental conditions (e.g., relative humidity, temperature), and quantitative measurements with reference URLs.
16. chirality_or_specific_optical_rotation: Information on chiral properties or specific optical rotation, including measured values, enantiomeric purity, and supporting literature references.
17. glass_transition_temperature: The glass transition temperature (Tg) including determination method (e.g., DSC), exact values or ranges, and reference URLs.
18. degradation_temperature: The temperature at which the API degrades, including experimental conditions, thresholds, kinetic data, and supporting references.

Steps:
1. Review the consolidated report thoroughly.
2. Extract each data field using precise and technical language appropriate for pharmaceutical chemistry.
3. For any property where relevant information is not available, assign an empty string or null value.
4. Output only a JSON object with keys exactly matching the APILiteratureData schema (do not include any additional commentary).

Output Format:
The final output must be a JSON object formatted exactly as:
{{ "api_name": "...", "cas_number": "...", "description": "...", "solubility": "...", "melting_point": "...", "chemical_names": "...", "molecular_formula": "...", "molecular_weight": ..., "log_p": "...", "boiling_point": "...", "polymorphs": "...", "scheme_of_degradation_route": "...", "stability_indicators": "...", "impurities": "...", "biopharmaceutical_classification": "...", "hygroscopicity": "...", "chirality_or_specific_optical_rotation": "...", "glass_transition_temperature": "...", "degradation_temperature": "...", "rld_special_characteristics": "...", "rld_manufacturing_process_info": "..." }}

Do not wrap the JSON output in markdown code blocks.
"""


PROMPT_GENERATE_REPORT = """
You are an expert pharmaceutical researcher tasked with writing a comprehensive, fact-based report on the API {API} using only validated chemical data and the evidence provided below. Write the report in plain text without a title (the title and date will be added later). Your report must be highly precise, data-rich, and use advanced pharmaceutical chemistry and technology terminology.

Use the validated API properties strictly as provided:
1. CAS Number: <cas_number>{cas_number}</cas_number>
2. Molecular Formula: <molecular_formula>{molecular_formula}</molecular_formula>
3. Molecular Weight: <molecular_weight>{molecular_weight}</molecular_weight>
4. IUPAC Name: <chemical_names>{chemical_names}</chemical_names>
5. LogP: <log_p>{log_p}</log_p>
6. Melting Point: <melting_point>{melting_point}</melting_point>
7. Boiling Point: <boiling_point>{boiling_point}</boiling_point>
8. Solubility: <solubility>{solubility}</solubility>
9. Physical Description: <description>{description}</description>
10. pKa: <pKa>{pka}</pKa>
11. Stability conditions: <stability_conditions>{stability_conditions}</stability_conditions>

Structure your report as follows:
1. Research Findings by API Property: For each property (CAS Number, Molecular Formula, Molecular Weight, IUPAC Name, LogP, Stability conditions, pKa, Melting Point, Boiling Point, Solubility, Physical Description, polymorphs, scheme_of_degradation_route, stability_indicators, impurities, biopharmaceutical_classification, hygroscopicity, chirality_or_specific_optical_rotation, glass_transition_temperature, degradation_temperature, rld_special_characteristics, rld_manufacturing_process_info), present the key findings as follows:
- Report the specific numerical values or qualitative data.
- Include the experimental or analytical methods used to obtain these values.
- Provide inline citations as Markdown hyperlinks where applicable.

2. Citations: At the end of the report, list all source URLs used as Markdown hyperlinks.

3. Use only the provided evidence in the context section below. Do not include any additional commentary or unverified data.

Evidence from Selected Documents:
<context> {context} </context>
Generate the report solely based on the provided evidence. Your answer must be detailed, precise, and data-rich.
"""