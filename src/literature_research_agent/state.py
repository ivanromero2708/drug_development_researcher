from langgraph.graph import add_messages
from langchain_core.messages import AnyMessage
from typing import TypedDict, List, Annotated, Dict, Union, Optional
from src.state import ProductInformation, API, TavilyQuery, APILiteratureData, PropertyReportSection, RLDReportSection
from pydantic import BaseModel, Field
import operator

class APIExternalData(BaseModel):
    cas_number: Optional[str] = Field(
        description="CAS number in XXXX-XX-X format",
    )
    description: str = Field(
        description="Physical description with bullet points"
    )
    solubility: str = Field(
        description="Solubility in various solvents"
    )
    pka: Optional[str] = Field(
        ...,
        description = "The pKa or dissociation constant for the API. pKa is the negative logarithm of the acid dissociation constant (Ka) of a compound, representing the pH at which half of the compound is ionized. It indicates the strength of an acid: lower pKa values correspond to stronger acids, while higher values indicate weaker acids."
    )
    stability: Optional[str] = Field(
        ..., 
        description = "The stability storage conditions for the API. Stability Conditions refer to the specific environmental parameters under which an Active Pharmaceutical Ingredient (API) or drug product maintains its chemical, physical, microbiological, and therapeutic integrity over time. These conditions typically include temperature, humidity, light exposure, and packaging requirements to prevent degradation and ensure efficacy and safety."
    )
    melting_point: str = Field(
        description="Melting point in 'value ± deviation °C' format",
    )
    chemical_names: str = Field(
        description="IUPAC name of compound",
    )
    molecular_formula: str = Field(
        description="Molecular formula in Hill notation",
    )
    molecular_weight: Optional[float] = Field(
        description="Molecular weight in g/mol",
    )
    log_p: str = Field(
        description="Octanol-water partition coefficient",
    )
    boiling_point: str = Field(
        description="Boiling point in 'value °C at pressure'",
    )


# Define the research state
class LiteratureResearchGraphState(TypedDict):
    API: API
    product_information_child: ProductInformation
    api_external_APIkey_data: APIExternalData
    api_research_property_report: Annotated[List[PropertyReportSection], operator.add]
    rld_research_report: Annotated[List[RLDReportSection], operator.add]
    search_queries: List[TavilyQuery] 
    api_literature_data: APILiteratureData
