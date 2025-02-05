

PROMPT_GENERATE_SUB_QUESTIONS = """
Generate {number_of_queries} detailed search queries that, when used for literature research, will uncover comprehensive information about the API’s properties and behavior in its pharmaceutical context.
- Polymorphs – Detailed description of polymorphic forms of the active substance identified in the literature.
- Scheme of degradation routes – Detailed scheme of degradation routes.
- Stability indicators – Key stability indicators for the drug product obtained from the literature.
- Impurities – Information on relevant impurities of the Active Ingredient derived from the literature.
- Biopharmaceutical classification – Classification based on physicochemical properties and permeability.
- Hygroscopicity – Data on hygroscopicity collected through relevant literature.
- Chirality or specific optical rotation – Information on chirality or specific optical rotation for the API.
- Glass transition temperature – Information based on available studies in the literature.
- Degradation temperature – Temperature at which API degradation is identified in the literature.
- RLD special characteristics – Special characteristics of the API and excipients for the RLD, such as crystalline form or particle size.
- RLD manufacturing process information – Information on the manufacturing process for the RLD, including controls and recommended conditions.

1. Inputs:
- Active Pharmaceutical Ingredient (API) to be investigated: {API}
- Product desired dosage form: {product_dosage_form}
- Product route of administration: {route_of_administration}

2.Additional details:
Use the provided API, dosage form, and route of administration as contextual information.
Ensure that the generated queries collectively cover all eleven aspects listed above.
For each aspect, include reasoning or contextual analysis on what specific information should be captured. Present the reasoning before listing the final search queries.
If possible, combine related aspects in one query while ensuring that no required field is omitted.
Avoid any conclusions or definitive statements until all reasoning steps have been presented.

3. Output Format: The final answer should be a JSON object with one key: queries: an array of strings, where each string is a search query targeting one or more of the required aspects. The JSON must not include any markdown formatting or code block markers. It is important that you generate {number_of_queries} queries that group all the needed information from the API

4. Examples:
- "Dronabinol": 
    - "What are the reported polymorphic forms and degradation schemes of Dronabinol in capsule formulations for oral administration, and which stability indicators are highlighted in the literature?"
    - "How do impurities, hygroscopicity, and chirality or specific optical rotation influence the formulation of Dronabinol in capsule dosage forms for oral administration?"
    - "What are the known glass transition temperature and degradation temperature values for Dronabinol, and what RLD special characteristics and manufacturing process details are described in relevant studies?"

- "Acetazolamide": 
    - "What are the known polymorphic forms and detailed degradation routes of Acetazolamide in tablet formulations for oral administration, including key stability indicators from the literature?"
    - "How are impurities, biopharmaceutical classification, and hygroscopicity characterized for Acetazolamide in tablet dosage forms, and what impact do they have on formulation stability?"
    - "What information is available regarding the chirality or specific optical rotation, glass transition temperature, and degradation temperature of Acetazolamide, along with its RLD special characteristics and manufacturing process details?"
- "Aspirin":
    - "What are the reported polymorphic forms and degradation routes for Aspirin in tablet formulations for oral administration, and what stability indicators have been identified in the literature?"
    - "How do impurities, biopharmaceutical classification, and hygroscopicity affect Aspirin's formulation in tablet dosage forms for oral administration?"
    - "What data exists on the glass transition temperature, degradation temperature, and RLD special characteristics and manufacturing process information for Aspirin in oral tablet formulations?"
- "Vonoprazan": 
    - "What are the known polymorphic forms and degradation schemes of Vonoprazan in tablet formulations for oral administration, and which stability indicators are reported in scientific literature?"
    - "How are impurities, biopharmaceutical classification, and hygroscopicity described for Vonoprazan in tablet dosage forms, and what insights are available on chirality or specific optical rotation?"
    - "What information is available on the glass transition temperature, degradation temperature, and RLD special characteristics and manufacturing process details for Vonoprazan in oral formulations?"

5. Notes:
Begin with your reasoning or contextual analysis for each required aspect.
End with the final JSON output listing the generated search queries.
Ensure that all required fields are addressed without omitting any detail.
"""