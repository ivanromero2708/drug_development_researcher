from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from src.rld_research_graph.state import RLDResearchGraphState, RLDResearchOutputState
from src.configuration import Configuration

from src.rld_research_graph.nodes import(
    GetCleanDrugLabelInfo,
    GenerateRLDContent,   
    ConsolidateRLDContext, 
)

from src.rld_research_graph.edges import(
    ParallelizeRLDContentGen
)

get_clean_drug_label_info = GetCleanDrugLabelInfo()
paralellize_rld_content_gen = ParallelizeRLDContentGen()
generate_rld_content = GenerateRLDContent()
consolidate_rld_context = ConsolidateRLDContext()

# Add nodes and edges 
rld_researcher_graph_builder = StateGraph(input=RLDResearchGraphState, output=RLDResearchOutputState)
rld_researcher_graph_builder.add_node("get_clean_drug_label_info", get_clean_drug_label_info.run)
rld_researcher_graph_builder.add_node("generate_rld_content", generate_rld_content.run)
rld_researcher_graph_builder.add_node("consolidate_rld_context", consolidate_rld_context.run)

# Logic
rld_researcher_graph_builder.add_edge(START, "get_clean_drug_label_info")
rld_researcher_graph_builder.add_conditional_edges("get_clean_drug_label_info", paralellize_rld_content_gen.run, ["generate_rld_content"])
rld_researcher_graph_builder.add_edge("generate_rld_content", "consolidate_rld_context")
rld_researcher_graph_builder.add_edge("consolidate_rld_context", END)

# Graph definition
rld_researcher_graph_memory = MemorySaver()
rld_researcher_graph_graph = rld_researcher_graph_builder.compile(checkpointer= rld_researcher_graph_memory)