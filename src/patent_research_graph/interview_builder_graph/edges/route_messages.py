from ..state import InterviewState
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration

class RouteMessages:
    def __init__(self) -> None:
        pass
    
    def route_messages(self, state: InterviewState, config: RunnableConfig, name: str = "expert"):
        """ Route between question and answer """
        # Max number of turns
        configurable = Configuration.from_runnable_config(config)
        max_num_turns_interview_patent = configurable.max_num_turns_interview_patent
        # Get messages
        messages = state["messages"]

        # Check the number of expert answers 
        num_responses = len(
            [m for m in messages if isinstance(m, AIMessage) and m.name == name]
        )

        # End if expert has answered more than the max turns
        if num_responses >= max_num_turns_interview_patent:
            return 'save_interview'

        # This router is run after each question - answer pair 
        # Get the last question asked to check if it signals the end of discussion
        last_question = messages[-2]
        
        if "Thank you so much for your help" in last_question.content:
            return 'save_interview'
        return "ask_question"
    
    def run(self, state: InterviewState, config: RunnableConfig, name: str = "expert"):
        return self.route_messages(state, config, name)
