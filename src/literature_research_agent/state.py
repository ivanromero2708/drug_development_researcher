from langgraph.graph import add_messages
from langchain_core.messages import AnyMessage
from typing import TypedDict, List, Annotated, Dict, Union
import operator
from src.state import ProductInformation, API, DocumentCluster, TavilyQuery, APILiteratureData

from pydantic import BaseModel, Field
from typing import List, Optional


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
    api_literature_data: APILiteratureData

class InputState(TypedDict):
    product_information: ProductInformation                                               # Product information to be developed

class OutputState(TypedDict):
    apis_literature_data: List[APILiteratureData]