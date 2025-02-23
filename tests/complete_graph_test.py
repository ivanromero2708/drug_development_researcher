import unittest
import asyncio
import os
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command  # per docs
from src.graph_final import drug_development_researcher_graph
from src.state import API, ProductInformation, DrugDevelopmentResearchGraphState, PotentialRLD
from src.configuration import Configuration

class TestDrugDevelopmentResearcherGraphCLI(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Define the input document path (real or dummy for testing)
        self.input_document_path = r"C:\Users\Ivan\OneDrive - Grupo Procaps\Portafolio NTF\16 - I&D 4.0\2. Investigación de Literatura - Degradación de APIs\1.2 MVP\Documentos Ejemplos\Dronabinol +Aceta\Unigel Dronabinol + Acetazolamida - SOW (STATEMENT OF WORK).pdf"
        # Initialize state with realistic apis_text_information and add dummy PotentialRLD data.
        self.test_state: DrugDevelopmentResearchGraphState = {
            "input_documents": [self.input_document_path],
            "apis_text_information": "Dronabinol in Soft gelatin capsules, and Acetazolamide in tablet. Both in the oral route of administration.",
            "is_rld_combination": "N",
            "is_supplement": "N",
            "apis": [],
            "api_literature_data": [],
            "patent_background_restrictions": "",
            "rld_packaging_descriptions": "",
            "context": {},
            "report_docx_dir_string": "",
        }
        self.config = RunnableConfig(configurable=Configuration())
        self.memory = MemorySaver()
        self.graph = drug_development_researcher_graph

    async def test_cli_human_interaction(self):
        """
        This test runs the full drug development graph until the human feedback node (FormulatorFeedbackProductResearch)
        triggers an interrupt. Then it prompts you on the CLI for your decision, updates the graph state, and resumes execution.
        """
        thread_info = {"configurable": {"thread_id": "cli_test_thread"}}
        events = []
        interrupt_payload = None

        # Run the graph until an interrupt is reached.
        async for event in self.graph.astream(self.test_state, thread_info, stream_mode="updates"):
            print("=" * 60)
            print(event)
            print("=" * 60)
        
        interrupt_payload = event["__interrupt__"]
        
        potential_RLDs_interrupted_raw = interrupt_payload[0].value["potential_RLDs"]
        flat_potential_RLDs = [rld for sublist in potential_RLDs_interrupted_raw for rld in sublist]
        
        current_RLDs = interrupt_payload[0].value["RLDs"]
        
        # Display available potential RLDs nicely.
        print("=== Available Reference Products ===")
        for i, rld in enumerate(flat_potential_RLDs):
            print(f"[{i}] Title: {rld.title}")
            print(f"     API: {rld.api_name}")
            print(f"     Brand: {rld.brand_name}")
            print(f"     Manufacturer: {rld.manufacturer}")
            print(f"     SetID: {rld.setid}\n")
        print("====================================")
        
        # Prompt the user for a decision.
        print("Graph paused at human feedback node. Please provide your decision.")
        feedback_decision = input("Enter feedback decision (retry_api, retry_dosage, enrich_as_is, or enrich_selected): ").strip()
        
        # If the decision is "enrich", proceed with all potential RLDs.     
        if feedback_decision == "enrich_as_is":
            human_response = {
                "feedback_decision": "enrich_as_is",
                "selected_RLDs": flat_potential_RLDs,
            }
                
        # If the decision is "enrich_selected", display the potential_RLDs and allow selection.
        elif feedback_decision == "enrich_selected":
            # Mostrar los potenciales RLD (ya se hicieron arriba) y solicitar índices.
            selected_indexes_input = input("Enter the index values for the reference products sepparated by comma: ").strip()
            try:
                selected_indexes = [int(idx.strip()) for idx in selected_indexes_input.split(",") if idx.strip().isdigit()]
            except ValueError:
                print("Invalid input, no selected reference products.")
                selected_indexes = []
            selected_RLDs = [flat_potential_RLDs[i] for i in selected_indexes if i < len(flat_potential_RLDs)]
            
            human_response = {
                "feedback_decision": "enrich_selected",
                "selected_RLDs": selected_RLDs
            }
        
        # If the decision is "retry_dosage", prompt for API names and new dosage forms.
        elif feedback_decision == "retry_dosage":
            # Prompt for API names to update (comma separated)
            apis_retry_input = input("Enter the API names to change dosage form (comma separated): ").strip()
            api_names = [api.strip() for api in apis_retry_input.split(",") if api.strip()]
            
            # For each API, prompt for the new dosage form and build a mapping.
            new_dosage_mapping = {}
            for api in api_names:
                new_dosage = input(f"Enter new dosage form for API '{api}': ").strip()
                new_dosage_mapping[api] = new_dosage

            # Modify the existing RLDs (update dosage form for matching APIs)
            for rld in current_RLDs:
                if rld.api_name in new_dosage_mapping:
                    rld.rld_dosage_form = new_dosage_mapping[rld.api_name]
                    
            # Store the modified RLDs in the human response.
            human_response = {
                "feedback_decision": "retry_dosage",
                "RLDs": current_RLDs
            }
        
        # If the decision is "retry_api", prompt for API names and reset brand names.
        elif feedback_decision == "retry_api":
            # Prompt for the API names (comma separated) for which the brand name should be reset.
            apis_retry_input = input("Enter the API names to retry (comma separated): ").strip()
            api_names = [api.strip() for api in apis_retry_input.split(",") if api.strip()]

            # Modify the existing RLDs (update brand_name for matching APIs)
            for rld in current_RLDs:
                if rld.api_name in api_names:
                    rld.brand_name = rld.api_name
            
            # Return the updated list in the human response.
            human_response = {
                "feedback_decision": "retry_api",
                "RLDs": current_RLDs  # Use the modified list.
            }
        
        # Use a while loop to allow replay until a final decision is reached.
        # We assume that only "enrich_as_is" or "enrich_selected" are final decisions.
        while human_response["feedback_decision"] not in ["enrich_as_is", "enrich_selected"]:
            print("Graph will replay with your current decision.")
            async for event in self.graph.astream(Command(resume=human_response), thread_info, stream_mode="updates"):
                print("=" * 60)
                print(event)
                print("=" * 60)
            
            interrupt_payload = event["__interrupt__"]
            # Update the potential RLDs from the last event.
            potential_RLDs_interrupted_raw = interrupt_payload[0].value["potential_RLDs"]
            flat_potential_RLDs = [rld for sublist in potential_RLDs_interrupted_raw for rld in sublist]
            
            current_RLDs = interrupt_payload[0].value["RLDs"]
            
            # Show updated potential RLDs.
            print("=== Updated Available Reference Products ===")
            for i, rld in enumerate(flat_potential_RLDs):
                print(f"[{i}] Title: {rld.title}")
                print(f"     API: {rld.api_name}")
                print(f"     Brand: {rld.brand_name}")
                print(f"     Manufacturer: {rld.manufacturer}")
                print(f"     SetID: {rld.setid}\n")
            print("====================================")
            # Prompt again.
            new_decision = input("Enter feedback decision (retry_api, retry_dosage, enrich_as_is, or enrich_selected): ").strip()

            if new_decision == "enrich_as_is":
                human_response = {
                    "feedback_decision": "enrich_as_is",
                    "selected_RLDs": flat_potential_RLDs,
                }
            
            elif new_decision == "enrich_selected":
                selected_indexes_input = input("Enter the index values for the reference products separated by comma: ").strip()
                try:
                    selected_indexes = [int(idx.strip()) for idx in selected_indexes_input.split(",") if idx.strip().isdigit()]
                except ValueError:
                    print("Invalid input, no reference products selected.")
                    selected_indexes = []
                selected_RLDs = [flat_potential_RLDs[i] for i in selected_indexes if i < len(flat_potential_RLDs)]
                
                human_response = {
                    "feedback_decision": "enrich_selected",
                    "selected_RLDs": selected_RLDs
                }
            
            elif new_decision == "retry_dosage":
                apis_retry_input = input("Enter the API names to change dosage form (comma separated): ").strip()
                api_names = [api.strip() for api in apis_retry_input.split(",") if api.strip()]
                new_dosage_mapping = {}
                for api in api_names:
                    new_dosage = input(f"Enter new dosage form for API '{api}': ").strip()
                    new_dosage_mapping[api] = new_dosage
                human_response["APIS_for_retry"] = api_names
                human_response["new_dosage_form"] = new_dosage_mapping
                for rld in current_RLDs:
                    if rld.api_name in new_dosage_mapping:
                        rld.rld_dosage_form = new_dosage_mapping[rld.api_name]
                        
                human_response = {
                    "feedback_decision": "retry_dosage",
                    "RLDs": current_RLDs
                }
                
            elif new_decision == "retry_api":
                apis_retry_input = input("Enter the API names to retry (comma separated): ").strip()
                api_names = [api.strip() for api in apis_retry_input.split(",") if api.strip()]
                human_response["APIS_for_retry"] = api_names
                for rld in current_RLDs:
                    if rld.api_name in api_names:
                        rld.brand_name = rld.api_name
                
                # Return the updated list in the human response.
                human_response = {
                    "feedback_decision": "retry_api",
                    "RLDs": current_RLDs  # Use the modified list.
                }

        print("Final human response:")
        print(human_response)
        
        # Resume execution using Command(resume=human_response)
        resumed_events = []
        async for event in self.graph.astream(Command(resume=human_response), thread_info, stream_mode="updates"):
            resumed_events.append(event)
        print("Resumed events:")
        print(resumed_events)
        
        #final_state = self.graph.get_state(thread_info).values
        #print("Final state:")
        #print(final_state)

        # Basic assertions for testing purposes.
        #self.assertEqual(final_state.get("feedback_decision"), human_response["feedback_decision"])
        #if human_response["feedback_decision"] in ["enrich", "go_enrich_accept", "enrich_as_is", "enrich_selected"]:
        #    self.assertGreater(len(final_state.get("selected_RLDs", [])), 0)
        #self.assertIn(self.input_document_path, final_state.get("input_documents", []))

if __name__ == "__main__":
    unittest.main()