import unittest
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

# Import the compiled drug development graph and required state models.
from src.graph_final import drug_development_researcher_graph
from src.state import API, ProductInformation, DrugDevelopmentResearchGraphState
from src.configuration import Configuration

class TestDrugDevelopmentResearcherGraph(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Define the input document path (using a raw string to handle Windows backslashes).
        self.input_document_path = r"C:\Users\Ivan\OneDrive - Grupo Procaps\Portafolio NTF\26. GESTIÓN ab initio DE LA ESTABILIDAD\Documentos Ejemplos\Vonoprazan\9. DMI VONOPRAZAN.pdf"

        # Prepare the initial state for the graph execution.
        # Note: DrugDevelopmentResearchGraphState is defined as a TypedDict so we use a plain dictionary.
        self.test_state: DrugDevelopmentResearchGraphState = {
            "input_documents": [self.input_document_path],
            "apis_text_information": "Vonoprazan Fumarate in tablet in the oral rout of administration",
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
        async for event in self.graph.astream(self.test_state, thread_info, stream_mode="values", subgraphs=True):
            print(event)
        
        #state = self.graph.get_state(thread_info, subgraphs=True)
        #print(state.tasks[0])
        
        """
        TODO
        RLD SELECTION LOGIC FROM THE STATE
        
        user must be given these options:
        feedback_decision: Literal["retry_daily_med", "go_enrich_accept", "go_enrich_blank"]
        
        It must be listed the different potential RLDs per API, for the user to choose... the user selection must be returned to the graph in thr variable feedback_decision and the selection of the reference products must be given back in the updated state value for selected_RLDs: List[PotentialRLD]
        
         # We'll get the partial state
        partial_state = self.graph.get_state(thread_info).values
        potential_rlds = partial_state.get("potential_RLDs", [])
        apis = partial_state.get("apis", [])

        # Group potential RLDs by api_name
        rlds_by_api = defaultdict(list)
        for rld in potential_rlds:
            rlds_by_api[rld["api_name"]].append(rld)

        # Show them to the user. In a real app, you'd do an interactive prompt. 
        # Here, we just print and pick programmatically:

        print("\n*** Potential RLDs by API ***")
        chosen_rlds = []  # We'll store final picks here
        for api_obj in apis:
            api_name = api_obj["API_name"]
            possible_rlds = rlds_by_api.get(api_name, [])
            print(f"API: {api_name}")
            if not possible_rlds:
                print("  => No potential RLD found for this API.")
                # The user might skip or do blank, in that case we won't pick anything
                continue

            # Print them
            for i, rld_data in enumerate(possible_rlds):
                print(f"  [{i}] Title={rld_data['title']}, setid={rld_data['setid']}, image={rld_data['image_url']}")

            # For demonstration, let's pick index 0 for each API that has any
            # In a real scenario, you'd prompt the user or do some logic.
            pick_index = 0
            chosen_rld = possible_rlds[pick_index]
            print(f"  => Chosen index={pick_index}, setid={chosen_rld['setid']}")
            chosen_rlds.append(chosen_rld)

        # 4) Suppose the user wants to accept RLD => "go_enrich_accept"
        # If user wants blank => "go_enrich_blank"
        # If user wants to retry => "retry_daily_med"
        feedback_decision = "go_enrich_accept"

        # We'll store them in the state by calling update_state
        self.graph.update_state(
            thread_info,
            {
                "feedback_decision": feedback_decision,
                "selected_RLDs": chosen_rlds
            },
            as_node="formulator_feedback_product_research"  
        )

        # 5) Now resume the graph
        for event in self.graph.stream(None, thread_info, stream_mode="values"):
            events.append(event)
        """
        
        # Retrieve the final state from the graph.
        #final_state = self.graph.get_state(thread_info).values
        
        # Assert that 'input_documents' is present and has not been removed.
        #self.assertIn("input_documents", final_state)
        #self.assertGreater(len(final_state["input_documents"]), 0, "Expected non-empty input_documents.")
        #self.assertEqual(final_state["input_documents"][0], self.input_document_path,
        #                 "The input document path should be preserved in the state.")
        
        # Optionally, if your extract node adds processed data to the state (for example, under a key like 'extracted_information'),
        # you can add additional assertions here.
        # Example:
        # self.assertIn("extracted_information", final_state.get("context", {}))
        
        #print("\n✅ Final state after 'extract_input_information' node:")
        #print(final_state)

if __name__ == "__main__":
    unittest.main()
