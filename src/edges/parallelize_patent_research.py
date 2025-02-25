from langchain_core.runnables import RunnableConfig
from src.state import DrugDevelopmentResearchGraphState
from langgraph.constants import Send
from langchain_core.runnables import RunnableConfig

class ParallelizePatentResearch:
    def __init__(self):
        pass

    def run(self, state: DrugDevelopmentResearchGraphState, config: RunnableConfig):
        return [
            Send("patent_research", 
                {
                    "api": api,
                }
            ) 
            for api in state["apis"]
        ]