import os
from dataclasses import dataclass, field, fields
from typing import Any, Optional, Dict
from langchain_core.runnables import RunnableConfig
from typing_extensions import Annotated
from dataclasses import dataclass
import os, getpass
from dotenv import load_dotenv

load_dotenv()  # Cargar variables de entorno desde .env

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

MAPPING_DRUG_LABEL_SECTION = {
    "API_name_with_UNII": "product_info_str",
    "inactive_ingredients_with_UNII_str": "product_info_str",
    "type_pckg_material": "product_info_str",
    "rld_how_supplied": "how_supplied_storage_handling",
    "rld_physical_characteristics": "product_info_str",
    "rld_storage_conditions": "how_supplied_storage_handling",
    "rld_special_characteristics": "description",
    "strengths": "dosage_forms_strengths",
}

HUMAN_MESSAGE_EXAMPLE1_RLD = {
    "API_name_with_UNII": """
You must generate the “RLD Section” text for the user’s specified section. The user’s data includes:
- API_name: <API_name>Dronabinol</API_name>
- dosage_form: <dosage_form>CAPSULE</dosage_form>
- route_of_administration: <route_of_administration>ORAL</route_of_administration>

**Instructions**:
1. Return a JSON with two fields: "rld_section" matching the requested name, and "research_report" containing only the final text for that snippet. 
2. If bullet points or references like “[25]” appear, preserve them. 
3. If no snippet is provided, say "No data available." 
4. Do not add extra disclaimers or mention chain-of-thought.
5. Keep it concise, formal, and scientifically oriented, exactly for the requested section.

Below is the **relevant snippet** from the drug label or context for this RLD section:
<drug_label_doc_info>
MARINOL 
dronabinol capsule
Product Information
Product Type	HUMAN PRESCRIPTION DRUG	Item Code (Source)	NDC:53097-568
Route of Administration	ORAL	DEA Schedule	CIII    
Active Ingredient/Active Moiety
Ingredient Name	Basis of Strength	Strength
DRONABINOL (UNII: 7J8897W37S) (DRONABINOL - UNII:7J8897W37S)	DRONABINOL	2.5 mg
Inactive Ingredients
Ingredient Name	Strength
GELATIN, UNSPECIFIED (UNII: 2G86QN327L)	 
GLYCERIN (UNII: PDC6A3C0OX)	 
SESAME OIL (UNII: QX10HYY4QV)	 
TITANIUM DIOXIDE (UNII: 15FIX9V2JP)	 
Product Characteristics
Color	WHITE	Score	no score
Shape	ROUND	Size	8mm
Flavor		Imprint Code	UM
Contains	    
Packaging
#	Item Code	Package Description	Marketing Start Date	Marketing End Date
1	NDC:53097-568-60	1 in 1 CARTON	05/10/2017	
1		60 in 1 BOTTLE; Type 0: Not a Combination Product		
Marketing Information
Marketing Category	Application Number or Monograph Citation	Marketing Start Date	Marketing End Date
NDA	NDA018651	05/10/2017	
MARINOL 
dronabinol capsule
Product Information
Product Type	HUMAN PRESCRIPTION DRUG	Item Code (Source)	NDC:53097-569
Route of Administration	ORAL	DEA Schedule	CIII    
Active Ingredient/Active Moiety
Ingredient Name	Basis of Strength	Strength
DRONABINOL (UNII: 7J8897W37S) (DRONABINOL - UNII:7J8897W37S)	DRONABINOL	5 mg
Inactive Ingredients
Ingredient Name	Strength
GELATIN, UNSPECIFIED (UNII: 2G86QN327L)	 
GLYCERIN (UNII: PDC6A3C0OX)	 
SESAME OIL (UNII: QX10HYY4QV)	 
TITANIUM DIOXIDE (UNII: 15FIX9V2JP)	 
FERRIC OXIDE RED (UNII: 1K09F3G675)	 
FERROSOFERRIC OXIDE (UNII: XM0M87F357)	 
Product Characteristics
Color	BROWN	Score	no score
Shape	ROUND	Size	8mm
Flavor		Imprint Code	UM
Contains	    
Packaging
#	Item Code	Package Description	Marketing Start Date	Marketing End Date
1	NDC:53097-569-60	1 in 1 CARTON	05/10/2017	
1		60 in 1 BOTTLE; Type 0: Not a Combination Product		
Marketing Information
Marketing Category	Application Number or Monograph Citation	Marketing Start Date	Marketing End Date
NDA	NDA018651	05/10/2017	
MARINOL 
dronabinol capsule
Product Information
Product Type	HUMAN PRESCRIPTION DRUG	Item Code (Source)	NDC:53097-570
Route of Administration	ORAL	DEA Schedule	CIII    
Active Ingredient/Active Moiety
Ingredient Name	Basis of Strength	Strength
DRONABINOL (UNII: 7J8897W37S) (DRONABINOL - UNII:7J8897W37S)	DRONABINOL	10 mg
Inactive Ingredients
Ingredient Name	Strength
GELATIN, UNSPECIFIED (UNII: 2G86QN327L)	 
GLYCERIN (UNII: PDC6A3C0OX)	 
SESAME OIL (UNII: QX10HYY4QV)	 
TITANIUM DIOXIDE (UNII: 15FIX9V2JP)	 
FERRIC OXIDE RED (UNII: 1K09F3G675)	 
FERRIC OXIDE YELLOW (UNII: EX438O2MRT)	 
Product Characteristics
Color	ORANGE	Score	no score
Shape	ROUND	Size	8mm
Flavor		Imprint Code	UM
Contains	    
Packaging
#	Item Code	Package Description	Marketing Start Date	Marketing End Date
1	NDC:53097-570-60	1 in 1 CARTON	05/10/2017	
1		60 in 1 BOTTLE; Type 0: Not a Combination Product		
Marketing Information
Marketing Category	Application Number or Monograph Citation	Marketing Start Date	Marketing End Date
NDA	NDA018651	05/10/2017	
Labeler - ThePharmaNetwork, LLC (939435280)
Establishment
Name	Address	ID/FEI	Business Operations
Patheon Softgels Inc		002193829	MANUFACTURE(53097-568, 53097-569, 53097-570)
</drug_label_doc_info>
    """,
    "inactive_ingredients_with_UNII_str": """
You must generate the “RLD Section” text for the user’s specified section. The user’s data includes:
- API_name: <API_name>Dronabinol</API_name>
- dosage_form: <dosage_form>CAPSULE</dosage_form>
- route_of_administration: <route_of_administration>ORAL</route_of_administration>

**Instructions**:
1. Return a JSON with two fields: "rld_section" matching the requested name, and "research_report" containing only the final text for that snippet. 
2. If bullet points or references like “[25]” appear, preserve them. 
3. If no snippet is provided, say "No data available." 
4. Do not add extra disclaimers or mention chain-of-thought.
5. Keep it concise, formal, and scientifically oriented, exactly for the requested section.

Below is the **relevant snippet** from the drug label or context for this RLD section:
<drug_label_doc_info>
MARINOL 
dronabinol capsule
Product Information
Product Type	HUMAN PRESCRIPTION DRUG	Item Code (Source)	NDC:53097-568
Route of Administration	ORAL	DEA Schedule	CIII    
Active Ingredient/Active Moiety
Ingredient Name	Basis of Strength	Strength
DRONABINOL (UNII: 7J8897W37S) (DRONABINOL - UNII:7J8897W37S)	DRONABINOL	2.5 mg
Inactive Ingredients
Ingredient Name	Strength
GELATIN, UNSPECIFIED (UNII: 2G86QN327L)	 
GLYCERIN (UNII: PDC6A3C0OX)	 
SESAME OIL (UNII: QX10HYY4QV)	 
TITANIUM DIOXIDE (UNII: 15FIX9V2JP)	 
Product Characteristics
Color	WHITE	Score	no score
Shape	ROUND	Size	8mm
Flavor		Imprint Code	UM
Contains	    
Packaging
#	Item Code	Package Description	Marketing Start Date	Marketing End Date
1	NDC:53097-568-60	1 in 1 CARTON	05/10/2017	
1		60 in 1 BOTTLE; Type 0: Not a Combination Product		
Marketing Information
Marketing Category	Application Number or Monograph Citation	Marketing Start Date	Marketing End Date
NDA	NDA018651	05/10/2017	
MARINOL 
dronabinol capsule
Product Information
Product Type	HUMAN PRESCRIPTION DRUG	Item Code (Source)	NDC:53097-569
Route of Administration	ORAL	DEA Schedule	CIII    
Active Ingredient/Active Moiety
Ingredient Name	Basis of Strength	Strength
DRONABINOL (UNII: 7J8897W37S) (DRONABINOL - UNII:7J8897W37S)	DRONABINOL	5 mg
Inactive Ingredients
Ingredient Name	Strength
GELATIN, UNSPECIFIED (UNII: 2G86QN327L)	 
GLYCERIN (UNII: PDC6A3C0OX)	 
SESAME OIL (UNII: QX10HYY4QV)	 
TITANIUM DIOXIDE (UNII: 15FIX9V2JP)	 
FERRIC OXIDE RED (UNII: 1K09F3G675)	 
FERROSOFERRIC OXIDE (UNII: XM0M87F357)	 
Product Characteristics
Color	BROWN	Score	no score
Shape	ROUND	Size	8mm
Flavor		Imprint Code	UM
Contains	    
Packaging
#	Item Code	Package Description	Marketing Start Date	Marketing End Date
1	NDC:53097-569-60	1 in 1 CARTON	05/10/2017	
1		60 in 1 BOTTLE; Type 0: Not a Combination Product		
Marketing Information
Marketing Category	Application Number or Monograph Citation	Marketing Start Date	Marketing End Date
NDA	NDA018651	05/10/2017	
MARINOL 
dronabinol capsule
Product Information
Product Type	HUMAN PRESCRIPTION DRUG	Item Code (Source)	NDC:53097-570
Route of Administration	ORAL	DEA Schedule	CIII    
Active Ingredient/Active Moiety
Ingredient Name	Basis of Strength	Strength
DRONABINOL (UNII: 7J8897W37S) (DRONABINOL - UNII:7J8897W37S)	DRONABINOL	10 mg
Inactive Ingredients
Ingredient Name	Strength
GELATIN, UNSPECIFIED (UNII: 2G86QN327L)	 
GLYCERIN (UNII: PDC6A3C0OX)	 
SESAME OIL (UNII: QX10HYY4QV)	 
TITANIUM DIOXIDE (UNII: 15FIX9V2JP)	 
FERRIC OXIDE RED (UNII: 1K09F3G675)	 
FERRIC OXIDE YELLOW (UNII: EX438O2MRT)	 
Product Characteristics
Color	ORANGE	Score	no score
Shape	ROUND	Size	8mm
Flavor		Imprint Code	UM
Contains	    
Packaging
#	Item Code	Package Description	Marketing Start Date	Marketing End Date
1	NDC:53097-570-60	1 in 1 CARTON	05/10/2017	
1		60 in 1 BOTTLE; Type 0: Not a Combination Product		
Marketing Information
Marketing Category	Application Number or Monograph Citation	Marketing Start Date	Marketing End Date
NDA	NDA018651	05/10/2017	
Labeler - ThePharmaNetwork, LLC (939435280)
Establishment
Name	Address	ID/FEI	Business Operations
Patheon Softgels Inc		002193829	MANUFACTURE(53097-568, 53097-569, 53097-570)
</drug_label_doc_info>
    """,
    "strengths": """
You must generate the “RLD Section” text for the user’s specified section. The user’s data includes:
- API_name: <API_name>Dronabinol</API_name>
- dosage_form: <dosage_form>CAPSULE</dosage_form>
- route_of_administration: <route_of_administration>ORAL</route_of_administration>

**Instructions**:
1. Return a JSON with two fields: "rld_section" matching the requested name, and "research_report" containing only the final text for that snippet. 
2. If bullet points or references like “[25]” appear, preserve them. 
3. If no snippet is provided, say "No data available." 
4. Do not add extra disclaimers or mention chain-of-thought.
5. Keep it concise, formal, and scientifically oriented, exactly for the requested section.

Below is the **relevant snippet** from the drug label or context for this RLD section:
<drug_label_doc_info>
MARINOL is supplied as round, soft gelatin capsules for oral use as follows:
• 2.5 mg white capsules (Identified UM)
• 5 mg dark brown capsules (Identified UM)
• 10 mg orange capsules (Identified UM)
</drug_label_doc_info>
    """,
    "type_pckg_material": """
You must generate the “RLD Section” text for the user’s specified section. The user’s data includes:
- API_name: <API_name>Dronabinol</API_name>
- dosage_form: <dosage_form>CAPSULE</dosage_form>
- route_of_administration: <route_of_administration>ORAL</route_of_administration>

**Instructions**:
1. Return a JSON with two fields: "rld_section" matching the requested name, and "research_report" containing only the final text for that snippet. 
2. If bullet points or references like “[25]” appear, preserve them. 
3. If no snippet is provided, say "No data available." 
4. Do not add extra disclaimers or mention chain-of-thought.
5. Keep it concise, formal, and scientifically oriented, exactly for the requested section.

Below is the **relevant snippet** from the drug label or context for this RLD section:
<drug_label_doc_info>
NDC 53097-568-60
Bottle of 60 Capsules
Rx Only


marinol 2.5 mg 60 counts container Label

NDC 53097-569-60
Bottle of 60 Capsules
Rx Only


marinol-5mg

NDC 53097-570-60
Bottle of 60 Capsules
Rx Only


marinol-10mg
Close
INGREDIENTS AND APPEARANCE
MARINOL 
dronabinol capsule
Product Information
Product Type	HUMAN PRESCRIPTION DRUG	Item Code (Source)	NDC:53097-568
Route of Administration	ORAL	DEA Schedule	CIII    
Active Ingredient/Active Moiety
Ingredient Name	Basis of Strength	Strength
DRONABINOL (UNII: 7J8897W37S) (DRONABINOL - UNII:7J8897W37S)	DRONABINOL	2.5 mg
Inactive Ingredients
Ingredient Name	Strength
GELATIN, UNSPECIFIED (UNII: 2G86QN327L)	 
GLYCERIN (UNII: PDC6A3C0OX)	 
SESAME OIL (UNII: QX10HYY4QV)	 
TITANIUM DIOXIDE (UNII: 15FIX9V2JP)	 
Product Characteristics
Color	WHITE	Score	no score
Shape	ROUND	Size	8mm
Flavor		Imprint Code	UM
Contains	    
Packaging
#	Item Code	Package Description	Marketing Start Date	Marketing End Date
1	NDC:53097-568-60	1 in 1 CARTON	05/10/2017	
1		60 in 1 BOTTLE; Type 0: Not a Combination Product		
Marketing Information
Marketing Category	Application Number or Monograph Citation	Marketing Start Date	Marketing End Date
NDA	NDA018651	05/10/2017	
MARINOL 
dronabinol capsule
Product Information
Product Type	HUMAN PRESCRIPTION DRUG	Item Code (Source)	NDC:53097-569
Route of Administration	ORAL	DEA Schedule	CIII    
Active Ingredient/Active Moiety
Ingredient Name	Basis of Strength	Strength
DRONABINOL (UNII: 7J8897W37S) (DRONABINOL - UNII:7J8897W37S)	DRONABINOL	5 mg
Inactive Ingredients
Ingredient Name	Strength
GELATIN, UNSPECIFIED (UNII: 2G86QN327L)	 
GLYCERIN (UNII: PDC6A3C0OX)	 
SESAME OIL (UNII: QX10HYY4QV)	 
TITANIUM DIOXIDE (UNII: 15FIX9V2JP)	 
FERRIC OXIDE RED (UNII: 1K09F3G675)	 
FERROSOFERRIC OXIDE (UNII: XM0M87F357)	 
Product Characteristics
Color	BROWN	Score	no score
Shape	ROUND	Size	8mm
Flavor		Imprint Code	UM
Contains	    
Packaging
#	Item Code	Package Description	Marketing Start Date	Marketing End Date
1	NDC:53097-569-60	1 in 1 CARTON	05/10/2017	
1		60 in 1 BOTTLE; Type 0: Not a Combination Product		
Marketing Information
Marketing Category	Application Number or Monograph Citation	Marketing Start Date	Marketing End Date
NDA	NDA018651	05/10/2017	
MARINOL 
dronabinol capsule
Product Information
Product Type	HUMAN PRESCRIPTION DRUG	Item Code (Source)	NDC:53097-570
Route of Administration	ORAL	DEA Schedule	CIII    
Active Ingredient/Active Moiety
Ingredient Name	Basis of Strength	Strength
DRONABINOL (UNII: 7J8897W37S) (DRONABINOL - UNII:7J8897W37S)	DRONABINOL	10 mg
Inactive Ingredients
Ingredient Name	Strength
GELATIN, UNSPECIFIED (UNII: 2G86QN327L)	 
GLYCERIN (UNII: PDC6A3C0OX)	 
SESAME OIL (UNII: QX10HYY4QV)	 
TITANIUM DIOXIDE (UNII: 15FIX9V2JP)	 
FERRIC OXIDE RED (UNII: 1K09F3G675)	 
FERRIC OXIDE YELLOW (UNII: EX438O2MRT)	 
Product Characteristics
Color	ORANGE	Score	no score
Shape	ROUND	Size	8mm
Flavor		Imprint Code	UM
Contains	    
Packaging
#	Item Code	Package Description	Marketing Start Date	Marketing End Date
1	NDC:53097-570-60	1 in 1 CARTON	05/10/2017	
1		60 in 1 BOTTLE; Type 0: Not a Combination Product		
Marketing Information
Marketing Category	Application Number or Monograph Citation	Marketing Start Date	Marketing End Date
NDA	NDA018651	05/10/2017	
Labeler - ThePharmaNetwork, LLC (939435280)
Establishment
Name	Address	ID/FEI	Business Operations
Patheon Softgels Inc		002193829	MANUFACTURE(53097-568, 53097-569, 53097-570)    
</drug_label_doc_info>
    """,
    "rld_how_supplied": """
You must generate the “RLD Section” text for the user’s specified section. The user’s data includes:
- API_name: <API_name>Dronabinol</API_name>
- dosage_form: <dosage_form>CAPSULE</dosage_form>
- route_of_administration: <route_of_administration>ORAL</route_of_administration>

**Instructions**:
1. Return a JSON with two fields: "rld_section" matching the requested name, and "research_report" containing only the final text for that snippet. 
2. If bullet points or references like “[25]” appear, preserve them. 
3. If no snippet is provided, say "No data available." 
4. Do not add extra disclaimers or mention chain-of-thought.
5. Keep it concise, formal, and scientifically oriented, exactly for the requested section.

Below is the **relevant snippet** from the drug label or context for this RLD section:
<drug_label_doc_info>
MARINOL® (dronabinol capsules, USP)

2.5 mg white capsules (Identified UM).
NDC 53097-568-60 (Bottle of 60 capsules).

5 mg dark brown capsules (Identified UM).
NDC 53097-569-60 (Bottle of 60 capsules).

10 mg orange capsules (Identified UM).
NDC 53097-570-60 (Bottle of 60 capsules).

Storage Conditions

MARINOL capsules should be packaged in a well-closed container and stored in a cool environment between 8° and 15°C (46° and 59°F) and alternatively could be stored in a refrigerator. Protect from freezing    
    """,
    "rld_physical_characteristics": """
NDC 53097-568-60
Bottle of 60 Capsules
Rx Only


marinol 2.5 mg 60 counts container Label

NDC 53097-569-60
Bottle of 60 Capsules
Rx Only


marinol-5mg

NDC 53097-570-60
Bottle of 60 Capsules
Rx Only


marinol-10mg
Close
INGREDIENTS AND APPEARANCE
MARINOL 
dronabinol capsule
Product Information
Product Type	HUMAN PRESCRIPTION DRUG	Item Code (Source)	NDC:53097-568
Route of Administration	ORAL	DEA Schedule	CIII    
Active Ingredient/Active Moiety
Ingredient Name	Basis of Strength	Strength
DRONABINOL (UNII: 7J8897W37S) (DRONABINOL - UNII:7J8897W37S)	DRONABINOL	2.5 mg
Inactive Ingredients
Ingredient Name	Strength
GELATIN, UNSPECIFIED (UNII: 2G86QN327L)	 
GLYCERIN (UNII: PDC6A3C0OX)	 
SESAME OIL (UNII: QX10HYY4QV)	 
TITANIUM DIOXIDE (UNII: 15FIX9V2JP)	 
Product Characteristics
Color	WHITE	Score	no score
Shape	ROUND	Size	8mm
Flavor		Imprint Code	UM
Contains	    
Packaging
#	Item Code	Package Description	Marketing Start Date	Marketing End Date
1	NDC:53097-568-60	1 in 1 CARTON	05/10/2017	
1		60 in 1 BOTTLE; Type 0: Not a Combination Product		
Marketing Information
Marketing Category	Application Number or Monograph Citation	Marketing Start Date	Marketing End Date
NDA	NDA018651	05/10/2017	
MARINOL 
dronabinol capsule
Product Information
Product Type	HUMAN PRESCRIPTION DRUG	Item Code (Source)	NDC:53097-569
Route of Administration	ORAL	DEA Schedule	CIII    
Active Ingredient/Active Moiety
Ingredient Name	Basis of Strength	Strength
DRONABINOL (UNII: 7J8897W37S) (DRONABINOL - UNII:7J8897W37S)	DRONABINOL	5 mg
Inactive Ingredients
Ingredient Name	Strength
GELATIN, UNSPECIFIED (UNII: 2G86QN327L)	 
GLYCERIN (UNII: PDC6A3C0OX)	 
SESAME OIL (UNII: QX10HYY4QV)	 
TITANIUM DIOXIDE (UNII: 15FIX9V2JP)	 
FERRIC OXIDE RED (UNII: 1K09F3G675)	 
FERROSOFERRIC OXIDE (UNII: XM0M87F357)	 
Product Characteristics
Color	BROWN	Score	no score
Shape	ROUND	Size	8mm
Flavor		Imprint Code	UM
Contains	    
Packaging
#	Item Code	Package Description	Marketing Start Date	Marketing End Date
1	NDC:53097-569-60	1 in 1 CARTON	05/10/2017	
1		60 in 1 BOTTLE; Type 0: Not a Combination Product		
Marketing Information
Marketing Category	Application Number or Monograph Citation	Marketing Start Date	Marketing End Date
NDA	NDA018651	05/10/2017	
MARINOL 
dronabinol capsule
Product Information
Product Type	HUMAN PRESCRIPTION DRUG	Item Code (Source)	NDC:53097-570
Route of Administration	ORAL	DEA Schedule	CIII    
Active Ingredient/Active Moiety
Ingredient Name	Basis of Strength	Strength
DRONABINOL (UNII: 7J8897W37S) (DRONABINOL - UNII:7J8897W37S)	DRONABINOL	10 mg
Inactive Ingredients
Ingredient Name	Strength
GELATIN, UNSPECIFIED (UNII: 2G86QN327L)	 
GLYCERIN (UNII: PDC6A3C0OX)	 
SESAME OIL (UNII: QX10HYY4QV)	 
TITANIUM DIOXIDE (UNII: 15FIX9V2JP)	 
FERRIC OXIDE RED (UNII: 1K09F3G675)	 
FERRIC OXIDE YELLOW (UNII: EX438O2MRT)	 
Product Characteristics
Color	ORANGE	Score	no score
Shape	ROUND	Size	8mm
Flavor		Imprint Code	UM
Contains	    
Packaging
#	Item Code	Package Description	Marketing Start Date	Marketing End Date
1	NDC:53097-570-60	1 in 1 CARTON	05/10/2017	
1		60 in 1 BOTTLE; Type 0: Not a Combination Product		
Marketing Information
Marketing Category	Application Number or Monograph Citation	Marketing Start Date	Marketing End Date
NDA	NDA018651	05/10/2017	
Labeler - ThePharmaNetwork, LLC (939435280)
Establishment
Name	Address	ID/FEI	Business Operations
Patheon Softgels Inc		002193829	MANUFACTURE(53097-568, 53097-569, 53097-570)   
</drug_label_doc_info> 
    """,
    "rld_storage_conditions": """
You must generate the “RLD Section” text for the user’s specified section. The user’s data includes:
- API_name: <API_name>Dronabinol</API_name>
- dosage_form: <dosage_form>CAPSULE</dosage_form>
- route_of_administration: <route_of_administration>ORAL</route_of_administration>

**Instructions**:
1. Return a JSON with two fields: "rld_section" matching the requested name, and "research_report" containing only the final text for that snippet. 
2. If bullet points or references like “[25]” appear, preserve them. 
3. If no snippet is provided, say "No data available." 
4. Do not add extra disclaimers or mention chain-of-thought.
5. Keep it concise, formal, and scientifically oriented, exactly for the requested section.

Below is the **relevant snippet** from the drug label or context for this RLD section:
<drug_label_doc_info>
MARINOL® (dronabinol capsules, USP)

2.5 mg white capsules (Identified UM).
NDC 53097-568-60 (Bottle of 60 capsules).

5 mg dark brown capsules (Identified UM).
NDC 53097-569-60 (Bottle of 60 capsules).

10 mg orange capsules (Identified UM).
NDC 53097-570-60 (Bottle of 60 capsules).

Storage Conditions

MARINOL capsules should be packaged in a well-closed container and stored in a cool environment between 8° and 15°C (46° and 59°F) and alternatively could be stored in a refrigerator. Protect from freezing       
</drug_label_doc_info>
    """,
    "rld_special_characteristics": """
You must generate the “RLD Section” text for the user’s specified section. The user’s data includes:
- API_name: <API_name>Dronabinol</API_name>
- dosage_form: <dosage_form>CAPSULE</dosage_form>
- route_of_administration: <route_of_administration>ORAL</route_of_administration>

**Instructions**:
1. Return a JSON with two fields: "rld_section" matching the requested name, and "research_report" containing only the final text for that snippet. 
2. If bullet points or references like “[25]” appear, preserve them. 
3. If no snippet is provided, say "No data available." 
4. Do not add extra disclaimers or mention chain-of-thought.
5. Keep it concise, formal, and scientifically oriented, exactly for the requested section.

Below is the **relevant snippet** from the drug label or context for this RLD section:
<drug_label_doc_info>
Dronabinol is a cannabinoid designated chemically as (6aR,10aR)-6a,7,8,10a-Tetrahydro-6,6,9-trimethyl-3-pentyl-6H-dibenzo[b,d]-pyran-1-ol. Dronabinol has the following empirical and structural formulas:



marinol-struct


C21H30O2 (molecular weight = 314.46)

Dronabinol, the active ingredient in MARINOL (dronabinol capsules, USP), is synthetic delta-9-tetrahydrocannabinol (delta-9-THC).

Dronabinol is a light yellow resinous oil that is sticky at room temperature and hardens upon refrigeration. Dronabinol is insoluble in water and is formulated in sesame oil. It has a pKa of 10.6 and an octanol-water partition coefficient: 6,000:1 at pH 7.

Each MARINOL capsule strength is formulated with the following inactive ingredients: 2.5 mg capsule contains gelatin, glycerin, sesame oil, and titanium dioxide; 5 mg capsule contains iron oxide red and iron oxide black, gelatin, glycerin, sesame oil, and titanium dioxide; 10 mg capsule contains iron oxide red and iron oxide yellow, gelatin, glycerin, sesame oil, and titanium dioxide.    
</drug_label_doc_info>
    """,
}

