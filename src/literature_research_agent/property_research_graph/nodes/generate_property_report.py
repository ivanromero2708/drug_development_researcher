from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from src.literature_research_agent.property_research_graph.state import PropertyResearchGraphState
from src.configuration import Configuration
from src.literature_research_agent.property_research_graph.prompts import PROMPT_GENERATE_PROPERTY_REPORT

class GeneratePropertyReport:
    def __init__(self):
        self.configurable = None
    
    def generate_property_report(self, state: PropertyResearchGraphState, config: RunnableConfig):
        query = state["query"]
        property_research_context = state["property_research_context"]
        
        # Get configuration and initialize the LLM
        configurable = Configuration.from_runnable_config(config)
        llm = ChatOpenAI(model=configurable.gpt4omini, temperature=0) 
        
        system_instructions = PROMPT_GENERATE_PROPERTY_REPORT.format(
            query = query,
            property_research_context = property_research_context,
        )
        system_msg = SystemMessage(
            content = system_instructions
        )
        
        human_msg = HumanMessage(
            content = f"Generate a detailed, fact-based Plain Text report using the provided property context."
        )
        
        response = llm.invoke([system_msg, human_msg])
        plain_text_content = response.content
        
        return {"api_property_report": [plain_text_content]}
    
    def run(self, state: PropertyResearchGraphState, config: RunnableConfig):
        return self.generate_property_report(state, config)