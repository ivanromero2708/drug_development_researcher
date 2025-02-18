from pydantic import BaseModel, Field
from typing import List, TypedDict, Annotated, Optional
import operator

from typing import List, Literal
from pydantic import BaseModel, Field
from langgraph.channels.last_value import LastValue

class RLD(BaseModel):
    api_name: str = Field(..., description= "The name of the active ingredient for the reference list drug product")
    brand_name: str = Field(..., description= "The brand name for the reference list drug product")
    rld_dosage_form: str = Field(..., description="The dosage form of the reference list drug product.")
    manufacturer: str = Field(..., description= "The manufacturer of the reference list drug product")
    route_of_administration: str = Field(..., description= "The route of administration of the reference list drug product")

class RLDReportSection(BaseModel):
    rld_section: Literal[
        "API_name_with_UNII",
        "inactive_ingredients_with_UNII_str",
        "type_pckg_material",
        "rld_how_supplied",
        "rld_physical_characteristics",
        "rld_storage_conditions",
        "rld_special_characteristics",
        "strengths",        
        ] = Field(
        ...,
        description = "The name of the specific rld report element of the Active Ingredient exposed in the research report"
    )
    research_report: str = Field(
        ...,
        description="A plain text research report of the given information in a highly pharmaceutical chemist scientific, detailed and exhaustive style."
    )

# Add Tavily's arguments to enhance the web search tool's capabilities
class TavilyQuery(BaseModel):
    query: str = Field(description="web search query")

# Define the args_schema for the tavily_search tool using a multi-query approach, enabling more precise queries for Tavily.
class TavilySearchInput(BaseModel):
    sub_queries: List[TavilyQuery] = Field(description="set of sub-queries that can be answered in isolation")

# Data from API research task
class APILiteratureResearchData(BaseModel):
    api_name: str = Field(
        ...,
        description= "The name of the API."
    )
    cas_number: Optional[str] = Field(
        ...,
        description="CAS number in XXXX-XX-X format",
    )
    pka: Optional[str] = Field(
        ...,
        description = "The pKa or dissociation constant for the API. pKa is the negative logarithm of the acid dissociation constant (Ka) of a compound, representing the pH at which half of the compound is ionized. It indicates the strength of an acid: lower pKa values correspond to stronger acids, while higher values indicate weaker acids."
    )
    stability: Optional[str] = Field(
        ..., 
        description = "The stability storage conditions for the API. Stability Conditions refer to the specific environmental parameters under which an Active Pharmaceutical Ingredient (API) or drug product maintains its chemical, physical, microbiological, and therapeutic integrity over time. These conditions typically include temperature, humidity, light exposure, and packaging requirements to prevent degradation and ensure efficacy and safety."
    )
    description: str = Field(
        ...,
        description="Physical description with bullet points"
    )
    solubility: str = Field(
        ...,
        description="Solubility in various solvents"
    )
    melting_point: str = Field(
        ...,
        description="Melting point in 'value ± deviation °C' format",
    )
    chemical_names: str = Field(
        ...,
        description="IUPAC name of compound",
    )
    molecular_formula: str = Field(
        ...,
        description="Molecular formula in Hill notation",
    )
    molecular_weight: Optional[float] = Field(
        ...,
        description="Molecular weight in g/mol",
    )
    log_p: str = Field(
        ...,
        description="Octanol-water partition coefficient",
    )
    boiling_point: str = Field(
        ...,
        description="Boiling point in 'value °C at pressure'",
    )
    polymorphs: str = Field(
        ...,
        description="Complete text with references in a scientific and research article style from the Detailed description of polymorphic forms of the active substance identified in the literature. It includes the url link as reference"
    )
    scheme_of_degradation_route: str = Field(
        ...,
        description="Complete text with references in a scientific and research article style Detailed scheme of degradation routes based on literature and DMF sources. It includes the url link as reference"
    )
    stability_indicators: str = Field(
        ...,
        description="Complete text with references in a scientific and research article style Key stability indicators obtained from the literature and DMF. It includes the url link as reference"
    )
    impurities: str = Field(
        ...,
        description="Complete text with references in a scientific and research article style Information on relevant impurities derived from the literature, DMF, and USP Monograph, if applicable. It includes the url link as reference"
    )
    biopharmaceutical_classification: str = Field(
        ...,
        description=" Complete text with references in a scientific and research article style Biopharmaceutical classification based on physicochemical properties and permeability. It includes the url link as reference"
    )
    hygroscopicity: str = Field(
        ...,
        description="Complete text with references in a scientific and research article style Data on hygroscopicity. It includes the url link as reference"
    )
    chirality_or_specific_optical_rotation: str = Field(
        ...,
        description="Complete text with references in a scientific and research article style Information on chirality or specific optical rotation obtained from DMF and other literary sources. It includes the url link as reference"
    )
    glass_transition_temperature: str = Field(
        ...,
        description="Complete text with references in a scientific and research article style Glass transition temperature based on available studies in the literature. It includes the url link as reference"
    )
    degradation_temperature: str = Field(
        ...,
        description="Complete text with references in a scientific and research article style Degradation temperature identified in the literature. It includes the url link as reference"
    )

