from typing import TypedDict, List, Annotated, Dict, Union, Optional, Literal
from pydantic import BaseModel, Field
import operator
from src.state import RLDReportSection, API, ProductInformation, RLD, RLDResearchData, PotentialRLD
from src.product_research_graph.state import ProductResearchData, ProductReportSection

class InactiveIngredientwithUNII(BaseModel):
    commercial_presentation: str = Field(..., description = "Commercial presentation of the product.")
    inactive_ingredient: str = Field(..., description = "The name of the inactive ingredient.")
    route_of_administration: str = Field(..., description = "The route of administraion of the product.")
    cas_number: str = Field(..., description = "The CAS number of the inactive ingredient.")
    UNII: str = Field(..., description = "The Unique Ingredient Identifier of the Inactive Ingredient.")
    MDE: str = Field(..., description = "The Maximum Daily Exposure recommended on the IIG FDA database for the inactive ingredient.")

class DrugLabelDoc(BaseModel):
    indications_usage: str
    dosage_administration: str
    dosage_forms_strengths: str
    contraindications: str
    warnings_precautions: str
    adverse_reactions: str
    drug_interactions: str
    use_specific_populations: str
    overdosage: str
    description: str
    clinical_pharmacology: str
    nonclinical_toxicology: str
    clinical_studies: str
    how_supplied_storage_handling: str
    patient_counseling: str
    product_info_str: str

class ProductEnrichmentGraphState(TypedDict):
    selected_RLD: PotentialRLD
        
    drug_label_doc: DrugLabelDoc
    
    product_research_report: Annotated[List[ProductReportSection], operator.add]
    product_research_data: Annotated[List[ProductResearchData], operator.add]

class ProductEnrichmentOutputState(TypedDict):
    product_research_report: Annotated[List[ProductReportSection], operator.add]
    product_research_data: Annotated[List[ProductResearchData], operator.add]

class GenerateProductContentGraphState(TypedDict):
    selected_RLD: PotentialRLD
    drug_label_doc: DrugLabelDoc
    product_report_section: str
    product_research_data: Annotated[List[RLDReportSection], operator.add]

















class RLDResearchGraphState(TypedDict):
    RLD: RLD
    
    drug_label_doc: DrugLabelDoc
    rld_research_report: Annotated[List[RLDReportSection], operator.add]
    
    rld_research_data: Annotated[List[RLDResearchData], operator.add]
    
    brand_name: str
#    pckg_lagel_img: str
    manufacturer: str
    #inactive_ingredients_with_UNII: List[InactiveIngredientwithUNII]

class RLDResearchOutputState(TypedDict):
    rld_research_report: Annotated[List[RLDReportSection], operator.add] 
    rld_research_data: Annotated[List[RLDResearchData], operator.add]   
    brand_name: str
#    pckg_lagel_img: str
    manufacturer: str

class GenerateRLDContentGraphState(TypedDict):
    RLD: RLD
    drug_label_doc: DrugLabelDoc
    rld_report_section: str
    rld_section_research_report: Annotated[List[RLDReportSection], operator.add]