AI_MESSAGE_EXAMPLE1_RLD = {
    "API_name_with_UNII": """
Dronabinol (UNII: 7J8897W37S).
    """,
    "inactive_ingredients_with_UNII_str": """
Each Marinol® capsule strength is formulated with the following inactive ingredients: 
2.5 mg capsule contains:
Gelatin, Unspecified (UNII: 2G86QN327L)
Glycerin (UNII: PDC6A3C0OX)
Sesame Oil (UNII: QX10HYY4QV)
Titanium Dioxide (UNII: 15FIX9V2JP)
5 mg capsule contains:
Gelatin, Unspecified (UNII: 2G86QN327L)
Glycerin (UNII: PDC6A3C0OX)
Sesame Oil (UNII: QX10HYY4QV)
Ferric Oxide Red (UNII: 1K09F3G675)
Ferrosoferric Oxide (UNII: XM0M87F357)
Titanium Dioxide (UNII: 15FIX9V2JP)
10 mg capsule contains:
Gelatin, Unspecified (UNII: 2G86QN327L)
Glycerin (UNII: PDC6A3C0OX)
Sesame Oil (UNII: QX10HYY4QV)
Titanium Dioxide (UNII: 15FIX9V2JP)
Ferric Oxide Red (UNII: 1K09F3G675)
Ferric Oxide Yellow (UNII: EX438O2MRT).
    """,
    "strengths": """
2.5 mg
5 mg
10 mg 
    """,
    "type_pckg_material": """
Carton containing an amber glass bottle (with plastic cap and seal) and a package insert.    
    """,
    "rld_how_supplied": """
Marinol® (dronabinol capsules, USP) 2.5 mg: Bottle x 60 capsules (NDC 53097-571-60)
Marinol® (dronabinol capsules, USP) 5 mg: Bottle x 60 capsules (NDC 53097-572-60)
Marinol® (dronabinol capsules, USP) 10 mg: Bottle x 60 capsules (NDC 53097-573-60)    
    """,
    "rld_physical_characteristics": """
Marinol® (dronabinol capsules, USP) 2.5 mg
Color: White
Size: 8 mm
Shape: Round
Imprint code: M2
Die roll: 3 round A STD
Marinol® (dronabinol capsules, USP) 5 mg
Color: Brown
Size: 8 mm
Shape: Round
Imprint code: M5
Die roll: 3 round A STD
Marinol® (dronabinol capsules, USP) 10 mg
Color: Orange
Size: 8 mm
Shape: Round
Imprint code: MX
Die roll: 3 round A STD    
    """,
    "rld_storage_conditions": """
Store in a cool environment between 8 and 15 °C (46 and 59 °F) and alternatively store in a refrigerator. Protect from freezing.    
    """,
    "rld_special_characteristics": """
Dronabinol, the active ingredient in Marinol® (dronabinol capsules, USP), is synthetic delta-9- tetrahydrocannabinol (delta-9-THC).
Dronabinol is a light yellow resinous oil that is sticky at room temperature and hardens upon refrigeration. Dronabinol is insoluble in water and is formulated in sesame oil. It has a pKa of 10.6 and an octanol-water partition coefficient: 6,000:1 at pH 7.    
    """,
}

