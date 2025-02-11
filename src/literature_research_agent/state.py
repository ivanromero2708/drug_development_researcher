from langgraph.graph import add_messages
from langchain_core.messages import AnyMessage
from typing import TypedDict, List, Annotated, Dict, Union, Optional
from src.state import ProductInformation, API, DocumentCluster, TavilyQuery, APILiteratureData
from pydantic import BaseModel, Field

class APIExternalData(BaseModel):
    cas_number: Optional[str] = Field(
        default="Not available",
        description="CAS number in XXXX-XX-X format",
    )
    description: str = Field(
        default="",
        description="Physical description with bullet points"
    )
    solubility: str = Field(
        default="",
        description="Solubility in various solvents"
    )
    melting_point: str = Field(
        default="Not available",
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
        None,
        ge=0,
        description="Molecular weight in g/mol",
    )
    log_p: str = Field(
        default="Not available",
        description="Octanol-water partition coefficient",
    )
    boiling_point: str = Field(
        default="Not available",
        description="Boiling point in 'value °C at pressure'",
    )


# Define the research state
class LiteratureResearchGraphState(TypedDict):
    API: API
    product_information_child: ProductInformation                                               # Product information to be developed
    api_external_APIkey_data: APIExternalData
    search_queries: List[TavilyQuery]                                                     # List of search queries
    documents: Dict[str, Dict[Union[str, int], Union[str, float]]]
    document_clusters: List[DocumentCluster]
    chosen_clusters: List[int]
    context: str
    consolidated_research_report: str                                                     # Consolidated report
    api_literature_data: APILiteratureData

class InputState(TypedDict):
    product_information: ProductInformation                                               # Product information to be developed

class OutputState(TypedDict):
    apis_literature_data: List[APILiteratureData]