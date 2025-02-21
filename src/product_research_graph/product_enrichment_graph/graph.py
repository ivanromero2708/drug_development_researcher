from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from src.product_research_graph.product_enrichment_graph.state import ProductEnrichmentGraphState, ProductEnrichmentOutputState

from src.product_research_graph.product_enrichment_graph.nodes import(
    GetCleanDrugLabelInfo,
    GenerateRLDContent,   
    ConsolidateRLDContext, 
)

from src.product_research_graph.product_enrichment_graph.edges import(
    ParallelizeRLDContentGen
)

# Initialize Nodes
get_clean_drug_label_info = GetCleanDrugLabelInfo()
generate_rld_content = GenerateRLDContent()
consolidate_rld_context = ConsolidateRLDContext()

# Initialize Edges
paralellize_rld_content_gen = ParallelizeRLDContentGen()

# Create Graph
product_enrichement_graph_builder = StateGraph(input=ProductEnrichmentGraphState, output=ProductEnrichmentOutputState)

# Add Nodes
product_enrichement_graph_builder.add_node("get_clean_drug_label_info", get_clean_drug_label_info.run)
product_enrichement_graph_builder.add_node("generate_rld_content", generate_rld_content.run)
product_enrichement_graph_builder.add_node("consolidate_rld_context", consolidate_rld_context.run)

# Add Edges
product_enrichement_graph_builder.add_edge(START, "get_clean_drug_label_info")
product_enrichement_graph_builder.add_conditional_edges("get_clean_drug_label_info", paralellize_rld_content_gen.run, ["generate_rld_content"])
product_enrichement_graph_builder.add_edge("generate_rld_content", "consolidate_rld_context")
product_enrichement_graph_builder.add_edge("consolidate_rld_context", END)

# Compile the graph
product_enrichment_graph_memory = MemorySaver()
product_enrichment_graph = product_enrichement_graph_builder.compile(checkpointer=product_enrichment_graph_memory)