HUMAN_MESSAGE_EXAMPLE2_RLD = {
    "API_name_with_UNII": """
You must generate the “RLD Section” text for the user’s specified section. The user’s data includes:
- API_name: <API_name>ACETAZOLAMIDE</API_name>
- dosage_form: <dosage_form>TABLET</dosage_form>
- route_of_administration: <route_of_administration>ORAL</route_of_administration>

**Instructions**:
1. Return a JSON with two fields: "rld_section" matching the requested name, and "research_report" containing only the final text for that snippet. 
2. If bullet points or references like “[25]” appear, preserve them. 
3. If no snippet is provided, say "No data available." 
4. Do not add extra disclaimers or mention chain-of-thought.
5. Keep it concise, formal, and scientifically oriented, exactly for the requested section.

Below is the **relevant snippet** from the drug label or context for this RLD section:
<drug_label_doc_info>
NDC 51672-4023-1
100 Tablets

AcetaZOLAMIDE
Tablets USP,
250 mg

TARO

Keep this and all medications out of
the reach of children.

Rx only

PRINCIPAL DISPLAY PANEL - 250 mg Tablet Bottle Label
Close
INGREDIENTS AND APPEARANCE
ACETAZOLAMIDE 
acetazolamide tablet
Product Information
Product Type	HUMAN PRESCRIPTION DRUG	Item Code (Source)	NDC:51672-4022
Route of Administration	ORAL
Active Ingredient/Active Moiety
Ingredient Name	Basis of Strength	Strength
Acetazolamide (UNII: O3FX965V0I) (Acetazolamide - UNII:O3FX965V0I)	Acetazolamide	125 mg
Inactive Ingredients
Ingredient Name	Strength
Lactose Monohydrate (UNII: EWQ57Q8I5X)	 
Starch, Corn (UNII: O8232NY3SJ)	 
Gelatin, Unspecified (UNII: 2G86QN327L)	 
Glycerin (UNII: PDC6A3C0OX)	 
Water (UNII: 059QF0KO0R)	 
Talc (UNII: 7SEV7J4R1U)	 
Sodium Starch Glycolate Type A Potato (UNII: 5856J3G2A2)	 
Magnesium Stearate (UNII: 70097M6I30)	 
Product Characteristics
Color	WHITE	Score	2 pieces
Shape	ROUND	Size	9mm
Flavor		Imprint Code	T52
Contains	    
Packaging
#	Item Code	Package Description	Marketing Start Date	Marketing End Date
1	NDC:51672-4022-1	100 in 1 BOTTLE; Type 0: Not a Combination Product	05/28/1997	
Marketing Information
Marketing Category	Application Number or Monograph Citation	Marketing Start Date	Marketing End Date
ANDA	ANDA040195	05/28/1997	
ACETAZOLAMIDE 
acetazolamide tablet
Product Information
Product Type	HUMAN PRESCRIPTION DRUG	Item Code (Source)	NDC:51672-4023
Route of Administration	ORAL
Active Ingredient/Active Moiety
Ingredient Name	Basis of Strength	Strength
Acetazolamide (UNII: O3FX965V0I) (Acetazolamide - UNII:O3FX965V0I)	Acetazolamide	250 mg
Inactive Ingredients
Ingredient Name	Strength
Lactose Monohydrate (UNII: EWQ57Q8I5X)	 
Starch, Corn (UNII: O8232NY3SJ)	 
Gelatin, Unspecified (UNII: 2G86QN327L)	 
Glycerin (UNII: PDC6A3C0OX)	 
Water (UNII: 059QF0KO0R)	 
Talc (UNII: 7SEV7J4R1U)	 
Sodium Starch Glycolate Type A Potato (UNII: 5856J3G2A2)	 
Magnesium Stearate (UNII: 70097M6I30)	 
Product Characteristics
Color	WHITE	Score	4 pieces
Shape	ROUND	Size	11mm
Flavor		Imprint Code	T53
Contains	    
Packaging
#	Item Code	Package Description	Marketing Start Date	Marketing End Date
1	NDC:51672-4023-1	100 in 1 BOTTLE; Type 0: Not a Combination Product	05/28/1997	
Marketing Information
Marketing Category	Application Number or Monograph Citation	Marketing Start Date	Marketing End Date
ANDA	ANDA040195	05/28/1997	
Labeler - Taro Pharmaceuticals U.S.A., Inc. (145186370)
Establishment
Name	Address	ID/FEI	Business Operations
Taro Pharmaceutical Industries Ltd.		600072078	MANUFACTURE(51672-4022, 51672-4023)
</drug_label_doc_info>
    """,
    "inactive_ingredients_with_UNII_str": """
You must generate the “RLD Section” text for the user’s specified section. The user’s data includes:
- API_name: <API_name>ACETAZOLAMIDE</API_name>
- dosage_form: <dosage_form>TABLET</dosage_form>
- route_of_administration: <route_of_administration>ORAL</route_of_administration>

**Instructions**:
1. Return a JSON with two fields: "rld_section" matching the requested name, and "research_report" containing only the final text for that snippet. 
2. If bullet points or references like “[25]” appear, preserve them. 
3. If no snippet is provided, say "No data available." 
4. Do not add extra disclaimers or mention chain-of-thought.
5. Keep it concise, formal, and scientifically oriented, exactly for the requested section.

Below is the **relevant snippet** from the drug label or context for this RLD section:
<drug_label_doc_info>
NDC 51672-4023-1
100 Tablets

AcetaZOLAMIDE
Tablets USP,
250 mg

TARO

Keep this and all medications out of
the reach of children.

Rx only

PRINCIPAL DISPLAY PANEL - 250 mg Tablet Bottle Label
Close
INGREDIENTS AND APPEARANCE
ACETAZOLAMIDE 
acetazolamide tablet
Product Information
Product Type	HUMAN PRESCRIPTION DRUG	Item Code (Source)	NDC:51672-4022
Route of Administration	ORAL
Active Ingredient/Active Moiety
Ingredient Name	Basis of Strength	Strength
Acetazolamide (UNII: O3FX965V0I) (Acetazolamide - UNII:O3FX965V0I)	Acetazolamide	125 mg
Inactive Ingredients
Ingredient Name	Strength
Lactose Monohydrate (UNII: EWQ57Q8I5X)	 
Starch, Corn (UNII: O8232NY3SJ)	 
Gelatin, Unspecified (UNII: 2G86QN327L)	 
Glycerin (UNII: PDC6A3C0OX)	 
Water (UNII: 059QF0KO0R)	 
Talc (UNII: 7SEV7J4R1U)	 
Sodium Starch Glycolate Type A Potato (UNII: 5856J3G2A2)	 
Magnesium Stearate (UNII: 70097M6I30)	 
Product Characteristics
Color	WHITE	Score	2 pieces
Shape	ROUND	Size	9mm
Flavor		Imprint Code	T52
Contains	    
Packaging
#	Item Code	Package Description	Marketing Start Date	Marketing End Date
1	NDC:51672-4022-1	100 in 1 BOTTLE; Type 0: Not a Combination Product	05/28/1997	
Marketing Information
Marketing Category	Application Number or Monograph Citation	Marketing Start Date	Marketing End Date
ANDA	ANDA040195	05/28/1997	
ACETAZOLAMIDE 
acetazolamide tablet
Product Information
Product Type	HUMAN PRESCRIPTION DRUG	Item Code (Source)	NDC:51672-4023
Route of Administration	ORAL
Active Ingredient/Active Moiety
Ingredient Name	Basis of Strength	Strength
Acetazolamide (UNII: O3FX965V0I) (Acetazolamide - UNII:O3FX965V0I)	Acetazolamide	250 mg
Inactive Ingredients
Ingredient Name	Strength
Lactose Monohydrate (UNII: EWQ57Q8I5X)	 
Starch, Corn (UNII: O8232NY3SJ)	 
Gelatin, Unspecified (UNII: 2G86QN327L)	 
Glycerin (UNII: PDC6A3C0OX)	 
Water (UNII: 059QF0KO0R)	 
Talc (UNII: 7SEV7J4R1U)	 
Sodium Starch Glycolate Type A Potato (UNII: 5856J3G2A2)	 
Magnesium Stearate (UNII: 70097M6I30)	 
Product Characteristics
Color	WHITE	Score	4 pieces
Shape	ROUND	Size	11mm
Flavor		Imprint Code	T53
Contains	    
Packaging
#	Item Code	Package Description	Marketing Start Date	Marketing End Date
1	NDC:51672-4023-1	100 in 1 BOTTLE; Type 0: Not a Combination Product	05/28/1997	
Marketing Information
Marketing Category	Application Number or Monograph Citation	Marketing Start Date	Marketing End Date
ANDA	ANDA040195	05/28/1997	
Labeler - Taro Pharmaceuticals U.S.A., Inc. (145186370)
Establishment
Name	Address	ID/FEI	Business Operations
Taro Pharmaceutical Industries Ltd.		600072078	MANUFACTURE(51672-4022, 51672-4023)
</drug_label_doc_info>
    """,
    "type_pckg_material": """
You must generate the “RLD Section” text for the user’s specified section. The user’s data includes:
- API_name: <API_name>ACETAZOLAMIDE</API_name>
- dosage_form: <dosage_form>TABLET</dosage_form>
- route_of_administration: <route_of_administration>ORAL</route_of_administration>

**Instructions**:
1. Return a JSON with two fields: "rld_section" matching the requested name, and "research_report" containing only the final text for that snippet. 
2. If bullet points or references like “[25]” appear, preserve them. 
3. If no snippet is provided, say "No data available." 
4. Do not add extra disclaimers or mention chain-of-thought.
5. Keep it concise, formal, and scientifically oriented, exactly for the requested section.

Below is the **relevant snippet** from the drug label or context for this RLD section:
<drug_label_doc_info>
NDC 51672-4023-1
100 Tablets

AcetaZOLAMIDE
Tablets USP,
250 mg

TARO

Keep this and all medications out of
the reach of children.

Rx only

PRINCIPAL DISPLAY PANEL - 250 mg Tablet Bottle Label
Close
INGREDIENTS AND APPEARANCE
ACETAZOLAMIDE 
acetazolamide tablet
Product Information
Product Type	HUMAN PRESCRIPTION DRUG	Item Code (Source)	NDC:51672-4022
Route of Administration	ORAL
Active Ingredient/Active Moiety
Ingredient Name	Basis of Strength	Strength
Acetazolamide (UNII: O3FX965V0I) (Acetazolamide - UNII:O3FX965V0I)	Acetazolamide	125 mg
Inactive Ingredients
Ingredient Name	Strength
Lactose Monohydrate (UNII: EWQ57Q8I5X)	 
Starch, Corn (UNII: O8232NY3SJ)	 
Gelatin, Unspecified (UNII: 2G86QN327L)	 
Glycerin (UNII: PDC6A3C0OX)	 
Water (UNII: 059QF0KO0R)	 
Talc (UNII: 7SEV7J4R1U)	 
Sodium Starch Glycolate Type A Potato (UNII: 5856J3G2A2)	 
Magnesium Stearate (UNII: 70097M6I30)	 
Product Characteristics
Color	WHITE	Score	2 pieces
Shape	ROUND	Size	9mm
Flavor		Imprint Code	T52
Contains	    
Packaging
#	Item Code	Package Description	Marketing Start Date	Marketing End Date
1	NDC:51672-4022-1	100 in 1 BOTTLE; Type 0: Not a Combination Product	05/28/1997	
Marketing Information
Marketing Category	Application Number or Monograph Citation	Marketing Start Date	Marketing End Date
ANDA	ANDA040195	05/28/1997	
ACETAZOLAMIDE 
acetazolamide tablet
Product Information
Product Type	HUMAN PRESCRIPTION DRUG	Item Code (Source)	NDC:51672-4023
Route of Administration	ORAL
Active Ingredient/Active Moiety
Ingredient Name	Basis of Strength	Strength
Acetazolamide (UNII: O3FX965V0I) (Acetazolamide - UNII:O3FX965V0I)	Acetazolamide	250 mg
Inactive Ingredients
Ingredient Name	Strength
Lactose Monohydrate (UNII: EWQ57Q8I5X)	 
Starch, Corn (UNII: O8232NY3SJ)	 
Gelatin, Unspecified (UNII: 2G86QN327L)	 
Glycerin (UNII: PDC6A3C0OX)	 
Water (UNII: 059QF0KO0R)	 
Talc (UNII: 7SEV7J4R1U)	 
Sodium Starch Glycolate Type A Potato (UNII: 5856J3G2A2)	 
Magnesium Stearate (UNII: 70097M6I30)	 
Product Characteristics
Color	WHITE	Score	4 pieces
Shape	ROUND	Size	11mm
Flavor		Imprint Code	T53
Contains	    
Packaging
#	Item Code	Package Description	Marketing Start Date	Marketing End Date
1	NDC:51672-4023-1	100 in 1 BOTTLE; Type 0: Not a Combination Product	05/28/1997	
Marketing Information
Marketing Category	Application Number or Monograph Citation	Marketing Start Date	Marketing End Date
ANDA	ANDA040195	05/28/1997	
Labeler - Taro Pharmaceuticals U.S.A., Inc. (145186370)
Establishment
Name	Address	ID/FEI	Business Operations
Taro Pharmaceutical Industries Ltd.		600072078	MANUFACTURE(51672-4022, 51672-4023)
</drug_label_doc_info>
    """,
    "rld_how_supplied": """
You must generate the “RLD Section” text for the user’s specified section. The user’s data includes:
- API_name: <API_name>ACETAZOLAMIDE</API_name>
- dosage_form: <dosage_form>TABLET</dosage_form>
- route_of_administration: <route_of_administration>ORAL</route_of_administration>

**Instructions**:
1. Return a JSON with two fields: "rld_section" matching the requested name, and "research_report" containing only the final text for that snippet. 
2. If bullet points or references like “[25]” appear, preserve them. 
3. If no snippet is provided, say "No data available." 
4. Do not add extra disclaimers or mention chain-of-thought.
5. Keep it concise, formal, and scientifically oriented, exactly for the requested section.

Below is the **relevant snippet** from the drug label or context for this RLD section:
<drug_label_doc_info>
Acetazolamide Tablets USP are supplied as follows:
125 mg - White, round, scored in half, on one side, "T52" engraved on the other side.
NDC 51672-4022-1 - Bottle of 100

250 mg - White, round, scored in quarters, on one side, "T53" engraved on the other side.
NDC 51672-4023-1 - Bottle of 100

Store at 20° to 25°C (68° to 77°F) [see USP Controlled Room Temperature].
</drug_label_doc_info>
    """,
    "rld_physical_characteristics": """
You must generate the “RLD Section” text for the user’s specified section. The user’s data includes:
- API_name: <API_name>ACETAZOLAMIDE</API_name>
- dosage_form: <dosage_form>TABLET</dosage_form>
- route_of_administration: <route_of_administration>ORAL</route_of_administration>

**Instructions**:
1. Return a JSON with two fields: "rld_section" matching the requested name, and "research_report" containing only the final text for that snippet. 
2. If bullet points or references like “[25]” appear, preserve them. 
3. If no snippet is provided, say "No data available." 
4. Do not add extra disclaimers or mention chain-of-thought.
5. Keep it concise, formal, and scientifically oriented, exactly for the requested section.

Below is the **relevant snippet** from the drug label or context for this RLD section:
<drug_label_doc_info>
NDC 51672-4023-1
100 Tablets

AcetaZOLAMIDE
Tablets USP,
250 mg

TARO

Keep this and all medications out of
the reach of children.

Rx only

PRINCIPAL DISPLAY PANEL - 250 mg Tablet Bottle Label
Close
INGREDIENTS AND APPEARANCE
ACETAZOLAMIDE 
acetazolamide tablet
Product Information
Product Type	HUMAN PRESCRIPTION DRUG	Item Code (Source)	NDC:51672-4022
Route of Administration	ORAL
Active Ingredient/Active Moiety
Ingredient Name	Basis of Strength	Strength
Acetazolamide (UNII: O3FX965V0I) (Acetazolamide - UNII:O3FX965V0I)	Acetazolamide	125 mg
Inactive Ingredients
Ingredient Name	Strength
Lactose Monohydrate (UNII: EWQ57Q8I5X)	 
Starch, Corn (UNII: O8232NY3SJ)	 
Gelatin, Unspecified (UNII: 2G86QN327L)	 
Glycerin (UNII: PDC6A3C0OX)	 
Water (UNII: 059QF0KO0R)	 
Talc (UNII: 7SEV7J4R1U)	 
Sodium Starch Glycolate Type A Potato (UNII: 5856J3G2A2)	 
Magnesium Stearate (UNII: 70097M6I30)	 
Product Characteristics
Color	WHITE	Score	2 pieces
Shape	ROUND	Size	9mm
Flavor		Imprint Code	T52
Contains	    
Packaging
#	Item Code	Package Description	Marketing Start Date	Marketing End Date
1	NDC:51672-4022-1	100 in 1 BOTTLE; Type 0: Not a Combination Product	05/28/1997	
Marketing Information
Marketing Category	Application Number or Monograph Citation	Marketing Start Date	Marketing End Date
ANDA	ANDA040195	05/28/1997	
ACETAZOLAMIDE 
acetazolamide tablet
Product Information
Product Type	HUMAN PRESCRIPTION DRUG	Item Code (Source)	NDC:51672-4023
Route of Administration	ORAL
Active Ingredient/Active Moiety
Ingredient Name	Basis of Strength	Strength
Acetazolamide (UNII: O3FX965V0I) (Acetazolamide - UNII:O3FX965V0I)	Acetazolamide	250 mg
Inactive Ingredients
Ingredient Name	Strength
Lactose Monohydrate (UNII: EWQ57Q8I5X)	 
Starch, Corn (UNII: O8232NY3SJ)	 
Gelatin, Unspecified (UNII: 2G86QN327L)	 
Glycerin (UNII: PDC6A3C0OX)	 
Water (UNII: 059QF0KO0R)	 
Talc (UNII: 7SEV7J4R1U)	 
Sodium Starch Glycolate Type A Potato (UNII: 5856J3G2A2)	 
Magnesium Stearate (UNII: 70097M6I30)	 
Product Characteristics
Color	WHITE	Score	4 pieces
Shape	ROUND	Size	11mm
Flavor		Imprint Code	T53
Contains	    
Packaging
#	Item Code	Package Description	Marketing Start Date	Marketing End Date
1	NDC:51672-4023-1	100 in 1 BOTTLE; Type 0: Not a Combination Product	05/28/1997	
Marketing Information
Marketing Category	Application Number or Monograph Citation	Marketing Start Date	Marketing End Date
ANDA	ANDA040195	05/28/1997	
Labeler - Taro Pharmaceuticals U.S.A., Inc. (145186370)
Establishment
Name	Address	ID/FEI	Business Operations
Taro Pharmaceutical Industries Ltd.		600072078	MANUFACTURE(51672-4022, 51672-4023)
</drug_label_doc_info>

    """,
    "rld_storage_conditions": """
You must generate the “RLD Section” text for the user’s specified section. The user’s data includes:
- API_name: <API_name>ACETAZOLAMIDE</API_name>
- dosage_form: <dosage_form>TABLET</dosage_form>
- route_of_administration: <route_of_administration>ORAL</route_of_administration>

**Instructions**:
1. Return a JSON with two fields: "rld_section" matching the requested name, and "research_report" containing only the final text for that snippet. 
2. If bullet points or references like “[25]” appear, preserve them. 
3. If no snippet is provided, say "No data available." 
4. Do not add extra disclaimers or mention chain-of-thought.
5. Keep it concise, formal, and scientifically oriented, exactly for the requested section.

Below is the **relevant snippet** from the drug label or context for this RLD section:
<drug_label_doc_info>
Acetazolamide Tablets USP are supplie
d as follows:
125 mg - White, round, scored in half, on one side, "T52" engraved on the other side.
NDC 51672-4022-1 - Bottle of 100

250 mg - White, round, scored in quarters, on one side, "T53" engraved on the other side.
NDC 51672-4023-1 - Bottle of 100

Store at 20° to 25°C (68° to 77°F) [see USP Controlled Room Temperature].
</drug_label_doc_info>
    """,
    "rld_special_characteristics": """
You must generate the “RLD Section” text for the user’s specified section. The user’s data includes:
- API_name: <API_name>ACETAZOLAMIDE</API_name>
- dosage_form: <dosage_form>TABLET</dosage_form>
- route_of_administration: <route_of_administration>ORAL</route_of_administration>

**Instructions**:
1. Return a JSON with two fields: "rld_section" matching the requested name, and "research_report" containing only the final text for that snippet. 
2. If bullet points or references like “[25]” appear, preserve them. 
3. If no snippet is provided, say "No data available." 
4. Do not add extra disclaimers or mention chain-of-thought.
5. Keep it concise, formal, and scientifically oriented, exactly for the requested section.

Below is the **relevant snippet** from the drug label or context for this RLD section:
<drug_label_doc_info>
Acetazolamide, an inhibitor of the enzyme carbonic anhydrase, is a white to faintly yellowish white crystalline, odorless powder, weakly acidic, very slightly soluble in water and slightly soluble in alcohol. The chemical name for acetazolamide is N-(5-Sulfamoyl-1,3,4-thiadiazol-2-yl)-acetamide and has the following chemical structure:

Chemical Structure

Molecular Weight: 222.25

Molecular Formula: C4H6N4O3S2

Acetazolamide is available as oral tablets containing 125 mg and 250 mg of acetazolamide, respectively, and the following inactive ingredients: corn starch, gelatin, glycerin, lactose monohydrate, magnesium stearate, purified water, sodium starch glycolate and talc.
</drug_label_doc_info>
    """
}

