from langgraph.graph import add_messages
from langchain_core.messages import AnyMessage
from . import TavilySearchInput, DocumentCluster, ReportEvaluation
from typing import TypedDict, List, Annotated, Dict, Union
import operator



from pydantic import BaseModel, Field
from typing import List, Optional

# Add Tavily's arguments to enhance the web search tool's capabilities
class TavilyQuery(BaseModel):
    query: str = Field(description="web search query")

# Define the args_schema for the tavily_search tool using a multi-query approach, enabling more precise queries for Tavily.
class TavilySearchInput(BaseModel):
    sub_queries: List[TavilyQuery] = Field(description="set of sub-queries that can be answered in isolation")

class LiteratureResearchOutput(BaseModel):
    polymorphs: str = Field(
        ...,
        description="Detailed description of polymorphic forms of the active substance identified in the literature."
    )
    scheme_of_degradation_route: str = Field(
        ...,
        description="Detailed scheme of degradation routes based on literature and DMF sources."
    )
    stability_indicators: str = Field(
        ...,
        description="Key stability indicators obtained from the literature and DMF."
    )
    impurities: str = Field(
        ...,
        description="Information on relevant impurities derived from the literature, DMF, and USP Monograph, if applicable."
    )
    biopharmaceutical_classification: str = Field(
        ...,
        description="Biopharmaceutical classification based on physicochemical properties and permeability."
    )
    hygroscopicity: str = Field(
        ...,
        description="Data on hygroscopicity collected through PubChem web scraping and relevant literature."
    )
    chirality_or_specific_optical_rotation: str = Field(
        ...,
        description="Information on chirality or specific optical rotation obtained from DMF and other literary sources."
    )
    glass_transition_temperature: str = Field(
        ...,
        description="Glass transition temperature based on available studies in the literature."
    )
    degradation_temperature: str = Field(
        ...,
        description="Degradation temperature identified in the literature."
    )
    rld_special_characteristics: str = Field(
        ...,
        description="Special characteristics of the API and excipients for the RLD, such as crystalline form or particle size, based on COFA and literature."
    )
    rld_manufacturing_process_info: str = Field(
        ...,
        description="Manufacturing process information for the RLD, including controls and recommended conditions, obtained from sources like LiteratureResearchAgent, PatentResearchAgent, and EMA API."
    )

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

class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Query for web search.")

class Queries(BaseModel):
    queries: List[SearchQuery] = Field(
        description="List of search queries.",
    )

# Define Input product information
class ProductInformation(BaseModel):
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
    route_of_administracion: str = Field(
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

# Define the research state
class LiteratureResearchGraphState(TypedDict):
    input_documents: List[str]                                                            # List of strings with the local directory of the documents (Input from UI)
    product_information: ProductInformation                                               # Product information to be developed
    search_queries: List[SearchQuery]                                                     # List of search queries
    completed_report_section: Annotated[list, operator.add]                               # List of report sections 
    consolidated_research_report: str                                                     # Consolidated report
    literature_research_output_dict: LiteratureResearchOutput

class InputState(TypedDict):
    input_documents: List[str]

class OutputState(TypedDict):
    literature_research_output_dict: LiteratureResearchOutput