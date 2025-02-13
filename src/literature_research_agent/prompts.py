PROMPT_EXTRACT_INFORMATION = """
You are an expert pharmaceutical researcher specializing in pharmaceutical chemistry. Your task is to analyze the consolidated research report and extract all relevant data points into a structured JSON object that adheres exactly to the schema defined by APILiteratureData. The report is detailed, technical, and written in a scientific tone typical of a research article. Use precise and exhaustive language to capture all quantitative and qualitative details.

The data fields to extract are:

api_name: The official name of the API as presented in the report title or header.
cas_number: The unique Chemical Abstracts Service (CAS) registry number in the format XXXX-XX-X.
description: A detailed physical description of the API, including appearance, texture, and notable physical properties (presented as bullet points if applicable).
solubility: A comprehensive summary of the API’s solubility in various solvents, including quantitative measurements and conditions.
melting_point: The melting point of the API, expressed in a format such as "value ± deviation °C" and including measurement conditions.
chemical_names: The complete IUPAC name of the API, detailing its chemical structure using standardized nomenclature.
molecular_formula: The molecular formula of the API, presented in Hill notation.
molecular_weight: The molecular weight of the API in g/mol.
log_p: The octanol-water partition coefficient (LogP), indicating the API’s lipophilicity, with relevant measurement details.
boiling_point: The boiling point of the API, including temperature, pressure conditions (e.g., "value °C at 0.02 mm Hg"), and units.
polymorphs: A thorough description of the API’s polymorphic forms, including the number of forms, crystal systems, melting points, density variations, thermodynamic data, and literature references.
scheme_of_degradation_route: A detailed explanation of the API’s degradation pathways, specifying conditions, mechanistic steps, degradation products, kinetic parameters, and supporting references.
stability_indicators: An exhaustive description of the API’s stability data, including recovery percentages, assay results from stability-indicating methods, observed trends under stress conditions, and citations.
impurities: Detailed information on any impurities, including chemical identities, CAS numbers, quantitative levels, origins (e.g., degradation or synthesis byproducts), and literature support.
biopharmaceutical_classification: A detailed classification of the API according to the Biopharmaceutical Classification System (BCS), with solubility, permeability data, and experimental correlations, including references.
hygroscopicity: Detailed data on the API’s hygroscopic properties, including experimental conditions (e.g., relative humidity, temperature) and quantitative moisture uptake measurements, with citations.
chirality_or_specific_optical_rotation: Information on the API’s chiral properties or specific optical rotation, including measured values, enantiomeric purity, and stereochemical analysis, supported by literature.
glass_transition_temperature: The glass transition temperature (Tg) of the API, including the method of determination (e.g., DSC), exact values or ranges, and literature references.
degradation_temperature: The temperature at which the API degrades, including experimental conditions, identified thresholds, and any kinetic data, with supporting references.

Steps:
1. Thoroughly review the pharmaceutical consolidated report.
2. Identify and extract each data field as specified above, ensuring that all numerical values, units, and literature citations are captured accurately.
3. Use technical, precise language appropriate for pharmaceutical chemistry and maintain a scientific, research-article tone.
4. Map the extracted data to the corresponding keys in the JSON object.
5. If a field is missing in the report, assign an empty string or null value.
6. Output the result solely as a JSON object with keys exactly matching the APILiteratureData schema, without any additional commentary.

Output Format
The final output must be a JSON object formatted as follows (do not wrap in markdown code blocks):

{{ "api_name": "...", "cas_number": "...", "description": "...", "solubility": "...", "melting_point": "...", "chemical_names": "...", "molecular_formula": "...", "molecular_weight": ..., "log_p": "...", "boiling_point": "...", "polymorphs": "...", "scheme_of_degradation_route": "...", "stability_indicators": "...", "impurities": "...", "biopharmaceutical_classification": "...", "hygroscopicity": "...", "chirality_or_specific_optical_rotation": "...", "glass_transition_temperature": "...", "degradation_temperature": "...", "rld_special_characteristics": "...", "rld_manufacturing_process_info": "..." }}

Examples: For example, if the report specifies that the API is "Dronabinol" with a CAS Number of "1972-08-3", your output should begin as:

{{ "api_name": "Dronabinol", "cas_number": "1972-08-3", "description": "...", ... }}

Notes:
Use Markdown hyperlinks for inline citations when applicable.
The output must be detailed, exhaustive, and use technical language from pharmaceutical chemistry.
Do not include any additional text besides the JSON object.
"""


