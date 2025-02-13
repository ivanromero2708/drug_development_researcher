from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from src.literature_research_agent.state import LiteratureResearchGraphState
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration
from src.literature_research_agent.prompts import PROMPT_GENERATE_REPORT

class GenerateReport:
    def __init__(self):
        pass

    async def generate_report(self, state: LiteratureResearchGraphState, config: RunnableConfig) -> dict:
        
        API = state["API"]
        context = state["context"]
        api_external_APIkey_data = state["api_external_APIkey_data"]
        cas_number = api_external_APIkey_data.cas_number
        physical_description = api_external_APIkey_data.description
        solubility = api_external_APIkey_data.solubility
        melting_point = api_external_APIkey_data.melting_point
        iupac_name = api_external_APIkey_data.chemical_names
        molecular_formula = api_external_APIkey_data.molecular_formula
        molecular_weight = api_external_APIkey_data.molecular_weight
        logp = api_external_APIkey_data.log_p
        boiling_point=api_external_APIkey_data.boiling_point
        pka = api_external_APIkey_data.pka
        stability_conditions = api_external_APIkey_data.stability
        
        
        # Get configuration and initialize the LLM
        configurable = Configuration.from_runnable_config(config)
        llm = ChatOpenAI(model=configurable.o3mini, reasoning_effort="medium") 
        
        context = state["context"]
        # Título y fecha
        report_title = f"Pharmaceutical Research Report for {state['API'].API_name}"
        report_date = datetime.now().strftime('%B %d, %Y')

        # Human Instructions
        human_instructions = PROMPT_GENERATE_REPORT.format(
            API = API,
            context = context,
            cas_number = cas_number,
            description = physical_description,
            solubility = solubility,
            melting_point = melting_point,
            chemical_names = iupac_name,
            molecular_formula = molecular_formula,
            molecular_weight = molecular_weight,
            log_p = logp,
            boiling_point=boiling_point,
            pka = pka,
            stability_conditions = stability_conditions,
        )
        human_msg = HumanMessage(content = human_instructions)
        
        # System Instructions
        system_msg = SystemMessage(content = "Generate a detailed, fact-based Plain text report using the provided context.")
        
        try:
            response = await llm.ainvoke([system_msg, human_msg])
            markdown_content = response.content
            # Se añade el título y la fecha al informe final
            full_report = f"# {report_title}\n\n*{report_date}*\n\n{markdown_content}"
            return {
                "consolidated_research_report": full_report
            }
        except Exception as e:
            error_message = f"Error generating report: {str(e)}"
            return {
                "consolidated_research_report": f"# Error Generating Report\n\n*{report_date}*\n\n{error_message}"
            }

    async def run(self, state: LiteratureResearchGraphState, config: RunnableConfig):
        result = await self.generate_report(state, config)
        return result

