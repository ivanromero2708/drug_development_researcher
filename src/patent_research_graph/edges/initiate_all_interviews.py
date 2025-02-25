from src.patent_research_graph.state import PatentResearchGraphState
from langchain_core.messages import HumanMessage
from langgraph.constants import Send

class IniateAllInterviews:
    def __init__(self) -> None:
        pass
    
    def initiate_all_interviews(self, state: PatentResearchGraphState):
        """ This is the "map" step where we run each interview sub-graph using Send API """    
        api_name = state["api"].API_name
        return [Send(
            "conduct_interview", 
            {
                "analyst": analyst,
                "messages": [HumanMessage(
                                          content=f"So you said you were writing a Patent research report on {api_name}??"
                                        )]
                }
            ) for analyst in state["analysts"]
                ]
    
    def run(self, state: PatentResearchGraphState):
        result = self.initiate_all_interviews(state)
        return result