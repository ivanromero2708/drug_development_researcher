from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from src.state import DrugDevelopmentResearchGraphState

from src.literature_research_agent.graph import literature_researcher_graph_builder
from src.product_research_graph.graph import product_research_graph_builder

from .nodes import(
    ExtractAPIsInformation,
    ExtractInputInformation,
    ConsolidateContext,
    RenderReport,
)

from .edges import(
    InitializeLiteratureResearch,
    IsRLDCombination,
)

extract_apis_information = ExtractAPIsInformation()
extract_input_information = ExtractInputInformation()
initialize_literature_research_agent = InitializeLiteratureResearch()
consolidate_context = ConsolidateContext()
render_report = RenderReport()

is_rld_combination_edge = IsRLDCombination()

# Create Graph
drug_development_researcher_graph_builder = StateGraph(DrugDevelopmentResearchGraphState)
drug_development_researcher_memory = MemorySaver()

# Add nodes
# 1) Basic extraction
drug_development_researcher_graph_builder.add_node("extract_apis_information", extract_apis_information.run)
drug_development_researcher_graph_builder.add_node("extract_input_information", extract_input_information.run)

# 2) Literature research subgraph
drug_development_researcher_graph_builder.add_node("literature_research", literature_researcher_graph_builder.compile(checkpointer=drug_development_researcher_memory))

# 3) Product research subgraph
drug_development_researcher_graph_builder.add_node("product_research", product_research_graph_builder.compile(checkpointer=drug_development_researcher_memory))

# 4) Consolidation & final
drug_development_researcher_graph_builder.add_node("consolidate_context", consolidate_context.run)
drug_development_researcher_graph_builder.add_node("render_report", render_report.run)

# Add Edges

# Start -> extract_apis -> extract_input
drug_development_researcher_graph_builder.add_edge(START, "extract_apis_information")
drug_development_researcher_graph_builder.add_edge("extract_apis_information", "extract_input_information")


# Go to product_research subgraph
drug_development_researcher_graph_builder.add_edge("extract_apis_information", "product_research")

# Literature research (parallel path)
drug_development_researcher_graph_builder.add_conditional_edges(
    "extract_input_information",
    initialize_literature_research_agent.run,
    ["literature_research"]
)

# Product research (Subgraph execution)
drug_development_researcher_graph_builder.add_edge("extract_apis_information", "product_research")

# Merge paths -> consolidate
drug_development_researcher_graph_builder.add_edge(
    ["literature_research", "product_research"],
    "consolidate_context"
)

# Final
drug_development_researcher_graph_builder.add_edge("consolidate_context", "render_report")
drug_development_researcher_graph_builder.add_edge("render_report", END)

# Compile
drug_development_researcher_graph = drug_development_researcher_graph_builder.compile(
    checkpointer=drug_development_researcher_memory,
)