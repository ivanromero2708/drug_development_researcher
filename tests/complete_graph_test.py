import unittest
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

# Import the compiled drug development graph and required state models.
from src.graph import drug_development_researcher_graph
from src.state import API, ProductInformation, DrugDevelopmentResearchGraphState
from src.configuration import Configuration

class TestDrugDevelopmentResearcherGraph(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Define the input document path (using a raw string to handle Windows backslashes).
        self.input_document_path = r"C:\Users\Ivan\OneDrive - Grupo Procaps\Portafolio NTF\26. GESTIÓN ab initio DE LA ESTABILIDAD\Documentos Ejemplos\Dronabinol +Aceta\Unigel Dronabinol + Acetazolamida - SOW (STATEMENT OF WORK).pdf"

        # Prepare the initial state for the graph execution.
        # Note: DrugDevelopmentResearchGraphState is defined as a TypedDict so we use a plain dictionary.
        self.test_state: DrugDevelopmentResearchGraphState = {
            "input_documents": [self.input_document_path],
            "apis_text_information": "Dronabinol in Soft gelatin Capsules; Acetazolamide in tablets both in the ORAL route of administration",
            "is_rld_combination": "N",
            "is_supplement": "N",
            "apis": [],
            #"product_information": [],
            "api_literature_data": [],
            "patent_background_restrictions": "",
            "rld_packaging_descriptions": "",
            "context": {},
            "report_docx_dir_string": ""
        }
        
        # Create a dummy configuration (if needed by your nodes).
        self.config = RunnableConfig(configurable=Configuration())
        
        # Save a reference to the in-memory checkpoint and the compiled graph.
        self.memory = MemorySaver()
        self.graph = drug_development_researcher_graph

    async def test_extract_input_information(self):
        """
        Test the execution of the drug development graph.
        
        This test runs the graph (which begins at the START node, passes through
        'extract_input_information', and then ends) and asserts that the input
        document provided in the state is present in the final state.
        """
        thread_info = {"configurable": {"thread_id": "test_thread_1"}}
        events = []
        
        # Run the graph asynchronously.
        async for event in self.graph.astream(self.test_state, thread_info, stream_mode="values"):
            events.append(event)
        
        # Retrieve the final state from the graph.
        final_state = self.graph.get_state(thread_info).values
        
        # Assert that 'input_documents' is present and has not been removed.
        self.assertIn("input_documents", final_state)
        self.assertGreater(len(final_state["input_documents"]), 0, "Expected non-empty input_documents.")
        self.assertEqual(final_state["input_documents"][0], self.input_document_path,
                         "The input document path should be preserved in the state.")
        
        # Optionally, if your extract node adds processed data to the state (for example, under a key like 'extracted_information'),
        # you can add additional assertions here.
        # Example:
        # self.assertIn("extracted_information", final_state.get("context", {}))
        
        print("\n✅ Final state after 'extract_input_information' node:")
        print(final_state)

if __name__ == "__main__":
    unittest.main()
