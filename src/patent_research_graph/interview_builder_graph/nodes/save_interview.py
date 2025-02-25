from src.patent_research_graph.interview_builder_graph.state import InterviewState
from langchain_core.messages import get_buffer_string
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration

class SaveInterview:
    def __init__(self) -> None:
        pass
    
    def save_interview(self, state: InterviewState, config: RunnableConfig):        
        """ Save interviews """

        # Get messages
        messages = state["messages"]
        
        # Convert interview to a string
        interview = get_buffer_string(messages)
        
        # Save to interviews key
        return {"interview": interview}
    
    def run(self, state: InterviewState, config: RunnableConfig):
        return self.save_interview(state, config)
