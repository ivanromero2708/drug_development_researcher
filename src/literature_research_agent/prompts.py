PROMPT_GENERATE_REPORT = """
You are an expert pharmaceutical researcher tasked with writing a comprehensive, fact-based report on the API **{API}**.
Write the report in Markdown format WITHOUT including a title in the body; the title and date will be added separately.
Your report must be highly precise and data-rich. Include specific numerical values, measurements, CAS numbers, experimental results, and direct study findings extracted from the evidence provided. Avoid vague generalizations—cite exact values and observations wherever available.

Focus on the following sections and ensure that each API property is addressed as defined below:

1. **Introduction**:
   - Provide a concise overview of the API, including its chemical properties, therapeutic use, dosage form, and route of administration.
   - Include specific data on its chemical composition or key physicochemical parameters (e.g., melting point, pKa, molecular weight) if available.

2. **Research Findings by API Property**:
   For each API property listed below, extract and report the key findings from the evidence provided. Your summary must include specific numerical values, experimental data, and precise study results as follows:

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
{context}

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