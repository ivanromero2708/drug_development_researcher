import asyncio
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration
from src.literature_research_agent.state import LiteratureResearchGraphState
from src.state import APILiteratureData
from src.literature_research_agent.prompts import PROMPT_EXTRACT_INFORMATION


class ExtractInformation:
    def __init__(self):
        pass
    
    def extract_information(self, state: LiteratureResearchGraphState, config: RunnableConfig):
        consolidated_research_report = state["context"]
        
        # Get configuration and initialize the LLM
        configurable = Configuration.from_runnable_config(config)
        llm = ChatOpenAI(model=configurable.gpt4omini, temperature=0)
        structured_llm = llm.with_structured_output(APILiteratureData)
        
        report_language = configurable.language_for_report
        
        system_msg = SystemMessage(
            content = PROMPT_EXTRACT_INFORMATION
        )
        
        human_msg = HumanMessage(
            content = f"""Extract structured data from the provided consolidated pharmaceutical research report for pharmaceutical product development in the language {report_language}. In each variable, it is really important that you extract the url link.
            - Consolidated pharmaceutical report:
            <consolidated_research_report>
            {consolidated_research_report}
            </consolidated_research_report>"""
        )
        
        api_literature_data = structured_llm.invoke([system_msg, human_msg])
        
        return {"api_literature_data": [api_literature_data]}
    
    def run(self, state: LiteratureResearchGraphState, config: RunnableConfig):
        return self.extract_information(state, config)