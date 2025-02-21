from src.product_research_graph.state import ProductResearchGraphState
from langchain_core.runnables import RunnableConfig

class RouteProductResearch:
    def __init__(self):
        pass
    
    def route_product_research(self, state: ProductResearchGraphState, config):
        is_rld_combination = state["is_rld_combination"]
        is_supplement = state["is_supplement"]
        
        if is_supplement == "Y":
            return "search_by_ingredient"
        else:
            if is_rld_combination == "Y":
                return "search_orange_book_combined"
            else:
                return "search_orange_book_single"
    
    def run(self, state: ProductResearchGraphState, config: RunnableConfig):
        return self.route_product_research(state, config)