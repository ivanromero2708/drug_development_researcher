import asyncio
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_community.document_loaders import PyPDFLoader

from ..configuration import Configuration
from ..state import ProductInformation, DrugDevelopmentResearchGraphState, APIs, API
from ..prompts import PROMPT_EXTRACT_INPUT_INFORMATION, PROMPT_EXTRACT_API_INFORMATION

class ExtractAPIsInformation:
    def __init__(self):
        pass
    
    def extract_apis_information(self, state: DrugDevelopmentResearchGraphState, config: RunnableConfig):
        apis_text_information = state["apis_text_information"]
        
        # Initialize the node elements using the configuration.
        conf = Configuration.from_runnable_config(config)
        language_for_extraction = conf.language_for_extraction
        llm = ChatOpenAI(model=conf.o3mini, reasoning_effort = "medium")
        
        # Configure structured output for the ProductInformation model.
        structured_llm = llm.with_structured_output(APIs)
        
        system_msg = SystemMessage(
            content= PROMPT_EXTRACT_API_INFORMATION.format(
                apis_text_information = apis_text_information,
            )
        )
        
        human_msg = HumanMessage(
            content = f"Extract the information of the active ingredients (without, repeating the API) as structured JSON following the provided keys, in the desired language {language_for_extraction}"
        )
        
        apis_information = structured_llm.invoke([system_msg, human_msg])
        
        return {"apis": apis_information.list_apis}
    
    def run(self, state: DrugDevelopmentResearchGraphState, config: RunnableConfig):
        return self.extract_apis_information(state, config)