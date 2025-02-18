from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from src.state import DrugDevelopmentResearchGraphState

from src.literature_research_agent.graph import literature_researcher_graph_builder
from src.rld_research_graph.graph import rld_researcher_graph_builder

from .nodes import(
    ExtractAPIsInformation,
    ExtractInputInformation,
    ConsolidateContext,
    RenderReport,
    SearchOrangeBookSingle,
    SearchOrangeBookCombined,
)

from .edges import(
    InitializeLiteratureResearch,
    IsRLDCombination,
    ParallelizeRLDResearchCombined,
    ParallelizeRLDResearchSingle,
)

extract_apis_information = ExtractAPIsInformation()
extract_input_information = ExtractInputInformation()
initialize_literature_research_agent = InitializeLiteratureResearch()
consolidate_context = ConsolidateContext()
render_report = RenderReport()

is_rld_combination_edge = IsRLDCombination()
parallelize_rld_research_from_single = ParallelizeRLDResearchSingle()
parallelize_rld_research_from_combined = ParallelizeRLDResearchCombined()


search_orange_book_single = SearchOrangeBookSingle()
search_orange_book_combined = SearchOrangeBookCombined()

# Add nodes and edges 
drug_development_researcher_graph_builder = StateGraph(DrugDevelopmentResearchGraphState)

# 1) Basic extraction
drug_development_researcher_graph_builder.add_node("extract_apis_information", extract_apis_information.run)
drug_development_researcher_graph_builder.add_node("extract_input_information", extract_input_information.run)

# 2) Literature research subgraph
drug_development_researcher_graph_builder.add_node("literature_research", literature_researcher_graph_builder.compile())

# 3) RLD nodes and subgraph
drug_development_researcher_graph_builder.add_node("rld_research", rld_researcher_graph_builder.compile())
drug_development_researcher_graph_builder.add_node("search_orange_book_single", search_orange_book_single.run)
drug_development_researcher_graph_builder.add_node("search_orange_book_combined", search_orange_book_combined.run)


# 4) Consolidation & final
drug_development_researcher_graph_builder.add_node("consolidate_context", consolidate_context.run)
drug_development_researcher_graph_builder.add_node("render_report", render_report.run)

# EDGES

# Start -> extract_apis -> extract_input
drug_development_researcher_graph_builder.add_edge(START, "extract_apis_information")
drug_development_researcher_graph_builder.add_edge("extract_apis_information", "extract_input_information")


# Literature research (parallel path)
drug_development_researcher_graph_builder.add_conditional_edges(
    "extract_input_information",
    initialize_literature_research_agent.run,
    ["literature_research"]
)

# RLD combination check:
drug_development_researcher_graph_builder.add_conditional_edges(
    "extract_apis_information",
    is_rld_combination_edge.run,
    ["search_orange_book_single", "search_orange_book_combined"]
)

# RLD research (parallel path from single RLD search)
drug_development_researcher_graph_builder.add_conditional_edges(
    "search_orange_book_single",
    parallelize_rld_research_from_single.run,
    ["rld_research"]
)

# RLD research (parallel path from combined RLD search)
drug_development_researcher_graph_builder.add_conditional_edges(
    "search_orange_book_combined",
    parallelize_rld_research_from_combined.run,
    ["rld_research"]
)

# Merge paths -> consolidate
drug_development_researcher_graph_builder.add_edge(
    ["literature_research", "rld_research"],
    "consolidate_context"
)

# Final
drug_development_researcher_graph_builder.add_edge("consolidate_context", "render_report")
drug_development_researcher_graph_builder.add_edge("render_report", END)

# Compile
drug_development_researcher_memory = MemorySaver()
drug_development_researcher_graph = drug_development_researcher_graph_builder.compile(
    checkpointer=drug_development_researcher_memory
)
