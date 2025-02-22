from langgraph.types import interrupt, Command
from langchain_core.runnables import RunnableConfig
from src.product_research_graph.state import ProductResearchGraphState

class FormulatorFeedbackProductResearch:
    def __init__(self):
        self.configurable = None

    def formulator_feedback_product_research(self, state: ProductResearchGraphState, config: RunnableConfig):
        """
        Implements human interruption logic after formulator feedback.
        It surfaces current potential RLDs along with instructions for possible actions:
          - "retry_api": Retry DailyMed search by replacing RLD brand name with API name (for selected APIs).
          - "retry_dosage": Retry with a new dosage form (requires a 'new_dosage_form' value and list of APIs).
          - "enrich" or "go_enrich_accept": Proceed to enrichment with approved RLDs.
        The node calls interrupt() to pause execution and returns a Command object
        with a goto and state update based on the human's input.
        """
        # Call interrupt to request human input. (The returned value should be a dict.)
        human_response = interrupt({
            "potentialRLDs": state.get("potential_RLDs", []),
            "instructions": (
                "Please choose an option:\n"
                "- Enter 'retry_api' to retry using API name instead of brand name.\n"
                "- Enter 'retry_dosage' to retry with a new dosage form (provide 'new_dosage_form').\n"
                "- Enter 'enrich' (or 'go_enrich_accept') to proceed to product enrichment "
                "with the selected RLDs.\n"
                "If applicable, also provide 'APIS_for_retry' (a list of API names) or 'selected_RLDs' (a list of RLDs)."
            )
        })

        # Extract the values from the human input dictionary.
        feedback_decision = human_response.get("feedback_decision")
        selected_RLDs = human_response.get("selected_RLDs", [])
        APIS_for_retry = human_response.get("APIS_for_retry", [])
        new_dosage_form = human_response.get("new_dosage_form", "")

        if feedback_decision == "retry_api":
            # Update each RLD: if its api_name is in APIS_for_retry, set brand_name to api_name.
            updated_RLDs = state.get("RLDs", [])
            for rld in updated_RLDs:
                if rld.api_name in APIS_for_retry:
                    rld.brand_name = rld.api_name
            return Command(goto="retry_api", update={"RLDs": updated_RLDs})
        elif feedback_decision == "retry_dosage":
            updated_RLDs = state.get("RLDs", [])
            for rld in updated_RLDs:
                if rld.api_name in APIS_for_retry:
                    rld.rld_dosage_form = new_dosage_form
            return Command(goto="retry_dosage", update={"RLDs": updated_RLDs})
        elif feedback_decision in ["enrich", "go_enrich_accept"]:
            return Command(goto=feedback_decision, update={"selected_RLDs": selected_RLDs})
        else:
            # Default case: if no valid option is provided, assume enrichment with no selection.
            return Command(goto="go_enrich_blank", update={"selected_RLDs": []})

    def run(self, state: ProductResearchGraphState, config: RunnableConfig):
        return self.formulator_feedback_product_research(state, config)
