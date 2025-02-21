from langchain_core.runnables import RunnableConfig
from src.product_research_graph.state import ProductResearchGraphState
from langgraph.constants import Send
from src.configuration import MAPPING_DRUG_LABEL_SECTION

class ParallelizeRLDContentGen:
    def __init__(self):
        self.configurable = None
    
    def run(self, state: ProductResearchGraphState, config: RunnableConfig):
        return [
            Send("generate_rld_content", 
                {
                    "selected_RLD": state["selected_RLD"],
                    "drug_label_doc": state["drug_label_doc"],
                    "product_report_section": product_report_section,                    
                }
            ) 
            for product_report_section in MAPPING_DRUG_LABEL_SECTION.keys()
        ]