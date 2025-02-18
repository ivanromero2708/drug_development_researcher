from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration
from src.state import DrugDevelopmentResearchGraphState, RLD
from typing import List

class SupplementDailyMedResearch:
    def __init__(self):
        pass
    
    def supplement_daily_med_research(self, state: DrugDevelopmentResearchGraphState, config: RunnableConfig):
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
    
    def run (self, state: DrugDevelopmentResearchGraphState, config: RunnableConfig):
        return self.supplement_daily_med_research(state, config)