# Data from RLD research task
class RLDResearchData(BaseModel):
    API_name_with_UNII: str = Field(
        ...,
        description = "The name of the active pharmaceutical ingredient (API) along with its Unique Ingredient Identifier (UNII). For example, “Acetazolamide (UNII: O3FX965V0I)”. This helps clearly identify the exact chemical substance used in the reference listed drug."
    )
    inactive_ingredients_with_UNII_str: str = Field(
        ...,
        description = "A list or description of the inactive ingredients (excipients) in the RLD, each accompanied by its UNII (or other relevant identifier). For example, lactose monohydrate, starch, gelatin, etc. This section focuses on the excipients’ identity and regulatory references."
    )
    type_pckg_material: str = Field(
        ...,
        description = "The packaging material or container system used for the RLD, such as amber glass bottles, plastic bottles, blister packs, and so forth. This indicates how the product is presented commercially and what material is used to store or protect it."
    )
    rld_how_supplied: str = Field(
        ...,
        description = "The product’s commercial presentations and packaging details (e.g., number of tablets per bottle, NDC codes, package inserts). It often includes official references for how the product is supplied in the market."
    )
    rld_physical_characteristics: str = Field(
        ...,
        description = "Definition: The color, size, shape, imprint codes, scoring, or other visual/physical traits of the finished dosage form (e.g., “white, round, 9 mm, T53 engraved”)."
    )
    rld_special_characteristics: str = Field(
        ...,
        description = "Any special considerations or distinctive aspects of the RLD—such as the crystalline form used, particle size, unusual manufacturing steps, or advanced formulation technologies. Often highlights unique attributes of the API/excipients."
    )
    rld_storage_conditions: str = Field(..., description="The storage conditions for the rld product")
    strengths: str = Field(..., description="The strengths for the rld product")
    brand_name: str = Field(..., description="The brand name for the reference list drug")
    manufacturer: str = Field(..., description="The manufacturer for the reference list drug")















