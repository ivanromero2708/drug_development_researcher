from src.state import RLDResearchData
from src.rld_research_graph.state import RLDResearchGraphState
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration

class ConsolidateRLDContext:
    def __init__(self):
        self.configurable = None
    
    def consolidate_RLD_context(self, state: RLDResearchGraphState, config: RunnableConfig):
        # Convertir la lista de PropertyReportSection en un diccionario que mapea la propiedad a su research_report
        rld_reports = {}
        for section in state["rld_research_report"]:
            rld_reports[section.rld_section] = section.research_report
        
        rld_name = state["RLD"].brand_name
        manufacturer = state["RLD"].manufacturer
        
        rld_research_data = RLDResearchData(
            API_name_with_UNII = rld_reports.get("API_name_with_UNII", ""),
            inactive_ingredients_with_UNII_str = rld_reports.get("inactive_ingredients_with_UNII_str", ""),
            type_pckg_material = rld_reports.get("type_pckg_material", ""),
            rld_how_supplied = rld_reports.get("rld_how_supplied", ""),
            rld_physical_characteristics = rld_reports.get("rld_physical_characteristics", ""),
            rld_special_characteristics = rld_reports.get("rld_special_characteristics", ""),
            rld_storage_conditions = rld_reports.get("rld_storage_conditions", ""),
            strengths = rld_reports.get("strengths", ""),
            brand_name = rld_name,
            manufacturer = manufacturer,
        )
        
        return {"rld_research_data": rld_research_data}
    
    def run(self, state: RLDResearchGraphState, config: RunnableConfig):
        return self.consolidate_RLD_context(state, config)