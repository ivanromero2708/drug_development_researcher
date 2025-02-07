from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from .state import LiteratureResearchGraphState

#from research_process_graph.graph import research_process_builder
from .nodes import(
    GenerateSubQuestions,
    ConsolidateReport,
    ExtractInformation,
    TargetedWebSearch,
    ClusterRelatedDocs,
    EnrichDocuments,
    GenerateReport,
)

generate_sub_questions = GenerateSubQuestions()
consolidate_report = ConsolidateReport()
extract_information = ExtractInformation()
targeted_web_search = TargetedWebSearch()
cluster_related_docs = ClusterRelatedDocs()
enrich_documents = EnrichDocuments()
generate_report = GenerateReport()
extract_information = ExtractInformation()

# Add nodes and edges 
literature_researcher_graph_builder = StateGraph(LiteratureResearchGraphState)
literature_researcher_graph_builder.add_node("generate_sub_questions", generate_sub_questions.run)
literature_researcher_graph_builder.add_node("targeted_web_search", targeted_web_search.run)
literature_researcher_graph_builder.add_node("cluster_related_docs", cluster_related_docs.run)
literature_researcher_graph_builder.add_node("enrich_documents", enrich_documents.run)
literature_researcher_graph_builder.add_node("generate_report", generate_report.run)
literature_researcher_graph_builder.add_node("extract_information", extract_information.run)

# Logic
literature_researcher_graph_builder.add_edge(START, "generate_sub_questions")
literature_researcher_graph_builder.add_edge("generate_sub_questions", "targeted_web_search")
literature_researcher_graph_builder.add_edge("targeted_web_search", "cluster_related_docs")
literature_researcher_graph_builder.add_edge("cluster_related_docs", "enrich_documents")
literature_researcher_graph_builder.add_edge("enrich_documents", "generate_report")
literature_researcher_graph_builder.add_edge("generate_report", "extract_information")
literature_researcher_graph_builder.add_edge("extract_information", END)

literature_research_memory = MemorySaver()
literature_researcher_graph = literature_researcher_graph_builder.compile(checkpointer= literature_research_memory)