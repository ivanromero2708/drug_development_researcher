from pydantic import BaseModel, Field
from typing import List, TypedDict, Annotated, Optional
import operator

from typing import List, Literal
from pydantic import BaseModel, Field
from langgraph.channels.last_value import LastValue


# Add Tavily's arguments to enhance the web search tool's capabilities
class TavilyQuery(BaseModel):
    query: str = Field(description="web search query")

# Define the args_schema for the tavily_search tool using a multi-query approach, enabling more precise queries for Tavily.
class TavilySearchInput(BaseModel):
    sub_queries: List[TavilyQuery] = Field(description="set of sub-queries that can be answered in isolation")

class APILiteratureData(BaseModel):
    api_name: str = Field(
        ...,
        description= "The name of the API."
    )
    cas_number: Optional[str] = Field(
        ...,
        description="CAS number in XXXX-XX-X format",
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
    rld_special_characteristics: str = Field(
        ...,
        description="Complete text with references in a scientific and research article style Special characteristics of the API and excipients for the RLD, such as crystalline form or particle size, based on COFA and literature. It includes the url link as reference"
    )
    rld_manufacturing_process_info: str = Field(
        ...,
        description="Complete text with references in a scientific and research article style Manufacturing process information for the RLD, including controls and recommended conditions, obtained from sources like LiteratureResearchAgent, PatentResearchAgent, and EMA API. It includes the url link as reference"
    )

class APIsLiteratureData(BaseModel):
    apis_literature_data: List[APILiteratureData]

class ReportSection(BaseModel):
    name: str = Field(
        description="Name for this section of the report.",
    )
    description: str = Field(
        description="Brief overview of the main topics and concepts to be covered in this section.",
    )
    content: str = Field(
        description="The content of the section."
    )   

# Define the structure for clustering output
class DocumentCluster(BaseModel):
    property: Literal[
        'polymorphs',
        'scheme_of_degradation_route',
        'stability_indicators',
        'impurities',
        'biopharmaceutical_classification',
        'hygroscopicity',
        'chirality_or_specific_optical_rotation',
        'glass_transition_temperature',
        'degradation_temperature',
        'rld_special_characteristics',
        'rld_manufacturing_process_info'
    ] = Field(
        ...,
        description="The name of the property these documents belong to."
    )
    cluster: List[str] = Field(
        ...,
        description="A list of URLs relevant to the identified property."
    )

class DocumentClusters(BaseModel):
    clusters: List[DocumentCluster] = Field(default_factory=list, description="List of document clusters")

class API(BaseModel):
    API_name: str = Field(
        ...,
        description="The name of the pharmaceutical active ingredient."
    )

# Define Input product information
class ProductInformation(BaseModel):
    """The information of the pharmaceutical product to be developed"""
    APIs: List[API] = Field(
        ...,
        description="The list of the pharmaceutical active ingredient names"
    )
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

class DrugDevelopmentResearchInputState(TypedDict):
    input_documents: List[str]                                          # List of input documents SOW, DMI, DMF, among others

class DrugDevelopmentResearchOutputState(TypedDict):
    report_docx_dir_string: str                                              # Dir string for the research report

class DrugDevelopmentResearchGraphState(TypedDict):
    input_documents: List[str]
    apis: List[API]
    product_information: ProductInformation
    api_literature_data: Annotated[List[APILiteratureData], operator.add]
    patent_background_restrictions:str
#    api_monographs: List[APIMonograph]
#    drug_product_monographs: List[DrugProductMonograph]
    rld_packaging_descriptions: str
#    ingredients_iig: List[IngredientsIIG]
#    api_data_external_apis: List[APIExternalData]
    context_for_tpl: dict
    report_docx_dir_string: str
