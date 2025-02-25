from src.patent_research_graph.state import PatentResearchGraphState
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration

from langchain_openai import ChatOpenAI
from src.patent_research_graph.prompts import intro_conclusion_instructions
from langchain_core.messages import HumanMessage

class WriteIntroduction:
    def __init__(self) -> None:
        pass
        
    def write_introduction(self, state: PatentResearchGraphState, config: RunnableConfig):
        # Full set of sections
        sections = state["patent_research_report_sections"]
        api_name = state["api"].API_name
        
        # Get configuration and initialize the LLM
        configurable = Configuration.from_runnable_config(config)
        llm = ChatOpenAI(model=configurable.gpt4omini, temperature=0) 
        
        # Concat all sections together
        formatted_str_sections = "\n\n".join([f"{section}" for section in sections])
        
        # Summarize the sections into a final report
        
        instructions = intro_conclusion_instructions.format(
            formatted_str_sections=formatted_str_sections,
            api_name=api_name,
            )    
        
        intro = llm.invoke([instructions]+[HumanMessage(content=f"Write the report introduction")]) 
        return {"patent_research_report_introduction": intro.content}
    
    def run(self, state: PatentResearchGraphState, config: RunnableConfig):
        return self.write_introduction(state, config)
