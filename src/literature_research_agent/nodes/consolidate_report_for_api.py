from src.literature_research_agent.state import LiteratureResearchGraphState
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration

class ConsolidateReportAPI:
    def __init__(self):
        self.consigurable = None
    
    def consolidate_report_for_api(self, state: LiteratureResearchGraphState, config: RunnableConfig):
        api_property_report = ' '.join(state["api_property_report"])

        return {"context": api_property_report}
    
    def run(self, state: LiteratureResearchGraphState, config: RunnableConfig):
        return self.consolidate_report_for_api(state, config)