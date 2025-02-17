from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from src.literature_research_agent.rld_research_graph.state import RLDResearchGraphState, RLDResearchOutputState
from src.configuration import Configuration

from src.literature_research_agent.rld_research_graph.nodes import(
    SearchOrangeBook,
    GetCleanDrugLabelInfo,
    GenerateRLDContent,    
)

from src.literature_research_agent.rld_research_graph.edges import(
    ParallelizeRLDContentGen
)

search_orange_book = SearchOrangeBook(Configuration)
get_clean_drug_label_info = GetCleanDrugLabelInfo()
paralellize_rld_content_gen = ParallelizeRLDContentGen()
generate_rld_content = GenerateRLDContent()

# Add nodes and edges 
rld_researcher_graph_builder = StateGraph(input=RLDResearchGraphState, output=RLDResearchOutputState)
rld_researcher_graph_builder.add_node("search_orange_book", search_orange_book.run)
rld_researcher_graph_builder.add_node("get_clean_drug_label_info", get_clean_drug_label_info.run)
rld_researcher_graph_builder.add_node("generate_rld_content", generate_rld_content.run)

# Logic
rld_researcher_graph_builder.add_edge(START, "search_orange_book")
rld_researcher_graph_builder.add_edge("search_orange_book", "get_clean_drug_label_info")
rld_researcher_graph_builder.add_conditional_edges("get_clean_drug_label_info", paralellize_rld_content_gen.run, ["generate_rld_content"])
rld_researcher_graph_builder.add_edge("generate_rld_content", END)

# Graph definition
rld_researcher_graph_memory = MemorySaver()
rld_researcher_graph_graph = rld_researcher_graph_builder.compile(checkpointer= rld_researcher_graph_memory)