class APILiteratureData(BaseModel):
    api_name: str = Field(
        ...,
        description= "The name of the API."
    )
    cas_number: Optional[str] = Field(
        ...,
        description="CAS number in XXXX-XX-X format",
    )
    pka: Optional[str] = Field(
        ...,
        description = "The pKa or dissociation constant for the API. pKa is the negative logarithm of the acid dissociation constant (Ka) of a compound, representing the pH at which half of the compound is ionized. It indicates the strength of an acid: lower pKa values correspond to stronger acids, while higher values indicate weaker acids."
    )
    stability: Optional[str] = Field(
        ..., 
        description = "The stability storage conditions for the API. Stability Conditions refer to the specific environmental parameters under which an Active Pharmaceutical Ingredient (API) or drug product maintains its chemical, physical, microbiological, and therapeutic integrity over time. These conditions typically include temperature, humidity, light exposure, and packaging requirements to prevent degradation and ensure efficacy and safety."
    )
    description: str = Field(
        ...,
        description="Physical description with bullet points"
    )
    solubility: str = Field(
        ...,
        description="Solubility in various solvents"
    )
    melting_point: str = Field(
        ...,
        description="Melting point in 'value ± deviation °C' format",
    )
    chemical_names: str = Field(
        ...,
        description="IUPAC name of compound",
    )
    molecular_formula: str = Field(
        ...,
        description="Molecular formula in Hill notation",
    )
    molecular_weight: Optional[float] = Field(
        ...,
        description="Molecular weight in g/mol",
    )
    log_p: str = Field(
        ...,
        description="Octanol-water partition coefficient",
    )
    boiling_point: str = Field(
        ...,
        description="Boiling point in 'value °C at pressure'",
    )
    polymorphs: str = Field(
        ...,
        description="Complete text with references in a scientific and research article style from the Detailed description of polymorphic forms of the active substance identified in the literature. It includes the url link as reference"
    )
    scheme_of_degradation_route: str = Field(
        ...,
        description="Complete text with references in a scientific and research article style Detailed scheme of degradation routes based on literature and DMF sources. It includes the url link as reference"
    )
    stability_indicators: str = Field(
        ...,
        description="Complete text with references in a scientific and research article style Key stability indicators obtained from the literature and DMF. It includes the url link as reference"
    )
    impurities: str = Field(
        ...,
        description="Complete text with references in a scientific and research article style Information on relevant impurities derived from the literature, DMF, and USP Monograph, if applicable. It includes the url link as reference"
    )
    biopharmaceutical_classification: str = Field(
        ...,
        description=" Complete text with references in a scientific and research article style Biopharmaceutical classification based on physicochemical properties and permeability. It includes the url link as reference"
    )
    hygroscopicity: str = Field(
        ...,
        description="Complete text with references in a scientific and research article style Data on hygroscopicity. It includes the url link as reference"
    )
    chirality_or_specific_optical_rotation: str = Field(
        ...,
        description="Complete text with references in a scientific and research article style Information on chirality or specific optical rotation obtained from DMF and other literary sources. It includes the url link as reference"
    )
    glass_transition_temperature: str = Field(
        ...,
        description="Complete text with references in a scientific and research article style Glass transition temperature based on available studies in the literature. It includes the url link as reference"
    )
    degradation_temperature: str = Field(
        ...,
        description="Complete text with references in a scientific and research article style Degradation temperature identified in the literature. It includes the url link as reference"
    )
    API_name_with_UNII: str = Field(
        ...,
        description = "The name of the active pharmaceutical ingredient (API) along with its Unique Ingredient Identifier (UNII). For example, “Acetazolamide (UNII: O3FX965V0I)”. This helps clearly identify the exact chemical substance used in the reference listed drug."
    )
    inactive_ingredients_with_UNII_str: str = Field(
        ...,
        description = "A list or description of the inactive ingredients (excipients) in the RLD, each accompanied by its UNII (or other relevant identifier). For example, lactose monohydrate, starch, gelatin, etc. This section focuses on the excipients’ identity and regulatory references."
    )
    type_pckg_material: str = Field(
        ...,
        description = "The packaging material or container system used for the RLD, such as amber glass bottles, plastic bottles, blister packs, and so forth. This indicates how the product is presented commercially and what material is used to store or protect it."
    )
    rld_how_supplied: str = Field(
        ...,
        description = "The product’s commercial presentations and packaging details (e.g., number of tablets per bottle, NDC codes, package inserts). It often includes official references for how the product is supplied in the market."
    )
    rld_physical_characteristics: str = Field(
        ...,
        description = "Definition: The color, size, shape, imprint codes, scoring, or other visual/physical traits of the finished dosage form (e.g., “white, round, 9 mm, T53 engraved”)."
    )
    rld_special_characteristics: str = Field(
        ...,
        description = "Any special considerations or distinctive aspects of the RLD—such as the crystalline form used, particle size, unusual manufacturing steps, or advanced formulation technologies. Often highlights unique attributes of the API/excipients."
    )
    rld_storage_conditions: str = Field(..., description="The storage conditions for the rld product")
    strengths: str = Field(..., description="The strengths for the rld product")
    brand_name: str = Field(..., description="The brand name for the reference list drug")
    manufacturer: str = Field(..., description="The manufacturer for the reference list drug")

class APIsLiteratureData(BaseModel):
    apis_literature_data: List[APILiteratureData]

