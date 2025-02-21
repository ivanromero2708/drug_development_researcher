from typing import TypedDict, List, Literal, Annotated
from src.state import API, RLD, ProductResearchData, PotentialRLD, ProductReportSection
import operator
from pydantic import BaseModel

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

class DailyMedResearchGraphState(TypedDict):
    RLD: RLD
    potential_RLDs: Annotated[List[PotentialRLD], operator.add]

class ProductResearchGraphState(TypedDict):
    apis: List[API]
    is_rld_combination: Literal["Y", "N"]
    is_supplement: Literal["Y", "N"]
    
    RLDs: List[RLD]
    potential_RLDs: Annotated[List[PotentialRLD], operator.add]
    
    feedback_decision: Literal["retry_daily_med", "go_enrich_accept", "go_enrich_blank"]
    selected_RLDs: List[PotentialRLD]
        
    drug_label_doc: DrugLabelDoc
    
    product_research_report: Annotated[List[ProductReportSection], operator.add]
    product_research_data: Annotated[List[ProductResearchData], operator.add]
    
class ProductResearchOutputState(TypedDict):
    potential_RLDs: Annotated[List[PotentialRLD], operator.add]
    feedback_decision: Literal["retry_daily_med", "go_enrich_accept", "go_enrich_blank"]
    selected_RLDs: List[PotentialRLD]
    product_research_report: Annotated[List[ProductReportSection], operator.add]
    product_research_data: Annotated[List[ProductResearchData], operator.add]