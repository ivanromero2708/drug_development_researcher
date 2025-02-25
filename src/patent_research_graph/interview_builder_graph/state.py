import operator
from langgraph.graph import MessagesState
from typing import Annotated
from pydantic import BaseModel, Field
from src.patent_research_graph.state import Analyst

class InterviewState(MessagesState):
    max_num_turns: int # Number turns of conversation
    context: Annotated[list, operator.add] # Source docs
    analyst: Analyst # Analyst asking questions
    interview: str # Interview transcript
    patent_research_report_sections: list # Final key we duplicate in outer state for Send() API

class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Search query for retrieval.")