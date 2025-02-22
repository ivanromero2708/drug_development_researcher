import unittest
import asyncio
import os
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command  # Use Command from langgraph.types as per docs
from src.graph_final import drug_development_researcher_graph
from src.state import API, ProductInformation, DrugDevelopmentResearchGraphState
from src.configuration import Configuration

class TestDrugDevelopmentResearcherGraphCLI(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Define the input document path (real or dummy for testing)
        self.input_document_path = r"C:\Users\Ivan\OneDrive - Grupo Procaps\Portafolio NTF\26. GESTIÓN ab initio DE LA ESTABILIDAD\Documentos Ejemplos\Vonoprazan\9. DMI VONOPRAZAN.pdf"
        # Initialize state with a realistic apis_text_information and a potential RLD list.
        self.test_state: DrugDevelopmentResearchGraphState = {
            "input_documents": [self.input_document_path],
            "apis_text_information": "Vonoprazan Fumarate in tablet in the oral rout of administration",
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
        This test runs the full drug development graph until the human feedback node
        (FormulatorFeedbackProductResearch) triggers an interrupt. Then it prompts you on the CLI
        for your decision, updates the graph state, and resumes execution.
        """
        thread_info = {"configurable": {"thread_id": "cli_test_thread"}}
        events = []
        interrupt_payload = None

        # Run the graph until the interrupt is reached.
        async for event in self.graph.astream(self.test_state, thread_info, stream_mode="values", subgraphs=True):
            print("\n======================================")
            print(event)
            print("\n======================================")
            events.append(event)
            if "__interrupt__" in event:
                interrupt_payload = event["__interrupt__"]
                print("Interrupt payload received:")
                print(interrupt_payload)
                break

        if not interrupt_payload:
            print("No human interrupt occurred; exiting test.")
            return

        # Simulate CLI input: prompt the user for a decision.
        print("Graph paused at human feedback node. Please provide your decision.")
        feedback_decision = input("Enter feedback decision (retry_api, retry_dosage, enrich): ").strip()
        human_response = {"feedback_decision": feedback_decision}
        if feedback_decision == "retry_dosage":
            new_dosage = input("Enter new dosage form: ").strip()
            human_response["new_dosage_form"] = new_dosage
            apis_retry = input("Enter API names to retry (comma separated): ").strip()
            human_response["APIS_for_retry"] = [api.strip() for api in apis_retry.split(",") if api.strip()]
        elif feedback_decision == "retry_api":
            apis_retry = input("Enter API names to retry (comma separated): ").strip()
            human_response["APIS_for_retry"] = [api.strip() for api in apis_retry.split(",") if api.strip()]
        elif feedback_decision in ["enrich", "go_enrich_accept"]:
            # For testing, we simply select all potential RLDs.
            human_response["selected_RLDs"] = self.test_state["potential_RLDs"]

        print("Simulated human response:", human_response)

        # Update state at the FormulatorFeedback node.
        self.graph.update_state(
            thread_info,
            {
                "feedback_decision": human_response["feedback_decision"],
                "selected_RLDs": human_response.get("selected_RLDs", [])
            },
            as_node="formulator_feedback_product_research"
        )

        # Resume the graph execution using Command(resume=human_response)
        resumed_events = []
        async for event in self.graph.stream(Command(resume=human_response), thread_info, stream_mode="values"):
            resumed_events.append(event)
        print("Resumed events:")
        print(resumed_events)

        final_state = self.graph.get_state(thread_info).values
        print("Final state:")
        print(final_state)

        # Basic assertions for testing purposes.
        self.assertEqual(final_state.get("feedback_decision"), human_response["feedback_decision"])
        if human_response["feedback_decision"] in ["enrich", "go_enrich_accept"]:
            self.assertGreater(len(final_state.get("selected_RLDs", [])), 0)
        self.assertIn(self.input_document_path, final_state.get("input_documents", []))

if __name__ == "__main__":
    unittest.main()
