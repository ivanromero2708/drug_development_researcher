from typing import TypedDict, List, Annotated, Dict, Union, Optional
from pydantic import BaseModel, Field
from src.state import ProductInformation, API, PropertyReportSection
import operator

class PropertyResearchGraphState(TypedDict):
    API_name: str
    query: str
    documents: Dict[str, Dict[Union[str, int], Union[str, float]]]
    property_research_context: str
    api_research_property_report: Annotated[List[PropertyReportSection], operator.add]