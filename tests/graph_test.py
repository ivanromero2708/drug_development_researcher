import unittest
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig
from src.literature_research_agent.graph import literature_researcher_graph
from src.literature_research_agent.state import LiteratureResearchGraphState, API, ProductInformation
from src.configuration import Configuration

class TestLiteratureResearchGraphBreakpoints(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """Set up the test with a complete graph execution after a specified node."""
        
        # Create a dummy API instance.
        self.api = API(API_name="Aspirin")

        # Create dummy ProductInformation with required fields.
        self.product_information = ProductInformation(
            APIs=[self.api],
            product_name="Aspirin Tablets",
            product_type="OTC",
            generic_name="Acetylsalicylic Acid",
            product_strength="500 mg",
            product_dosage_form="tablet",
            route_of_administration="oral",
            product_dose="500 mg",
            physical_characteristics="round, white",
            packaging_type="blister pack",
            commercial_presentations="Box of 20 tablets",
            required_expiration_time="24 months",
            observations="No additional observations"
        )

        # Initialize the LiteratureResearchGraphState with all required keys.
        self.test_state = LiteratureResearchGraphState(
            API=self.api,
            product_information=self.product_information,
            search_queries=[],  # This should be filled after "generate_sub_questions" runs
            documents={},  # This will be filled after "targeted_web_search"
            document_clusters=[],
            chosen_clusters=[],
            context="",
            consolidated_research_report="",
            apis_literature_data=[]
        )

        # Create a dummy configuration.
        self.config = RunnableConfig(configurable=Configuration())

        # Reference the compiled literature researcher graph.
        self.memory = MemorySaver()

        # **Modify the graph to interrupt after "generate_sub_questions"**
        self.graph = literature_researcher_graph

    async def test_graph_execution_after_node(self):
        """Test the execution of the graph starting after 'generate_sub_questions' and ensuring web search execution."""

        # Run the graph until the specified breakpoint.
        thread_info = {"configurable": {"thread_id": "test_thread_1"}}
        events = []
        
        async for event in self.graph.astream(self.test_state, thread_info, stream_mode="values"):
            events.append(event)

        # Get the state at the first breakpoint.
        current_state = self.graph.get_state(thread_info).values

        # **Ensure "search_queries" were generated successfully**
        self.assertIn("search_queries", current_state)
        self.assertGreater(len(current_state["search_queries"]), 0, "Expected non-empty search queries.")

        print("\n✅ Breakpoint state (after 'generate_sub_questions' node):")
        print(current_state)

if __name__ == "__main__":
    unittest.main()
