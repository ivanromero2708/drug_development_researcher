import asyncio
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from ...configuration import Configuration
from ..state import LiteratureResearchGraphState, APILiteratureData

class ExtractInformation:
    def __init__(self):
        pass
    
    def extract_information(self, state: LiteratureResearchGraphState, config: RunnableConfig):
        consolidated_research_report = state["consolidated_research_report"]
        
        # Get configuration and initialize the LLM
        configurable = Configuration.from_runnable_config(config)
        llm = ChatOpenAI(model=configurable.gpt4o, temperature=0)
        structured_llm = llm.with_structured_output(APILiteratureData)
        
        api_literature_data = structured_llm.invoke(consolidated_research_report)
        return {"api_literature_data": api_literature_data}
    
    def run(self, state: LiteratureResearchGraphState, config: RunnableConfig):
        return self.extract_information(state, config)