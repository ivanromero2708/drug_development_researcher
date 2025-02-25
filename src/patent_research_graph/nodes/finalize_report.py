from src.patent_research_graph.state import PatentResearchGraphState
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration
from src.state import PatentResearchReport

class FinalizeReport:
    def __init__(self) -> None:
        pass
    
    def finalize_report(self, state: PatentResearchGraphState, config: RunnableConfig):
        """ The is the "reduce" step where we gather all the sections, combine them, and reflect on them to write the intro/conclusion """
        # Save full final report
        api_name = state["api"].API_name
        content = state["patent_research_report_content"]
        if content.startswith("Insights"):
            content = content.strip("Insights")
        if "Sources" in content:
            try:
                content, sources = content.split("\nSources\n")
            except:
                sources = None
        else:
            sources = None

        final_report = "- Introduction.\n\n" + state["patent_research_report_introduction"] + "\n\n---\n\n" + content + "\n\n---\n\n" + "- Conclusions.\n\n" + state["patent_research_report_conclusion"]
        if sources is not None:
            final_report += "\n\nSources\n" + sources
        return {"patent_research_report": [PatentResearchReport(api_name=api_name, patent_research_report_api=final_report)]}
    
    def run(self, state: PatentResearchGraphState, config: RunnableConfig):
        return self.finalize_report(state, config)
