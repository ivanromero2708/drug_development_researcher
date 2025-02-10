from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from src.state import DrugDevelopmentResearchGraphState

from src.literature_research_agent.graph import literature_researcher_graph_builder

from .nodes import(
    ExtractInputInformation,
)

from .edges import(
    InitializeLiteratureResearch,
)

extract_input_information = ExtractInputInformation()
initialize_literature_research_agent = InitializeLiteratureResearch()

# Add nodes and edges 
drug_development_researcher_graph_builder = StateGraph(DrugDevelopmentResearchGraphState)
drug_development_researcher_graph_builder.add_node("extract_input_information", extract_input_information.run)
drug_development_researcher_graph_builder.add_node("literature_research", literature_researcher_graph_builder.compile())

# Logic
drug_development_researcher_graph_builder.add_edge(START, "extract_input_information")
drug_development_researcher_graph_builder.add_conditional_edges("extract_input_information", initialize_literature_research_agent.run, ["literature_research"])
drug_development_researcher_graph_builder.add_edge("literature_research", END)


"""
drug_development_researcher_graph_builder.add_conditional_edges("extract_input_information", initiate_all_research.run, "literature_research")
drug_development_researcher_graph_builder.add_conditional_edges("literature_research", END)
"""

# Compile
drug_development_researcher_memory = MemorySaver()
drug_development_researcher_graph = drug_development_researcher_graph_builder.compile(checkpointer = drug_development_researcher_memory)
