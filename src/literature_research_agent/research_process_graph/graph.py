from langgraph.graph import START, END, StateGraph
from .state import ResearchProcessGraphState

from .nodes import (
    TargetedWebSearch,
    ClusterRelatedDocs,
    IdentifyCorrectClusters,
    EnrichDocuments,
    GenerateSubQueryReport,
)

# Node Initialization
targeted_web_search = TargetedWebSearch()
cluster_related_docs = ClusterRelatedDocs()
identify_correct_clusters = IdentifyCorrectClusters()
enrich_documents = EnrichDocuments()
generate_sub_query_report = GenerateSubQueryReport()

# Create Graph Nodes
research_process_builder = StateGraph(ResearchProcessGraphState)
research_process_builder.add_node("targeted_web_search", targeted_web_search.run)
research_process_builder.add_node("cluster_related_docs", cluster_related_docs.run)
research_process_builder.add_node("identify_correct_clusters", identify_correct_clusters.run)
research_process_builder.add_node("enrich_documents", enrich_documents.run)
research_process_builder.add_node("generate_sub_query_report", generate_sub_query_report.run)

# Logic
research_process_builder.add_edge(START, "targeted_web_search")
research_process_builder.add_edge("targeted_web_search", "cluster_related_docs")
research_process_builder.add_edge("cluster_related_docs", "identify_correct_clusters")
research_process_builder.add_edge("identify_correct_clusters", "enrich_documents")
research_process_builder.add_edge("enrich_documents", "generate_sub_query_report")
research_process_builder.add_edge("generate_sub_query_report", END)