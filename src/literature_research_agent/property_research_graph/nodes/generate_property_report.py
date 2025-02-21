from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from src.literature_research_agent.property_research_graph.state import PropertyResearchGraphState
from src.state import PropertyReportSection
from src.configuration import Configuration
from src.literature_research_agent.property_research_graph.prompts import SYSTEM_PROMPT_GENERATE_PROPERTY_REPORT, HUMAN_PROMPT_GENERATE_PROPERTY_REPORT
from pydantic import BaseModel, Field
from typing import Literal



class GeneratePropertyReport:
    def __init__(self):
        self.configurable = None
    
    def generate_property_report(self, state: PropertyResearchGraphState, config: RunnableConfig):
        query = state["query"]
        property_research_context = state["property_research_context"]
        
        # Get configuration and initialize the LLM
        configurable = Configuration.from_runnable_config(config)
        llm = ChatOpenAI(model=configurable.o3mini, reasoning_effort = "medium") 
        
        structured_llm = llm.with_structured_output(PropertyReportSection)
        
        system_msg = SystemMessage(
            content = SYSTEM_PROMPT_GENERATE_PROPERTY_REPORT.format(
            query = query,
            property_research_context = property_research_context,
        )
        )
        
        human_instructions = HUMAN_PROMPT_GENERATE_PROPERTY_REPORT
        
        human_msg = HumanMessage(
            content = human_instructions
        )
        
        response = structured_llm.invoke([system_msg, human_msg])        
        
        return {"api_research_property_report": [response]}
    
    def run(self, state: PropertyResearchGraphState, config: RunnableConfig):
        return self.generate_property_report(state, config)