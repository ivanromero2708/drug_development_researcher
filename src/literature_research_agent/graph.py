from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from .state import LiteratureResearchGraphState

from research_process_graph.graph import research_process_builder
from .nodes import(
    GenerateSubQuestions,
    ConsolidateReport,
    ExtractInformation,
    ExtractInputInformation,
)
from .edges import (
    InitiateAllResearch,
)

extract_input_information = ExtractInputInformation()
generate_sub_questions = GenerateSubQuestions()
consolidate_report = ConsolidateReport()
extract_information = ExtractInformation()
initiate_all_research = InitiateAllResearch()

# Add nodes and edges 
literature_researcher_graph_builder = StateGraph(LiteratureResearchGraphState)
literature_researcher_graph_builder.add_node("extract_input_information", extract_input_information.run)
literature_researcher_graph_builder.add_node("generate_sub_questions", generate_sub_questions.run)
literature_researcher_graph_builder.add_node("research_process", research_process_builder.compile())
literature_researcher_graph_builder.add_node("consolidate_report", consolidate_report.run())
literature_researcher_graph_builder.add_node("extract_information", extract_information.run())

# Logic
literature_researcher_graph_builder.add_edge(START, "extract_input_information")
literature_researcher_graph_builder.add_edge("extract_input_information", "generate_sub_questions")
literature_researcher_graph_builder.add_conditional_edges("generate_sub_questions", initiate_all_research.run, ["research_process"])
literature_researcher_graph_builder.add_edge("research_process", "consolidate_report")
literature_researcher_graph_builder.add_edge("consolidate_report", "extract_information")
literature_researcher_graph_builder.add_edge("extract_information", END)