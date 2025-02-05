import os
import unittest
import asyncio
from datetime import datetime
from langchain_core.runnables import RunnableConfig
from src.literature_research_agent.nodes.targeted_web_search import TargetedWebSearch
from src.literature_research_agent.state import LiteratureResearchGraphState, TavilyQuery
from src.configuration import Configuration

class TestTargetedWebSearch(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """Setup test environment before each test run."""
        # Skip integration test if TAVILY_API_KEY is not set
        if not os.getenv("TAVILY_API_KEY"):
            self.skipTest("TAVILY_API_KEY environment variable not set; skipping integration test.")

        # Create dummy TavilyQuery instances with realistic queries.
        self.search_queries = [
            TavilyQuery(query="What are the reported polymorphic forms and degradation routes of Semaglutide?"),
            TavilyQuery(query="How do stability indicators, impurities, and hygroscopicity affect Semaglutide formulations?")
        ]

        # Create a dummy LiteratureResearchGraphState with all required keys.
        self.test_state = LiteratureResearchGraphState(
            API=None,  # Not used in this node.
            product_information=None,  # Not used in this node.
            search_queries=self.search_queries,  # Directly use the list of queries.
            documents={},
            document_clusters=[],
            chosen_clusters=[],
            context="",
            consolidated_research_report="",
            apis_literature_data=[]
        )

        # Create a dummy configuration instance.
        self.config = RunnableConfig(configurable=Configuration())

        # Instantiate the TargetedWebSearch node.
        self.node = TargetedWebSearch()

    async def test_run_integration(self):
        """Test the integration of TargetedWebSearch node with real Tavily API."""
        # Run the node's research method asynchronously.
        output = await self.node.run(self.test_state)

        # Verify that the output contains the 'documents' key.
        self.assertIn("documents", output)
        documents = output["documents"]
        self.assertIsInstance(documents, dict)

        # Expect at least one document returned from the web search.
        self.assertGreater(len(documents), 0, "Expected at least one document from web search.")

        # Optionally, print out the retrieved documents for inspection.
        print("\n✅ Retrieved Documents:")
        for url, doc in documents.items():
            print("URL:", url)
            print("Document Data:", doc)

if __name__ == "__main__":
    unittest.main()
