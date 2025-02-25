from ..state import InterviewState
from ..prompts import section_writer_instructions
from langchain_core.messages import HumanMessage, SystemMessage

from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration
from langchain_openai import ChatOpenAI

class WriteSection:
    def __init__(self) -> None:
        pass
    
    def write_section(self, state: InterviewState, config: RunnableConfig):
        """ Node to answer a question """
        # Get state
        context = state["interview"]
        analyst = state["analyst"]
        
        # Get configuration and initialize the LLM
        configurable = Configuration.from_runnable_config(config)
        llm = ChatOpenAI(model=configurable.gpt4omini, temperature=0) 
    
        # Write section using either the gathered source docs from interview (context) or the interview itself (interview)
        system_message = section_writer_instructions.format(focus=analyst.description)
        section = llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content=f"Use this source to write your section: {context}")]) 
                    
        # Append it to state
        return {"patent_research_report_sections": [section.content]}
    
    def run(self, state: InterviewState, config: RunnableConfig):
        return self.write_section(state, config)
