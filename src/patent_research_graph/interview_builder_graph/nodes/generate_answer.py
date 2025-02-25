from src.patent_research_graph.interview_builder_graph.prompts import answer_instructions
from src.patent_research_graph.interview_builder_graph.state import InterviewState
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration

class GenerateAnswer:
    def __init__(self) -> None:
        pass
    
    def generate_answer(self, state: InterviewState, config: RunnableConfig):
        """ Node to answer a question """

        # Get state
        analyst = state["analyst"]
        messages = state["messages"]
        context = state["context"]

        # Get configuration and initialize the LLM
        configurable = Configuration.from_runnable_config(config)
        llm = ChatOpenAI(model=configurable.gpt4omini, temperature=0) 
        
        # Answer question
        system_message = answer_instructions.format(goals=analyst.persona, context=context)
        answer = llm.invoke([SystemMessage(content=system_message)]+messages)
                
        # Name the message as coming from the expert
        answer.name = "expert"
        
        # Append it to state
        return {"messages": [answer]}
    
    def run(self, state: InterviewState, config: RunnableConfig):
        return self.generate_answer(state, config)
