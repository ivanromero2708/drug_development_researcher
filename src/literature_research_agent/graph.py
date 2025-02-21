from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from src.literature_research_agent.state import LiteratureResearchGraphState

from src.literature_research_agent.property_research_graph.graph import property_research_graph_builder

from .nodes import(
    GenerateSubQuestions,
    ExtractInformation,
    SearchExternalAPIs,
    ConsolidateReportAPI,
)

from .edges import(
    InitiatePropertyResearch,
)

generate_sub_questions = GenerateSubQuestions()
initiate_property_research = InitiatePropertyResearch()
consolidate_report_for_api = ConsolidateReportAPI()
extract_information = ExtractInformation()
search_external_APIs = SearchExternalAPIs()

# Add nodes and edges 
literature_researcher_graph_builder = StateGraph(LiteratureResearchGraphState)
literature_researcher_graph_builder.add_node("generate_sub_questions", generate_sub_questions.run)
literature_researcher_graph_builder.add_node("property_research", property_research_graph_builder.compile())
literature_researcher_graph_builder.add_node("consolidate_report_for_api", consolidate_report_for_api.run)
literature_researcher_graph_builder.add_node("extract_information", extract_information.run)
literature_researcher_graph_builder.add_node("search_external_APIs", search_external_APIs.run)

# Logic
literature_researcher_graph_builder.set_entry_point("search_external_APIs")
literature_researcher_graph_builder.add_edge("search_external_APIs", "generate_sub_questions")
literature_researcher_graph_builder.add_conditional_edges("generate_sub_questions", initiate_property_research.run, ["property_research"])
literature_researcher_graph_builder.add_edge("property_research", "consolidate_report_for_api")
literature_researcher_graph_builder.add_edge("consolidate_report_for_api", END)

literature_research_memory = MemorySaver()
literature_researcher_graph = literature_researcher_graph_builder.compile(checkpointer= literature_research_memory)