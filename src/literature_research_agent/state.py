from langgraph.graph import add_messages
from langchain_core.messages import AnyMessage
from typing import TypedDict, List, Annotated, Dict, Union
import operator
from ..state import ProductInformation, API, DocumentCluster

from pydantic import BaseModel, Field
from typing import List, Optional

# Add Tavily's arguments to enhance the web search tool's capabilities
class TavilyQuery(BaseModel):
    query: str = Field(description="web search query")

# Define the args_schema for the tavily_search tool using a multi-query approach, enabling more precise queries for Tavily.
class TavilySearchInput(BaseModel):
    sub_queries: List[TavilyQuery] = Field(description="set of sub-queries that can be answered in isolation")

class APILiteratureData(BaseModel):
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

# Define the research state
class LiteratureResearchGraphState(TypedDict):
    API: API
    product_information: ProductInformation                                               # Product information to be developed
    search_queries: List[TavilyQuery]                                                     # List of search queries
    documents: Dict[str, Dict[Union[str, int], Union[str, float]]]
    document_clusters: List[DocumentCluster]
    chosen_clusters: List[int]
    context: str
    consolidated_research_report: str                                                     # Consolidated report
    apis_literature_data: List[APILiteratureData]

class InputState(TypedDict):
    product_information: ProductInformation                                               # Product information to be developed

class OutputState(TypedDict):
    apis_literature_data: List[APILiteratureData]