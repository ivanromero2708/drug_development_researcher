from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.patent_research_graph.state import PatentResearchGraphState, Perspectives, API
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration
from src.patent_research_graph.prompts import analyst_instructions
import os, getpass
from dotenv import load_dotenv
import unittest

load_dotenv()  # Cargar variables de entorno desde .env

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")

class CreateAnalysts:
    def __init__(self) -> None:
        pass

    def create_analysts(self, state: PatentResearchGraphState):
        """ Create analysts """
        api_obj = state["api"]
        
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0) 
        
        structured_llm = llm.with_structured_output(Perspectives)        

        # System message
        system_instructions = analyst_instructions.format(
            api_name = api_obj.API_name,
            api_desired_dosage_form = api_obj.desired_dosage_form,
            api_route_of_administration = api_obj.route_of_administration,
        )

        # Generate question 
        analysts = structured_llm.invoke([SystemMessage(content=system_instructions)]+[HumanMessage(content="Generate the set of analysts including each of their descriptions in an organized form.")])
        
        # Write the list of analysis to state
        return {"analysts": analysts}
    
    def run(self, state: PatentResearchGraphState):
        return self.create_analysts(state)


def main():
    state ={}
    state["api"] = API(API_name="Vonoprazan Fumarate", desired_dosage_form="TABLET", route_of_administration="oral")
    
    create_analysts = CreateAnalysts()
    result = create_analysts.run(state)
    print(f'Los analistas son:\n\n{result}')
    

if __name__ == "__main__":
    main()
