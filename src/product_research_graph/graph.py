from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from src.product_research_graph.state import ProductResearchGraphState, ProductResearchOutputState

from src.product_research_graph.product_enrichment_graph.graph import product_enrichement_graph_builder

from src.product_research_graph.nodes import (
    SearchByIngredient,
    SearchOrangeBookSingle,
    SearchOrangeBookCombined,
    DailyMedResearch,
    FormulatorFeedbackProductResearch,
)

from src.product_research_graph.edges import (
    ParallelizeDailyMedResearch,
    RouteProductResearch,
    RouteProductEnrichment,
)

# Initialize nodes
search_by_ingredient = SearchByIngredient()
search_orange_book_single = SearchOrangeBookSingle()
search_orange_book_combined = SearchOrangeBookCombined()
daily_med_research = DailyMedResearch()
formulator_feedback_product_research = FormulatorFeedbackProductResearch()

# Initialize edges
route_product_research = RouteProductResearch()
route_product_enrichment = RouteProductEnrichment()
parallelize_daily_med_research = ParallelizeDailyMedResearch()

# Create Graph
product_research_graph_builder =  StateGraph(input = ProductResearchGraphState, output = ProductResearchOutputState)

# Add nodes
# 1) Reference product search
product_research_graph_builder.add_node("search_by_ingredient", search_by_ingredient.run)
product_research_graph_builder.add_node("search_orange_book_single", search_orange_book_single.run)
product_research_graph_builder.add_node("search_orange_book_combined", search_orange_book_combined.run)

# 2) DailyMed search
product_research_graph_builder.add_node("daily_med_research", daily_med_research.run)

# 3) Formulator feedback on product research
product_research_graph_builder.add_node("formulator_feedback_product_research", formulator_feedback_product_research.run)

# 4) Parallelize Product Enrichment
product_research_graph_builder.add_node("product_enrichment", product_enrichement_graph_builder.compile())

# Add edges
# Initiate product research
product_research_graph_builder.add_conditional_edges(
    START,
    route_product_research.run,
    ["search_by_ingredient", "search_orange_book_single", "search_orange_book_combined"]
)

# Parallelizing DailyMed search
product_research_graph_builder.add_conditional_edges(
    "search_by_ingredient",
    parallelize_daily_med_research.run,
    ["daily_med_research"]
)

product_research_graph_builder.add_conditional_edges(
    "search_orange_book_single",
    parallelize_daily_med_research.run,
    ["daily_med_research"]
)

product_research_graph_builder.add_conditional_edges(
    "search_orange_book_combined",
    parallelize_daily_med_research.run,
    ["daily_med_research"]
)

# Formulator feedback
product_research_graph_builder.add_edge("daily_med_research", "formulator_feedback_product_research")

# Route to product enrichment
product_research_graph_builder.add_conditional_edges(
    "formulator_feedback_product_research",
    route_product_enrichment.run,
    ["product_enrichment", "daily_med_research"]
)

# Final
product_research_graph_builder.add_edge("product_enrichment", END)

# Compile graph
product_research_graph_memory = MemorySaver()
product_research_graph = product_research_graph_builder.compile(
    interrupt_before=["formulator_feedback_product_research"],
    #checkpointer=product_research_graph_memory,
)