PROMPT_GENERATE_REPORT = """
You are an expert pharmaceutical researcher tasked with writing a comprehensive, fact-based report on the API **{API}** using validated chemical data.
Write the report in plain text format WITHOUT including a title in the body; the title and date will be added separately.
Your report must be highly precise and data-rich. Use ONLY the validated data from the APIExternalData model and evidence provided.

**Validated API Properties** (strictly use these values):
- CAS Number: <cas_number>{cas_number}</cas_number>
- Molecular Formula: <molecular_formula>{molecular_formula}</molecular_formula>
- Molecular Weight: <molecular_weight>{molecular_weight}</molecular_weight>
- IUPAC Name: <chemical_names>{chemical_names}</chemical_names>
- LogP: <log_p>{log_p}</log_p>
- Melting Point: <melting_point>{melting_point}</melting_point>
- Boiling Point: <boiling_point>{boiling_point}</boiling_point>
- Solubility: <solubility>{solubility}</solubility>
- Physical Description: <description>{description}</description>
- pKa: <pKa>{pka}</pKa>
- Stability conditions: <stability_conditions>{stability_conditions}</stability_conditions>

Focus on the following sections and ensure that each API property is addressed as defined below:

1. **Introduction**:
   - Provide a concise overview of the API, including its chemical properties, therapeutic use, dosage form, and route of administration.
   - Include specific data on its chemical composition or key physicochemical parameters (e.g., melting point, pKa, molecular weight) if available.

2. **Research Findings by API Property**:
   For each API property listed below, extract and report the key findings from the evidence provided. Your summary must include specific numerical values, experimental data, and precise study results as follows:

   - CAS Number: Just report the value.
   
   - Molecular Formula: Just report the value.
   
   - Molecular Weight: Just report the value.
   
   - IUPAC Name: Just report the value.
   
   - LogP: Just report the values.
   
   - Stability conditions: A detailed scientific- technical description regarding the storage conditions under which the API is stable at shelf-life.
   
   - pKa: Report the pKa values.
   
   - Melting Point: Just report the values.
   
   - Boiling Point: Just report the values.
   
   - Solubility: Just report the values.
   
   - Physical Description: Just report the values.
   
   - **polymorphs**:  
     Describe the different polymorphic forms of the API. Include the number of forms identified, their crystal systems (e.g., triclinic, monoclinic), melting points, density differences, and any thermodynamic data such as transition temperatures or free energy changes.

   - **scheme_of_degradation_route**:  
     Explain the degradation pathways of the API. Report the conditions under which degradation occurs (e.g., UV exposure, temperature, pH), the mechanisms involved (e.g., photolysis, hydrolysis), and include specific degradation products or reaction schemes along with any kinetic parameters (e.g., degradation percentages).

   - **stability_indicators**:  
     Present quantitative stability data. Include recovery percentages, assay results (e.g., from stability-indicating HPLC methods), and any observed changes in API potency or purity under different stress conditions.

   - **impurities**:  
     Provide detailed information on identified impurities. For each impurity, include its CAS number, chemical formula, molecular weight, and measured levels (e.g., as percentages). Also mention whether the impurity is a synthetic byproduct, a degradation product, or a metabolite.

   - **biopharmaceutical_classification**:  
     Summarize the classification of the API according to the Biopharmaceutical Classification System (BCS). Include relevant data on solubility, permeability, and any experimental in vitro or in vivo correlation that supports the classification.

   - **hygroscopicity**:  
     Report experimental findings on the API's moisture absorption. Include conditions such as relative humidity and temperature, and numerical values (e.g., percentage of moisture uptake), along with any implications for formulation stability.

   - **chirality_or_specific_optical_rotation**:  
     Describe the chiral properties of the API. Include the measured optical rotation values, the enantiomeric purity (if applicable), and any direct study findings regarding its stereochemistry.

   - **glass_transition_temperature**:  
     Report the glass transition temperature (Tg) of the API, citing the method of determination (e.g., DSC) and the exact value or range measured. Explain its relevance to the API’s physical stability.

   - **degradation_temperature**:  
     Specify the temperature(s) at which the API degrades. Include details of the method used for the measurement and any observed thresholds or critical points.

   - **rld_special_characteristics**:  
     For the Reference Listed Drug (RLD), describe any unique characteristics such as the crystalline form, particle size distribution, or other special physical properties that distinguish it from generic formulations.

   - **rld_manufacturing_process_info**:  
     Summarize the manufacturing process details for the RLD. Include key process parameters, quality control measures, and any recommended processing conditions as reported in the literature or regulatory documents.

3. **Conclusions and Recommendations**:
   - Provide a clear summary of the overall insights, supported by precise data points from the evidence.
   - Propose specific next steps for further research or development, citing numerical or factual evidence as justification.

4. **Citations**:
   - Ensure that inline citations appear as Markdown hyperlinks within the text.
   - At the end of the report, list all source URLs used as Markdown hyperlinks.

### Evidence from Selected Documents:
<context>
{context}
</context>

Generate the report solely based on the provided evidence. Your answer must be detailed, precise, and data-rich.
"""

