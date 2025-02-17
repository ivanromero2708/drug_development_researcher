from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from src.state import DrugDevelopmentResearchGraphState

from src.literature_research_agent.graph import literature_researcher_graph_builder

from .nodes import(
    ExtractInputInformation,
    ConsolidateContext,
    RenderReport,
)

from .edges import(
    InitializeLiteratureResearch,
)

extract_input_information = ExtractInputInformation()
initialize_literature_research_agent = InitializeLiteratureResearch()
consolidate_context = ConsolidateContext()
render_report = RenderReport()

# Add nodes and edges 
drug_development_researcher_graph_builder = StateGraph(DrugDevelopmentResearchGraphState)
drug_development_researcher_graph_builder.add_node("extract_input_information", extract_input_information.run)
drug_development_researcher_graph_builder.add_node("literature_research", literature_researcher_graph_builder.compile())
drug_development_researcher_graph_builder.add_node("consolidate_context", consolidate_context.run)
drug_development_researcher_graph_builder.add_node("render_report", render_report.run)

# Logic
drug_development_researcher_graph_builder.add_edge(START, "extract_input_information")
drug_development_researcher_graph_builder.add_conditional_edges("extract_input_information", initialize_literature_research_agent.run, ["literature_research"])
drug_development_researcher_graph_builder.add_edge("literature_research", "consolidate_context")
drug_development_researcher_graph_builder.add_edge("consolidate_context", "render_report")
drug_development_researcher_graph_builder.add_edge("render_report", END)

# Compile
drug_development_researcher_memory = MemorySaver()
drug_development_researcher_graph = drug_development_researcher_graph_builder.compile(checkpointer = drug_development_researcher_memory)


