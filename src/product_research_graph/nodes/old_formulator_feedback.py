from src.product_research_graph.state import ProductResearchGraphState
from langchain_core.runnables import RunnableConfig

class FormulatorFeedbackProductResearch:
    def __init__(self):
        pass
    
    def formulator_feedback_product_research(self, state: ProductResearchGraphState, config: RunnableConfig):
        """ No-op node that should be interrupted on """
        pass
    
    def run(self, state: ProductResearchGraphState, config: RunnableConfig):
        return self.formulator_feedback_product_research(state, config)
    

    