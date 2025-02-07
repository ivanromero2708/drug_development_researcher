from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from ..state import LiteratureResearchGraphState
from langchain_core.runnables import RunnableConfig
from ...configuration import Configuration
from ..prompts import PROMPT_GENERATE_REPORT

class GenerateReport:
    def __init__(self):
        pass

    async def generate_report(self, state: LiteratureResearchGraphState, config: RunnableConfig) -> dict:
        
        API = state["API"]
        context = state["context"]
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
        )
        human_msg = HumanMessage(content = human_instructions)
        
        # System Instructions
        system_msg = SystemMessage(content = "Generate a detailed, fact-based Markdown report using the provided clusters of documents.")
        
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

# ----------------------------------------------------------------
# Código de test para verificar el nodo GenerateReport

if __name__ == "__main__":
    import asyncio
    from pydantic import BaseModel
    from typing import Dict, List

    # Modelos dummy para simular el estado (ajusta según la definición real de ResearchState)
    class DummyAPI(BaseModel):
        API_name: str

    class DummyProductInformation(BaseModel):
        product_dosage_form: str
        route_of_administration: str

    class DummyCluster(BaseModel):
        property: str
        cluster: List[str]

    # Simulación de clusters de documentos (resultado del clustering)
    dummy_clusters = [
        DummyCluster(property="polymorphs", cluster=["https://example.com/doc1", "https://example.com/doc2"]),
        DummyCluster(property="impurities", cluster=["https://example.com/doc2", "https://example.com/doc3"])
    ]

    # Simulación de documentos recuperados (este campo podría ser más complejo en la práctica)
    dummy_documents: Dict[str, str] = {
        "https://example.com/doc1": "Raw content from document 1 on polymorphs with inline citations.",
        "https://example.com/doc2": "Raw content from document 2 on impurities and stability indicators.",
        "https://example.com/doc3": "Raw content from document 3 on biopharmaceutical classification."
    }

    # Construir un estado dummy similar a ResearchState
    dummy_state: Dict = {
        "API": DummyAPI(API_name="Aspirin"),
        "product_information": DummyProductInformation(product_dosage_form="tablet", route_of_administration="oral"),
        "documents": dummy_documents,
        "document_clusters": dummy_clusters
    }

    # Configuración dummy (ajusta la ruta de Configuration según tu proyecto)
    from ...configuration import Configuration
    from langchain_core.runnables import RunnableConfig
    dummy_config = RunnableConfig(configurable=Configuration(number_of_queries=2, gpt4omini="gpt-4"))

    node = GenerateReport()
    result = asyncio.run(node.run(dummy_state))
    
    print("Generated Report:")
    print(result.get("report", ""))
