from langchain_core.runnables import RunnableConfig
from src.literature_research_agent.state import LiteratureResearchGraphState
from langgraph.constants import Send

class InitiatePropertyResearch:
    def __init__(self):
        self.configurable = None
    
    def run(self, state: LiteratureResearchGraphState, config: RunnableConfig):
        return [
            Send("property_research", 
                {
                    "query": query,
                }
            ) 
            for query in state["search_queries"]
        ]
