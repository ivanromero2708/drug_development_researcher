from src.state import ProductResearchData
from src.product_research_graph.product_enrichment_graph.state import ProductEnrichmentGraphState
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration

class ConsolidateRLDContext:
    def __init__(self):
        self.configurable = None
    
    def consolidate_RLD_context(self, state: ProductEnrichmentGraphState, config: RunnableConfig):
        # Convertir la lista de PropertyReportSection en un diccionario que mapea la propiedad a su research_report
        rld_reports = {}
        for section in state["product_research_data"]:
            rld_reports[section.product_report_section] = section.research_report
        
        rld_name = state["selected_RLD"].brand_name
        manufacturer = state["selected_RLD"].manufacturer
        
        product_research_data = ProductResearchData(
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
        
        return {"product_research_report": [product_research_data]}
    
    def run(self, state: ProductEnrichmentGraphState, config: RunnableConfig):
        return self.consolidate_RLD_context(state, config)