PROMPT_CLUSTER_RELATED_DOCS = """
You are an expert in pharmaceutical literature analysis. We have conducted an extensive literature search related to a pharmaceutical API, and now you have retrieved several documents (each with its URL and a brief content snippet). However, these documents cover different aspects of the API. Your task is to accurately cluster these documents into groups corresponding to the following API properties:

1. polymorphs: Detailed description of polymorphic forms of the active substance.
2. scheme_of_degradation_route: Detailed scheme of degradation routes based on literature and DMF sources.
3. stability_indicators: Key stability indicators.
4. impurities: Information on relevant impurities from literature, DMF, and USP Monograph.
5. biopharmaceutical_classification: Classification based on physicochemical properties and permeability.
6. hygroscopicity: Data on hygroscopicity from PubChem and relevant literature.
7. chirality_or_specific_optical_rotation: Information on chirality or specific optical rotation.
8. glass_transition_temperature: Glass transition temperature as reported in studies.
9. degradation_temperature: Degradation temperature.
10. rld_special_characteristics: Special characteristics of the API and excipients for the RLD.
11. rld_manufacturing_process_info: Manufacturing process information for the RLD, including controls and recommended conditions.

### API & Product Context
- **API Name**: {API}
- **Product Dosage Form**: {product_dosage_form}
- **Route of Administration**: {route_of_administration}

This context represents the core characteristics of the product and should be used as a baseline to judge the relevance of each document.

### Retrieved Documents for Clustering
Below is the list of retrieved documents, each with its URL and a brief content snippet:
{doc_list}

### Clustering Instructions
- **Relevance Based on Context**: Evaluate each document for clear, detailed information on one or more API properties using the above context.
- **Multi-Property Assignment**: A document may appear in more than one cluster if it covers several properties.
- **Handling Non-Relevant Documents**: If a document does not provide clear information for any property, omit it from all clusters.
- **Complete Coverage**: For any property that lacks relevant documents, return an empty list.

### Output Format
Return your output exactly in the following JSON format (do not include any markdown formatting):
{{
   "clusters": [
      {{
         "property": "polymorphs",
         "documents": ["url1", "url2", ...]
      }},
      {{
         "property": "scheme_of_degradation_route",
         "documents": [...]
      }},
      {{
         "property": "stability_indicators",
         "documents": [...]
      }},
      {{
         "property": "impurities",
         "documents": [...]
      }},
      {{
         "property": "biopharmaceutical_classification",
         "documents": [...]
      }},
      {{
         "property": "hygroscopicity",
         "documents": [...]
      }},
      {{
         "property": "chirality_or_specific_optical_rotation",
         "documents": [...]
      }},
      {{
         "property": "glass_transition_temperature",
         "documents": [...]
      }},
      {{
         "property": "degradation_temperature",
         "documents": [...]
      }},
      {{
         "property": "rld_special_characteristics",
         "documents": [...]
      }},
      {{
         "property": "rld_manufacturing_process_info",
         "documents": [...]
      }}
   ]
}}
"""

PROMPT_GENERATE_SUB_QUESTIONS = """
Generate one detailed search query for web research per each of the next properties, that when used for literature research, will uncover comprehensive information about the API’s properties and behavior in its pharmaceutical context:

1. Polymorphs: Detailed description of polymorphic forms of the active substance identified in the literature.
2. Scheme of degradation routes: Detailed scheme of degradation routes for the Active Pharmaceutical Ingredient.
3. Stability indicators: Key stability indicators for the drug product obtained from the literature.
4. Impurities: Detailed Technical Information on impurities of the Active Ingredient derived from the literature.
5. Biopharmaceutical classification: BCS Classification based on physicochemical properties solubility and permeability.
6. Hygroscopicity: Data on hygroscopicity of the Active Ingredient as raw material collected through relevant literature.
7. Chirality or specific optical rotation: Information on chirality or specific optical rotation for the API.
8. Glass transition temperature: Glass transition temperature values for the given API if applies.
9. Degradation temperature: Temperature at which API degradation is identified in the literature.

Inputs:
Active Pharmaceutical Ingredient (API) to be investigated: {API}
Product route of administration: {route_of_administration}

Additional details:
1. Use the provided API and route of administration as contextual information.
2. Ensure that the generated queries cover all eleven aspects listed above.
3. For each aspect, include reasoning or contextual analysis on what specific information should be captured. Present the reasoning before listing the final search queries.
4. Avoid any conclusions or definitive statements until all reasoning steps have been presented.

Output Format:
The final answer should be a JSON object with one key: queries. The value for queries must be an array of strings, where each string is a search query that targets one or more of the required aspects. The JSON must not include any markdown formatting or code block markers.

Notes:
Begin your answer with the reasoning or contextual analysis for each required aspect.
End with the final JSON output listing the generated search queries.
Ensure that all required fields are addressed without omitting any detail.
"""