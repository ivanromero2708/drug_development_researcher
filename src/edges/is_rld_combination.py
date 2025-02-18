from src.state import DrugDevelopmentResearchGraphState
from langgraph.constants import Send
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

class IsRLDCombination:
    def __init__(self):
        pass
    
    def is_rld_combination_edge(self, state: DrugDevelopmentResearchGraphState, config):
        is_rld_combination = state["is_rld_combination"]
        
        if is_rld_combination == "Y":
            return "search_orange_book_combined"
        else:
            return "search_orange_book_single"
    
    def run(self, state, config):
        return self.is_rld_combination_edge(state, config)