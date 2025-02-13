from src.configuration import Configuration
from src.literature_research_agent.state import LiteratureResearchGraphState
from src.state import TavilySearchInput
from src.literature_research_agent.prompts import PROMPT_GENERATE_SUB_QUESTIONS
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

class GenerateSubQuestions:
    def __init__(self):
        pass
    
    def generate_sub_questions(self, state: LiteratureResearchGraphState, config: RunnableConfig):
        """
        Node: Generate subquestions from the given API, and the general product information and create queries for web search
        
        Inputs (state):
          - API: The name of the API
          - Product information: Product related information.
        
        Output:
          - queries: A list of queries
        """
        API = state["API"]
        product_information = state["product_information_child"]
        
        route_of_administration = product_information.route_of_administration
        
        # Get configuration and initialize the LLM.
        configurable = Configuration.from_runnable_config(config)
        number_of_queries = configurable.number_of_queries
        llm = ChatOpenAI(model=configurable.gpt4omini, temperature=0)
        structured_llm = llm.with_structured_output(TavilySearchInput)
                
        # Build the prompt using the provided metaprompt guidelines.
        system_instructions = PROMPT_GENERATE_SUB_QUESTIONS.format(
            API=API,
            route_of_administration = route_of_administration,
        )
        system_msg = SystemMessage(content=system_instructions)
        instruction_msg = HumanMessage(
            content="Generate the required search queries as instructed."
        )
        
        # model invoking
        result = structured_llm.invoke([system_msg, instruction_msg])

        # The result should be a DomainRelationshipsOutput instance.
        search_queries = result.sub_queries

        return {"search_queries": search_queries}
    
    def run(self, state: LiteratureResearchGraphState, config: RunnableConfig):
        return self.generate_sub_questions(state, config)
    