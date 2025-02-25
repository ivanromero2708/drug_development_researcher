from src.patent_research_graph.interview_builder_graph.state import InterviewState


from ..prompts import question_instructions
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration

class GenerateQuestion:
    def __init__(self) -> None:
        pass

    def generate_question(self, state: InterviewState, config: RunnableConfig):
        """ Node to generate a question """
        # Get state
        analyst = state["analyst"]
        messages = state["messages"]
        
        # Get configuration and initialize the LLM
        configurable = Configuration.from_runnable_config(config)
        llm = ChatOpenAI(model=configurable.gpt4omini, temperature=0) 

        # Generate question 
        system_message = question_instructions.format(goals=analyst.persona)
        question = llm.invoke([SystemMessage(content=system_message)]+messages)
            
        # Write messages to state
        return {"messages": [question]}
    
    def run(self, state:InterviewState, config: RunnableConfig):
        return self.generate_question(state, config)
