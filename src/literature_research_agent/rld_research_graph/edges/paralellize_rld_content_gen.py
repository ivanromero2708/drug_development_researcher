from langchain_core.runnables import RunnableConfig
from src.literature_research_agent.rld_research_graph.state import RLDResearchGraphState
from langgraph.constants import Send
from src.configuration import MAPPING_DRUG_LABEL_SECTION

class ParallelizeRLDContentGen:
    def __init__(self):
        self.configurable = None
    
    def run(self, state: RLDResearchGraphState, config: RunnableConfig):
        return [
            Send("generate_rld_content", 
                {
                    "API": state["API"],
                    "product_information_child": state["product_information_child"],
                    "drug_label_doc": state["drug_label_doc"],
                    "rld_report_section": rld_report_section,                    
                }
            ) 
            for rld_report_section in MAPPING_DRUG_LABEL_SECTION.keys()
        ]