from langchain_core.runnables import RunnableConfig
from src.state import DrugDevelopmentResearchGraphState
from langgraph.constants import Send
from langchain_core.runnables import RunnableConfig

class ParallelizeRLDResearchSingle:
    def __init__(self):
        pass
    
    def parallelize_rld_research_from_single(self, state: DrugDevelopmentResearchGraphState, config: RunnableConfig):
        return [
            Send("rld_research", 
                {
                    "RLD": RLD,
                }
            ) 
            for RLD in state["RLDs"]
        ]
    
    def run(self, state: DrugDevelopmentResearchGraphState, config: RunnableConfig):
        return self.parallelize_rld_research_from_single(state, config)