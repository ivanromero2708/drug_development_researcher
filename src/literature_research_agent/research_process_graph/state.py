from pydantic import BaseModel, Field
from typing import TypedDict, List, Annotated, Dict, Union


# Define the structure for clustering output
class DocumentCluster(BaseModel):
    API_name: str = Field(
        ...,
        description="The name of the Active Pharmaceutical Ingredients these documents belong to."
    )
    cluster: List[str] = Field(
        ...,
        description="A list of URLs relevant to the identified Active Pharmaceutical Ingredient."
    )

class ResearchProcessGraphState(TypedDict):
    query: str
    documents: Dict[str, Dict[Union[str, int], Union[str, float]]]
    document_clusters: List[DocumentCluster]
    chosen_cluster: int
    context: str
    report: str