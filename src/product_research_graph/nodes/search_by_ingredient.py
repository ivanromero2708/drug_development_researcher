from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration
from src.product_research_graph.state import ProductResearchGraphState
from src.state import RLD
from typing import List

class SearchByIngredient:
    def __init__(self):
        pass
    
    def search_by_ingredient(self, state: ProductResearchGraphState, config: RunnableConfig):
        # Prepare a list for final RLD objects
            rld_list: List[RLD] = []

            # For each API
            apis = state["apis"]  # list of API objects
            for api_obj in apis:
                api_name = api_obj.API_name
                dosage_form = api_obj.desired_dosage_form  # literal field
                route_of_admin = api_obj.route_of_administration

                # Build an RLD object
                rld_item = RLD(
                    api_name=api_name,
                    brand_name=api_name,
                    manufacturer="",
                    rld_dosage_form=dosage_form,
                    route_of_administration = route_of_admin,
                )
                rld_list.append(rld_item)

            # Return for convenience
            return {"RLDs": rld_list}
    
    def run (self, state: ProductResearchGraphState, config: RunnableConfig):
        return self.search_by_ingredient(state, config)