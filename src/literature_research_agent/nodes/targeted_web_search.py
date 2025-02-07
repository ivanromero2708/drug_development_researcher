from ..state import LiteratureResearchGraphState, TavilyQuery
from tavily import AsyncTavilyClient
import asyncio
from typing import List
from datetime import datetime
from langchain_core.runnables import RunnableConfig
from ...configuration import Configuration

class TargetedWebSearch:
    def __init__(self):
        self.tavily_client = AsyncTavilyClient()
    
    async def tavily_search(self, sub_queries: List[TavilyQuery], config: RunnableConfig):
        """Perform searches for each sub-query using the Tavily search tool concurrently."""  
        async def perform_search(itm):
            try:
                configurable = Configuration.from_runnable_config(config)
                max_results_query = configurable.max_results_query
                
                query_with_date = f"{itm.query} {datetime.now().strftime('%m-%Y')}"
                response = await self.tavily_client.search(
                    query=query_with_date,
                    max_results=max_results_query,
                    include_raw_content=True
                )
                return response['results']
            except Exception as e:
                print(f"Error during search '{itm.query}': {str(e)}")
                return []
        
        search_tasks = [perform_search(itm) for itm in sub_queries]
        search_responses = await asyncio.gather(*search_tasks)
        
        search_results = []
        for response in search_responses:
            search_results.extend(response)
        
        return search_results
        
    async def research(self, state: LiteratureResearchGraphState, config: RunnableConfig = None):
        """
        Conducts a Tavily Search and stores documents.
        """
        state['documents'] = {}  # Inicializar documentos

        # Corregido: Usar self y pasar config
        response = await self.tavily_search(state['search_queries'], config)

        for doc in response:
            url = doc.get('url')
            if url and url not in state['documents']:
                state['documents'][url] = doc

        return {"documents": state['documents']}
    
    # Corregido: Añadir parámetro config al método run
    async def run(self, state: LiteratureResearchGraphState, config: RunnableConfig = None):
        return await self.research(state, config)