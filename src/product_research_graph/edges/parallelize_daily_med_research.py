from langchain_core.runnables import RunnableConfig
from src.product_research_graph.state import ProductResearchGraphState

from langgraph.constants import Send
from langchain_core.runnables import RunnableConfig

class ParallelizeDailyMedResearch:
    def __init__(self):
        pass
    
    def parallelize_daily_med_research(self, state: ProductResearchGraphState, config: RunnableConfig):
        return [
            Send("daily_med_research", 
                {
                    "RLD": RLD,
                }
            ) 
            for RLD in state["RLDs"]
        ]
    
    def run(self, state: ProductResearchGraphState, config: RunnableConfig):
        return self.parallelize_daily_med_research(state, config)