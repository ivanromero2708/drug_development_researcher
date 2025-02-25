from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from src.patent_research_graph.state import PatentResearchGraphState, PatentResearchOutputState
from src.patent_research_graph.edges.initiate_all_interviews import IniateAllInterviews


from .nodes import (
    CreateAnalysts,
    FinalizeReport,
    WriteConclusion,
    WriteIntroduction,
    WriteReport
)

from .interview_builder_graph.graph import (
    interview_builder,
)

create_analysts = CreateAnalysts()
write_report = WriteReport()
write_introduction = WriteIntroduction()
write_conclusion = WriteConclusion()
finalize_report = FinalizeReport()
initiate_all_interviews = IniateAllInterviews()

# Add nodes and edges 
patent_research_graph_builder = StateGraph(input = PatentResearchGraphState, output = PatentResearchOutputState)
patent_research_graph_builder.add_node("create_analysts", create_analysts.run)
patent_research_graph_builder.add_node("conduct_interview", interview_builder.compile())
patent_research_graph_builder.add_node("write_report",write_report.run)
patent_research_graph_builder.add_node("write_introduction",write_introduction.run)
patent_research_graph_builder.add_node("write_conclusion",write_conclusion.run)
patent_research_graph_builder.add_node("finalize_report",finalize_report.run)

# Logic
patent_research_graph_builder.add_edge(START, "create_analysts")
patent_research_graph_builder.add_conditional_edges("create_analysts", initiate_all_interviews.run, ["conduct_interview"])
patent_research_graph_builder.add_edge("conduct_interview", "write_report")
patent_research_graph_builder.add_edge("conduct_interview", "write_introduction")
patent_research_graph_builder.add_edge("conduct_interview", "write_conclusion")
patent_research_graph_builder.add_edge(["write_conclusion", "write_report", "write_introduction"], "finalize_report")
patent_research_graph_builder.add_edge("finalize_report", END)

# Compile
memory = MemorySaver()
patent_research_graph_graph = patent_research_graph_builder.compile(checkpointer=memory)