class API(BaseModel):
    API_name: str = Field(
        ...,
        description="The name of the pharmaceutical active ingredient."
    )
    route_of_administration: str = Field(
        ...,
        description="The route of administration of the pharmaceutical active ingredient."
    )
    desired_dosage_form: Literal[
        "AEROSOL, FOAM",
        "AEROSOL, METERED",
        "AEROSOL",
        "BAR, CHEWABLE",
        "CAPSULE, COATED PELLETS",
        "CAPSULE, DELAYED REL PELLETS, TABLET",
        "CAPSULE, DELAYED REL PELLETS",
        "CAPSULE, DELAYED RELEASE",
        "CAPSULE, EXTENDED RELEASE",
        "CAPSULE, PELLET",
        "CAPSULE, PELLETS",
        "CAPSULE, TABLET, CAPSULE, DELAYED REL PELLETS",
        "CAPSULE, TABLET, CAPSULE, DELAYED RELEASE",
        "CAPSULE, TABLET, TABLET",
        "CAPSULE, TABLET",
        "CAPSULE",
        "CLOTH",
        "CONCENTRATE",
        "CREAM, AUGMENTED",
        "CREAM, INSERT",
        "CREAM, SUPPOSITORY",
        "CREAM, TABLET",
        "CREAM",
        "DISC",
        "DRESSING",
        "DRUG-ELUTING CONTACT LENS",
        "ELIXIR",
        "EMULSION",
        "ENEMA",
        "FIBER, EXTENDED RELEASE",
        "FILM, EXTENDED RELEASE",
        "FILM",
        "FOAM",
        "FOR SOLUTION, TABLET, DELAYED RELEASE",
        "FOR SOLUTION, TABLET, FOR SOLUTION",
        "FOR SOLUTION",
        "FOR SUSPENSION, DELAYED RELEASE",
        "FOR SUSPENSION, EXTENDED RELEASE",
        "FOR SUSPENSION, TABLET",
        "FOR SUSPENSION",
        "GAS",
        "GEL, AUGMENTED",
        "GEL, METERED",
        "GEL",
        "GRANULE, DELAYED RELEASE",
        "GRANULE, EFFERVESCENT",
        "GRANULE",
        "GRANULES, EXTENDED RELEASE",
        "GRANULES",
        "GUM, CHEWING",
        "IMPLANT",
        "INHALANT",
        "INJECTABLE, LIPID COMPLEX",
        "INJECTABLE, LIPOSOMAL",
        "INJECTABLE, SUSPENSION",
        "INJECTABLE, TABLET",
        "INJECTABLE",
        "INSERT, EXTENDED RELEASE",
        "INSERT",
        "INTRAUTERINE DEVICE",
        "JELLY",
        "LIQUID",
        "LOTION, AUGMENTED",
        "LOTION/SHAMPOO",
        "LOTION",
        "OIL/DROPS",
        "OIL",
        "OINTMENT, AUGMENTED",
        "OINTMENT",
        "PASTE",
        "PASTILLE",
        "PATCH",
        "PELLET",
        "PELLETS",
        "POWDER, EXTENDED RELEASE",
        "POWDER, METERED",
        "POWDER",
        "RING",
        "SHAMPOO",
        "SOAP",
        "SOLUTION FOR SLUSH",
        "SOLUTION, ELIXIR",
        "SOLUTION, EXTENDED RELEASE",
        "SOLUTION, GEL FORMING/DROPS",
        "SOLUTION, METERED",
        "SOLUTION/DROPS",
        "SOLUTION",
        "SPONGE",
        "SPRAY, METERED",
        "SPRAY",
        "SUPPOSITORY",
        "SUSPENSION, EXTENDED RELEASE",
        "SUSPENSION, LIPOSOMAL",
        "SUSPENSION/DROPS",
        "SUSPENSION",
        "SWAB",
        "SYRUP",
        "SYSTEM, EXTENDED RELEASE",
        "SYSTEM",
        "TABLET, CHEWABLE, TABLET, CAPSULE",
        "TABLET, CHEWABLE, TABLET",
        "TABLET, CHEWABLE",
        "TABLET, COATED PARTICLES",
        "TABLET, DELAYED RELEASE",
        "TABLET, DISPERSIBLE",
        "TABLET, EFFERVESCENT",
        "TABLET, EXTENDED RELEASE, CHEWABLE",
        "TABLET, EXTENDED RELEASE",
        "TABLET, FOR SUSPENSION",
        "TABLET, ORALLY DISINTEGRATING, DELAYED RELEASE",
        "TABLET, ORALLY DISINTEGRATING, EXTENDED RELEASE",
        "TABLET, ORALLY DISINTEGRATING",
        "TABLET",
        "TAMPON",
        "TAPE",
        "TROCHE/LOZENGE"
    ] = Field(
        ...,
        description="The desired dosage form for that particular API in the product."
    )

