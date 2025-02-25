from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.patent_research_graph.state import PatentResearchGraphState, Perspectives
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration
from src.patent_research_graph.prompts import analyst_instructions


class CreateAnalysts:
    def __init__(self) -> None:
        pass

    def create_analysts(self, state: PatentResearchGraphState, config: RunnableConfig):
        """ Create analysts """
        api_obj = state["api"]
        
        # Get configuration and initialize the LLM
        configurable = Configuration.from_runnable_config(config)
        llm = ChatOpenAI(model=configurable.gpt4o, temperature=0) 
        
        structured_llm = llm.with_structured_output(Perspectives)        

        # System message
        system_instructions = analyst_instructions.format(
            api_name = api_obj.API_name,
            api_desired_dosage_form = api_obj.desired_dosage_form,
            api_route_of_administration = api_obj.route_of_administration,
        )

        # Generate question 
        analysts = structured_llm.invoke([SystemMessage(content=system_instructions)]+[HumanMessage(content="Generate the set of analysts.")])
        
        # Write the list of analysis to state
        return {"analysts": analysts.analysts}
    
    def run(self, state: PatentResearchGraphState, config: RunnableConfig):
        return self.create_analysts(state, config)
