from ..state import LiteratureResearchGraphState, TavilyQuery
from tavily import AsyncTavilyClient
import asyncio
from typing import List
from datetime import datetime


class TargetedWebSearch:
    def __init__(self):
        self.tavily_client = AsyncTavilyClient()
    
    async def tavily_search(self, sub_queries: List[TavilyQuery]):
        """Perform searches for each sub-query using the Tavily search tool concurrently."""  
        # Define a coroutine function to perform a single search with error handling
        async def perform_search(itm):
            try:
                # Add date to the query as we need the most recent results
                query_with_date = f"{itm.query} {datetime.now().strftime('%m-%Y')}"
                # Attempt to perform the search, hardcoding days to 7 (days will be used only when topic is news)
                response = await self.tavily_client.search(query=query_with_date, max_results=10)
                return response['results']
            except Exception as e:
                # Handle any exceptions, log them, and return an empty list
                print(f"Error occurred during search for query '{itm.query}': {str(e)}")
                return []
        
        # Run all the search tasks in parallel
        search_tasks = [perform_search(itm) for itm in sub_queries]
        search_responses = await asyncio.gather(*search_tasks)
        
        # Combine the results from all the responses
        search_results = []
        for response in search_responses:
            search_results.extend(response)
        
        return search_results
        
    async def research(self, state: LiteratureResearchGraphState):
        """
        Conducts a Tavily Search and stores all documents in a unified 'documents' attribute.
        """
        state['documents'] = {}  # Initialize documents if not already present

        research_node = TargetedWebSearch()
        # Perform the search and gather results
        response = await research_node.tavily_search(state['search_queries'])

        # Process each set of search results and add to documents
        for doc in response:
            url = doc.get('url')
            if url and url not in state['documents']:  # Avoid duplicates
                state['documents'][url] = doc

        return {"documents": state['documents']}
    
    async def run(self, state: LiteratureResearchGraphState):
        return await self.research(state)
