from langgraph.types import interrupt, Command
from langchain_core.runnables import RunnableConfig
from src.product_research_graph.state import ProductResearchGraphState

class FormulatorFeedbackProductResearch:
    def __init__(self):
        self.configurable = None

    def formulator_feedback_product_research(self, state: ProductResearchGraphState, config: RunnableConfig):
        """
        This node implements human interruption logic after the formulator’s feedback.
        It presents the current potential RLDs along with instructions for possible actions:
          - "retry_api": Replace RLD brand_name with API name (for selected APIs).
          - "retry_dosage": Retry with a new dosage form (requires a 'new_dosage_form' value and list of APIs).
          - "enrich" (or "go_enrich_accept"): Proceed to enrichment with approved RLDs.
        The node calls interrupt() to pause execution and returns a Command with both a goto route and a state update.
        """
        # Call interrupt to request human input.
        # (The returned value should be a dictionary with keys such as "feedback_decision", etc.)
        human_response = interrupt({
            "potential_RLDs": state.get("potential_RLDs", []),
            "RLDs": state.get("RLDs", []),
            "instructions": (
                "Please choose an option:\n"
                "- Enter 'retry_api' to retry using the API name instead of the brand name.\n"
                "- Enter 'retry_dosage' to retry with a new dosage form (provide 'new_dosage_form').\n"
                "- Enter 'enrich' (or 'go_enrich_accept') to proceed to product enrichment with the selected RLDs.\n"
                "If applicable, also provide 'APIS_for_retry' (a comma‐separated list of API names) or "
                "'selected_RLDs' (a list of RLDs)."
            )
        })

        # Extract values from the human response
        feedback_decision = human_response.get("feedback_decision")

        if feedback_decision == "retry_api":
            return Command(goto="parallelization_op_node", update={"RLDs": human_response.get("RLDs", []), "feedback_decision": "retry_daily_med"})
        
        elif feedback_decision == "retry_dosage":
            updated_RLDs = human_response.get("RLDs", [])
            return Command(goto="parallelization_op_node", update={"RLDs": human_response.get("RLDs", []), "feedback_decision": "retry_daily_med"})
        
        elif feedback_decision in ["enrich_as_is", "enrich_selected"]:
            updated_RLDs = human_response.get("RLDs", [])
            return Command(goto="parallelization_op_node", update={"selected_RLDs": human_response.get("selected_RLDs", []), "feedback_decision": "go_enrich_accept"})
        
    def run(self, state: ProductResearchGraphState, config: RunnableConfig):
        return self.formulator_feedback_product_research(state, config)
