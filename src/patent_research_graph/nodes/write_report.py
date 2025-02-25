from src.patent_research_graph.state import PatentResearchGraphState
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration

class WriteReport:
    def __init__(self) -> None:
        pass
    
    def write_report(self, state: PatentResearchGraphState, config: RunnableConfig):
        # Full set of sections
        sections = state["patent_research_report_sections"]

        # Concat all sections together
        formatted_str_sections = "\n\n".join([f"{section}" for section in sections])

        return {"patent_research_report_content": formatted_str_sections}
    
    def run(self, state: PatentResearchGraphState, config: RunnableConfig):
        return self.write_report(state, config)
