from langchain_core.runnables import RunnableConfig
from ..state import DrugDevelopmentResearchGraphState
from langgraph.constants import Send

class InitializeLiteratureResearch:
    def __init__(self):
        self.configurable = None
    
    def run(self, state: DrugDevelopmentResearchGraphState, config: RunnableConfig):
        product_information = state["product_information"]
        return [
            Send("literature_research", 
                {
                    "API": API,
                    "product_information": product_information,
                }
            ) 
            for API in state["apis"]
        ]
