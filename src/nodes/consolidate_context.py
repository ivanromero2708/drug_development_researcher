import json
from src.configuration import Configuration
from src.state import DrugDevelopmentResearchGraphState
from langchain_core.runnables import RunnableConfig

class ConsolidateContext:
    def __init__(self):
        self.configurable = None
    
    def consolidate_context(self, state: DrugDevelopmentResearchGraphState, config: RunnableConfig):
        # Convertir product_information a JSON (esto ya devuelve una cadena JSON)
        product_information_json = state["product_information"].model_dump_json()
        
        # Convertir cada objeto APILiteratureData a dict y luego serializar la lista a JSON
        api_literature_list = [api.model_dump() for api in state["literature_research_api_data"]]
        api_literature_json = json.dumps(api_literature_list)

        # Convertir cada objeto RLDResearchData a dict y luego serializar la lista a JSON
        rld_research_list = [rld.model_dump() for rld in state["product_research_report"]]
        rld_research_json = json.dumps(rld_research_list)
        
        # Convertir cada objeto RLDResearchData a dict y luego serializar la lista a JSON
        patent_research_list = [patent.model_dump() for patent in state["patent_research_report"]]
        patent_research_json = json.dumps(patent_research_list)
        
        combined_context = {
            "product_information": json.loads(product_information_json),
            "api_literature_data": json.loads(api_literature_json),
            "rld_research_data": json.loads(rld_research_json),
            "patent_research_data": json.loads(patent_research_json),
        }
        context_for_tpl = json.dumps(combined_context)
        
        return {"context_for_tpl": context_for_tpl}
    
    def run(self, state, config):
        return self.consolidate_context(state, config)
