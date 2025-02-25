from langgraph.graph import END
from ..state import GenerateAnalystsState

class ShouldContinue:
    def should_continue(state: GenerateAnalystsState):
        """ Return the next node to execute """

        # Check if human feedback
        human_analyst_feedback=state.get('human_analyst_feedback', None)
        if human_analyst_feedback:
            return "create_analysts"
        
        # Otherwise end
        return END
    
    def run(self, state: GenerateAnalystsState):
        return self.should_continue(state)