from pydantic import BaseModel, Field
from typing import List

from typing import List, Literal
from pydantic import BaseModel, Field

# Define the structure for clustering output
class DocumentCluster(BaseModel):
    property: Literal[
        'polymorphs',
        'scheme_of_degradation_route',
        'stability_indicators',
        'impurities',
        'biopharmaceutical_classification',
        'hygroscopicity',
        'chirality_or_specific_optical_rotation',
        'glass_transition_temperature',
        'degradation_temperature',
        'rld_special_characteristics',
        'rld_manufacturing_process_info'
    ] = Field(
        ...,
        description="The name of the property these documents belong to."
    )
    cluster: List[str] = Field(
        ...,
        description="A list of URLs relevant to the identified property."
    )

class DocumentClusters(BaseModel):
    clusters: List[DocumentCluster] = Field(default_factory=list, description="List of document clusters")

class API(BaseModel):
    API_name: str = Field(
        ...,
        description="The name of the pharmaceutical active ingredient."
    )

# Define Input product information
class ProductInformation(BaseModel):
    """The information of the pharmaceutical product to be developed"""
    APIs: List[API] = Field(
        ...,
        description="The list of the pharmaceutical active ingredient names"
    )
    product_name: str = Field(
        ...,
        description="The pharmaceutical product name that includes the Active Pharmaceutical Ingredients, and the pharmaceutical dosage form. For example: ´´´Dronabinol + Acetazolamide Unigel´´´, OR ´´´Vonoprazan Tablets´´´"
    )
    product_type: str = Field(
        ...,
        description="The pharmaceutical product type that could be one of these: OTC, RX, Nutraceutic, Cosmetic, others"
    )
    generic_name: str = Field(
        ...,
        description="The name of a generic or brand product with the desired API"
    )    
    product_strength: str = Field(
        ...,
        description="The name of the APIs included in the product with their respective strengths. For example: ´´´Dronabinol 2.5 mg + Acetazolamide 125 mg Unigel; Dronabinol 5 mg + Acetazolamide 250 mg Unigel´´´"
    )
    product_dosage_form: str = Field(
        ...,
        description="The pharmaceutical product dosage form, that could be: tablets, softgels, unigels, syrups, among others"
    )
    route_of_administration: str = Field(
        ...,
        description="The pharmaceutical product route of administration, that includes: oral, topic, nasal, intragastric, vaginal, among others"
    )
    product_dose: str = Field(
        ...,
        description= "The desired product dose. If not available, could be replaced by a message indicating ´´´According to physician's prescription´´´"
    )
    physical_characteristics: str = Field(
        ...,
        description= "Color, shape, form or printing desired in the final version of the product"
    )
    packaging_type: str = Field(
        ...,
        description= "Desired secondary packaging specifications"
    )
    commercial_presentations: str = Field(
        ...,
        description= """The desired commercial presentation of the pharmaceutical product. It could be something like: ´´´Blister packs x 28 capsules´´´, ´´´VONOPRAZAM 10 mg TAB  CAJA X 30 und CIAL, VONOPRAZAM 20 mg TAB  CAJA X 30 und CIAL, 
        VONOPRAZAM 10 mg TAB  CAJA X 5 und MM, VONOPRAZAM 20 mg TAB  CAJA X 5 und MM ´´´"""
    )
    required_expiration_time: str = Field(
        ...,
        description = """Required expiration time for the pharmaceutical product to be developed in months or years."""
    )
    observations: str = Field(
        ...,
        description= "Additional observations for the pharmaceutical product to be developed"
    )