AI_MESSAGE_EXAMPLE2_RLD = {
    "API_name_with_UNII": "Acetazolamide (UNII: O3FX965V0I)",
    "inactive_ingredients_with_UNII_str": """
Lactose Monohydrate (UNII: EWQ57Q8I5X)
Starch, Corn (UNII: O8232NY3SJ)
Gelatin, Unspecified (UNII: 2G86QN327L)
Glycerin (UNII: PDC6A3C0OX)
Water (UNII: 059QF0KO0R)
Talc (UNII: 7SEV7J4R1U)
Sodium Starch Glycolate Type A Potato (UNII: 5856J3G2A2)
Magnesium Stearate (UNII: 70097M6I30)
    """,
    "type_pckg_material": """
Plastic bottle with a package insert.
    """,
    "rld_how_supplied": """
Acetazolamide Tablets USP 125 mg: Bottle x 100 tablets (NDC 51672-4022-1)
Acetazolamide Tablets USP 250 mg: Bottle x 100 tablets (NDC 51672-4023-1)
    """,
    "rld_physical_characteristics": """
Acetazolamide Tablets USP 125 mg:
Color: White
Size: 9 mm
Shape: Round
Score/Imprint code: Scored in half, on one side, "T52" engraved on the other side.
Acetazolamide Tablets USP 250 mg:
Color: White
Size: 9 mm
Shape: Round
Score/Imprint code: Scored in quarters, on one side, "T53" engraved on the other side.
    """,
    "rld_storage_conditions": """
Store at 20° to 25°C (68° to 77°F).
    """,
    "rld_special_characteristics": """
Acetazolamide Tablets, USP from Pharmaceutical Industries Ltd. contain gelatin and glycerin. Gelatin has been used as a binder and a coating agent while Glycerin has been used as a solvent and binding enhancer in tablet manufacturing. The function of both excipients in the formulation must be studied.
    """
}

