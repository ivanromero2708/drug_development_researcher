from typing import TypedDict, List, Annotated, Dict, Union, Optional
from pydantic import BaseModel, Field
from src.state import ProductInformation, API

class PropertyResearchGraphState(TypedDict):
    query: str
    documents: Dict[str, Dict[Union[str, int], Union[str, float]]]
    property_research_context: str
    api_property_report: str