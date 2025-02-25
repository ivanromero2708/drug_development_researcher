from typing import List, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
import operator
from langgraph.graph import MessagesState
from src.state import API, PatentResearchReport

class Analyst(BaseModel):
    affiliation: str = Field(
       description="Primary affiliation of the analyst.",
    )
    name: str = Field(
        description="Name of the analyst."
    )
    role: str = Field(
        description="Role of the analyst in the context of the topic.",
    )
    description: str = Field(
        description="Description of the analyst focus, concerns, and motives.",
    )
    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nAffiliation: {self.affiliation}\nDescription: {self.description}\n"

class Perspectives(BaseModel):
    analysts: List[Analyst] = Field(
        description="Comprehensive list of analysts with their roles and affiliations.",
    )

class PatentResearchGraphState(TypedDict):     
    api: API
    analysts: List[Analyst] # Analyst asking questions
    patent_research_report_sections: Annotated[List[str], operator.add]
    patent_research_report_content: str   
    patent_research_report_introduction: str
    patent_research_report_conclusion: str
    
    patent_research_report: Annotated[List[PatentResearchReport], operator.add]

class PatentResearchOutputState(TypedDict):     
    patent_research_report: Annotated[List[PatentResearchReport], operator.add]
    