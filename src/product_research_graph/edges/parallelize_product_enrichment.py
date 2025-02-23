from src.product_research_graph.state import ProductResearchGraphState
from langchain_core.runnables import RunnableConfig
from langgraph.constants import Send

class ParallelizeProductEnrichment:
    """
    Conditional edge that reads `feedback_decision` from the state.
    
    - If 'feedback_decision' == 'retry_daily_med', we route to 'daily_med_research'.
    - If 'feedback_decision' starts with 'go_enrich' => we route to 'product_enrichment'.
      (Because it might be 'go_enrich_accept' or 'go_enrich_blank' or something else.)
    - Otherwise, we default to 'product_enrichment'.
    """

    def __init__(self):
        pass

    def run(self, state: ProductResearchGraphState, config: RunnableConfig):
        return [
            Send("product_enrichment", 
                {
                    "selected_RLD": selected_RLD,
                }
            ) 
            for selected_RLD in state["selected_RLDs"]
        ]