@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the chatbot."""
    gpt4o: str = "gpt-4o"
    gpt4omini: str = "gpt-4o-mini"
    o3mini: str = "o3-mini"
    claude_35_sonnet: str = "claude-3-5-sonnet-latest"
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY")
    local_orange_book_zip_path: str = r"C:\Users\Ivan\OneDrive - Grupo Procaps\Portafolio NTF\16 - I&D 4.0\2. Investigación de Literatura - Degradación de APIs\1.2 MVP\drug development researcher\databases\orange_book_database.zip"
    number_of_queries: int = 9
    max_results_query: int = 5
    max_tokens_per_source: int = 1000
    language_for_extraction: str = "english"
    language_for_report: str = "english"
    # Use default_factory for mutable dict fields
    HUMAN_MESSAGE_EXAMPLE1_RLD: Dict = field(default_factory=lambda: HUMAN_MESSAGE_EXAMPLE1_RLD)
    AI_MESSAGE_EXAMPLE1_RLD: Dict = field(default_factory=lambda: AI_MESSAGE_EXAMPLE1_RLD)
    HUMAN_MESSAGE_EXAMPLE2_RLD: Dict = field(default_factory=lambda: HUMAN_MESSAGE_EXAMPLE2_RLD)
    AI_MESSAGE_EXAMPLE2_RLD: Dict = field(default_factory=lambda: AI_MESSAGE_EXAMPLE2_RLD)
    MAPPING_DRUG_LABEL_SECTION: Dict = field(default_factory=lambda: MAPPING_DRUG_LABEL_SECTION)
    SECTIONCODE_MAP: Dict = field(default_factory=lambda: SECTIONCODE_MAP)
    
    @classmethod
    def from_runnable_config(cls, config):
        """Convierte un RunnableConfig en una instancia de Configuration"""
        configurable = config.configurable if hasattr(config, "configurable") else {}
        return cls(**configurable)