from src.literature_research_agent.state import LiteratureResearchGraphState, APILiteratureResearchData
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration

class ConsolidateReportAPI:
    def __init__(self):
        self.configurable = None
    
    def consolidate_report_for_api(self, state: LiteratureResearchGraphState, config: RunnableConfig):
        api_external_APIkey_data = state["api_external_APIkey_data"]
       
        # Convertir la lista de PropertyReportSection en un diccionario que mapea la propiedad a su research_report
        property_reports = {}
        for section in state["api_research_property_report"]:
            property_reports[section.property] = section.research_report
        
        API = state["API"].API_name
        
        api_literature_data = APILiteratureResearchData(
            api_name=API,
            cas_number=api_external_APIkey_data.cas_number,
            pka=api_external_APIkey_data.pka,
            stability=api_external_APIkey_data.stability,
            solubility=api_external_APIkey_data.solubility,
            melting_point=api_external_APIkey_data.melting_point,
            chemical_names=api_external_APIkey_data.chemical_names,
            molecular_formula=api_external_APIkey_data.molecular_formula,
            molecular_weight=api_external_APIkey_data.molecular_weight,
            log_p=api_external_APIkey_data.log_p,
            boiling_point=api_external_APIkey_data.boiling_point,
            # Asignar valores a partir de property_reports; si no existe, se usa cadena vacía.
            polymorphs=property_reports.get("polymorphs", ""),
            scheme_of_degradation_route=property_reports.get("scheme_of_degradation_route", ""),
            stability_indicators=property_reports.get("stability_indicators", ""),
            impurities=property_reports.get("impurities", ""),
            biopharmaceutical_classification=property_reports.get("biopharmaceutical_classification", ""),
            hygroscopicity=property_reports.get("hygroscopicity", ""),
            chirality_or_specific_optical_rotation=property_reports.get("chirality_or_specific_optical_rotation", ""),
            glass_transition_temperature=property_reports.get("glass_transition_temperature", ""),
            degradation_temperature=property_reports.get("degradation_temperature", ""),
            # Asegúrate de asignar un valor al campo "description"
            description=api_external_APIkey_data.description,
        )
        
        return {"literature_research_api_data": [api_literature_data]}
    
    def run(self, state: LiteratureResearchGraphState, config: RunnableConfig):
        return self.consolidate_report_for_api(state, config)