class APIs(BaseModel):
    list_apis: List[API] = Field(
        ...,
        description="The structured information for the given APIs including the name, and the desired dosage form"
    )

# Define Input product information
class ProductInformation(BaseModel):
    """The information of the pharmaceutical product to be developed"""
    product_name: str = Field(
        ...,
        description="The pharmaceutical product name that includes the Active Pharmaceutical Ingredients, and the pharmaceutical dosage form. For example: ´´´Dronabinol + Acetazolamide Unigel´´´, OR ´´´Vonoprazan Tablets´´´"
    )
    product_type: str = Field(
        ...,
        description="The pharmaceutical product type that could be one of these: OTC, RX, Nutraceutic, Cosmetic, others"
    )
    generic_name: str = Field(
        ...,
        description="The name of a generic or brand product with the desired API"
    )    
    product_strength: str = Field(
        ...,
        description="The name of the APIs included in the product with their respective strengths. For example: ´´´Dronabinol 2.5 mg + Acetazolamide 125 mg Unigel; Dronabinol 5 mg + Acetazolamide 250 mg Unigel´´´"
    )
    product_dosage_form: str = Field(
        ...,
        description="The pharmaceutical product dosage form, that could be: tablets, softgels, unigels, syrups, among others"
    )
    route_of_administration: str = Field(
        ...,
        description="The pharmaceutical product route of administration, that includes: oral, topic, nasal, intragastric, vaginal, among others"
    )
    product_dose: str = Field(
        ...,
        description= "The desired product dose. If not available, could be replaced by a message indicating ´´´According to physician's prescription´´´"
    )
    physical_characteristics: str = Field(
        ...,
        description= "Color, shape, form or printing desired in the final version of the product"
    )
    packaging_type: str = Field(
        ...,
        description= "Desired secondary packaging specifications"
    )
    commercial_presentations: str = Field(
        ...,
        description= """The desired commercial presentation of the pharmaceutical product. It could be something like: ´´´Blister packs x 28 capsules´´´, ´´´VONOPRAZAM 10 mg TAB  CAJA X 30 und CIAL, VONOPRAZAM 20 mg TAB  CAJA X 30 und CIAL, 
        VONOPRAZAM 10 mg TAB  CAJA X 5 und MM, VONOPRAZAM 20 mg TAB  CAJA X 5 und MM ´´´"""
    )
    required_expiration_time: str = Field(
        ...,
        description = """Required expiration time for the pharmaceutical product to be developed in months or years."""
    )
    observations: str = Field(
        ...,
        description= "Additional observations for the pharmaceutical product to be developed"
    )

class PropertyReportSection(BaseModel):
    property: Literal["polymorphs", "scheme_of_degradation_route", "stability_indicators", "impurities", "biopharmaceutical_classification", "hygroscopicity", "chirality_or_specific_optical_rotation", "glass_transition_temperature", "degradation_temperature"] = Field(
        ...,
        description = "The name of the specific physicochemical property of the Active Ingredient exposed in the research report"
    )
    research_report: str = Field(
        ...,
        description="A 100 words plain text research report of the given physicochemical property in a highly pharmaceutical chemist scientific, detailed and exhaustive style."
    )

class DrugDevelopmentResearchGraphState(TypedDict):
    input_documents: List[str]
    apis_text_information: str
    apis: List[API]
    product_information: ProductInformation
    is_rld_combination: Literal["Y", "N"]
    is_supplement: Literal["Y", "N"]
    
    literature_research_api_data: Annotated[List[APILiteratureResearchData], operator.add]
    
    RLDs: List[RLD]
    rld_research_data: Annotated[List[RLDResearchData], operator.add]
   
    
    patent_background_restrictions:str
#    api_monographs: List[APIMonograph]
#    drug_product_monographs: List[DrugProductMonograph]
    rld_packaging_descriptions: str
#    ingredients_iig: List[IngredientsIIG]
#    api_data_external_apis: List[APIExternalData]
    context_for_tpl: dict
    report_docx_dir_string: str
