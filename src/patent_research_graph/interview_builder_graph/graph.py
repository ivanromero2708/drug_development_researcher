from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from .state import InterviewState

from .nodes import (
    GenerateQuestion,
    SearchWeb,
    GenerateAnswer,
    SaveInterview,
    WriteSection,
)

from .edges import (
    RouteMessages,    
)

generate_question = GenerateQuestion()
search_web = SearchWeb()
generate_answer = GenerateAnswer()
save_interview = SaveInterview()
write_section = WriteSection()
route_messages = RouteMessages()

# Add nodes and edges 
interview_builder = StateGraph(InterviewState)
interview_builder.add_node("ask_question", generate_question.run)
interview_builder.add_node("search_web", search_web.run)
interview_builder.add_node("answer_question", generate_answer.run)
interview_builder.add_node("save_interview", save_interview.run)
interview_builder.add_node("write_section", write_section.run)

# Flow
interview_builder.add_edge(START, "ask_question")
interview_builder.add_edge("ask_question", "search_web")
interview_builder.add_edge("search_web", "answer_question")
interview_builder.add_conditional_edges("answer_question", route_messages.run,['ask_question','save_interview'])
interview_builder.add_edge("save_interview", "write_section")
interview_builder.add_edge("write_section", END)

# Interview 
memory = MemorySaver()
interview_graph = interview_builder.compile(checkpointer=memory).with_config(run_name="Conduct Interviews")