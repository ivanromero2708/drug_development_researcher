from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from src.literature_research_agent.property_research_graph.state import PropertyResearchGraphState

from .nodes import(
    WebResearch,
    GeneratePropertyReport,
)

web_research = WebResearch()
generate_property_report = GeneratePropertyReport()

# Add nodes and edges 
property_research_graph_builder = StateGraph(PropertyResearchGraphState)
property_research_graph_builder.add_node("web_research", web_research.run)
property_research_graph_builder.add_node("generate_property_report", generate_property_report.run)

# Logic
property_research_graph_builder.add_edge(START, "web_research")
property_research_graph_builder.add_edge("web_research", "generate_property_report")
property_research_graph_builder.add_edge("generate_property_report", END)

property_research_memory = MemorySaver()
property_research_graph = property_research_graph_builder.compile(checkpointer= property_research_memory)