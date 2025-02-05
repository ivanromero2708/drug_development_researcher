import unittest
from langchain_core.runnables import RunnableConfig
from src.literature_research_agent.nodes.generate_sub_questions import GenerateSubQuestions
from src.literature_research_agent.state import LiteratureResearchGraphState, API, ProductInformation, SearchQuery
from src.configuration import Configuration

class TestGenerateSubQuestions(unittest.TestCase):
    def setUp(self):
        # Create a dummy API instance.
        self.api = API(API_name="Semaglutide")
        
        # Create dummy ProductInformation with the required fields.
        self.product_information = ProductInformation(
            APIs=[self.api],
            product_name="Oral Ozempic",
            product_type="OTC",
            generic_name="Semaglutide",
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
            search_queries=[],
            documents={},
            document_clusters=[],
            chosen_clusters=[],
            context="",
            consolidated_research_report="",
            apis_literature_data=[]
        )
        
        # Create a dummy configuration with 2 queries and a dummy GPT model name.
        self.config = RunnableConfig(configurable=Configuration(number_of_queries=2, gpt4omini="gpt-4o-mini"))
        
        # Instantiate the GenerateSubQuestions node.
        self.node = GenerateSubQuestions()

    def test_generate_sub_questions(self):
        output = self.node.run(self.test_state, self.config)
        self.assertIn("search_queries", output)
        search_queries = output["search_queries"]
        
        # Validate that search_queries is a non-empty list.
        self.assertIsInstance(search_queries, list)
        self.assertGreater(len(search_queries), 0, "The list of search queries should not be empty.")
        
        # Validate each search query.
        for query in search_queries:
            self.assertIsInstance(query, SearchQuery)
            self.assertTrue(query.search_query, "Each search query should have a non-empty 'search_query' string.")
        
        print("\n✅ Generated Search Queries:")
        for query in search_queries:
            print(query.search_query)

if __name__ == "__main__":
    unittest.main()
