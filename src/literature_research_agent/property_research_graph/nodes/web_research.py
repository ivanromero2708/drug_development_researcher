import asyncio
import logging
from datetime import datetime

from src.literature_research_agent.property_research_graph.state import PropertyResearchGraphState
from tavily import AsyncTavilyClient

from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration

def deduplicate_and_format_sources(results, max_tokens_per_source=300, include_raw_content=True):
    """
    Deduplicates search results by URL and formats them into a readable context string.
    
    Args:
        results (List[dict]): List of search result dictionaries.
        max_tokens_per_source (int): Maximum number of tokens to include from raw_content.
        include_raw_content (bool): Whether to include raw source content.
        
    Returns:
        str: Formatted context string with deduplicated sources.
    """
    # Deduplicate by URL
    unique_sources = {}
    for source in results:
        url = source.get("url")
        if url and url not in unique_sources:
            unique_sources[url] = source

    # Format the results into a context string
    formatted_text = "Sources:\n\n"
    for source in unique_sources.values():
        title = source.get("title", "No Title")
        url = source.get("url", "No URL")
        content = source.get("content", "No Content")
        formatted_text += f"Source {title}:\n===\n"
        formatted_text += f"URL: {url}\n===\n"
        formatted_text += f"Most relevant content from source: {content}\n===\n"
        if include_raw_content:
            char_limit = max_tokens_per_source * 4  # Rough approximation: 4 characters per token
            raw_content = source.get("raw_content") or ""
            if len(raw_content) > char_limit:
                raw_content = raw_content[:char_limit] + "... [truncated]"
            formatted_text += f"Full source content limited to {max_tokens_per_source} tokens: {raw_content}\n\n"
    return formatted_text.strip()

class WebResearch:
    def __init__(self):
        self.tavily_client = AsyncTavilyClient()

    async def web_research(self, state: PropertyResearchGraphState, config: RunnableConfig):
        """
        Conducts a Tavily Search and stores retrieved documents ordered by score.
        """
        # Retrieve search query safely
        query = state.get("query", None)
        if not query:
            logging.error("No search query provided in state.")
            return {"property_research_context": "", "documents": {}}

        # Retrieve configuration values
        configurable = Configuration.from_runnable_config(config)
        max_results_query = configurable.max_results_query
        max_tokens_per_source = configurable.max_tokens_per_source
        
        # Append date to query to ensure recent results
        query_with_date = f"{query} {datetime.now().strftime('%m-%Y')}"

        try:
            # Asynchronous call to Tavily API
            response = await self.tavily_client.search(
                query=query_with_date,
                max_results=max_results_query,
                include_raw_content=True,
                include_domains = ["https://patents.google.com/", "https://ppubs.uspto.gov/pubwebapp/static/pages/ppubsbasic.html", "https://patentscope.wipo.int/search/es/search.jsf", "https://pubmed.ncbi.nlm.nih.gov/", "https://arxiv.org/", "https://core.ac.uk/", "https://www.sciencedirect.com/", "https://www.researchgate.net/", "https://www.semanticscholar.org/", "https://pubchem.ncbi.nlm.nih.gov/"]
            )
            # Ensure response contains 'results'
            web_research_results = response.get("results", [])
            
            # Ordenar los resultados por "score" de mayor a menor
            web_research_results = sorted(web_research_results, key=lambda x: x.get("score", 0), reverse=True)

        except Exception as e:
            logging.error(f"Error during Tavily search: {str(e)}")
            return {"property_research_context": "", "documents": {}}
        
        # Deduplicate and store documents in state by URL
        documents = {}
        for doc in web_research_results:
            url = doc.get("url")
            if url and url not in documents:
                documents[url] = doc
        
        # Create the context string using the deduplicated and ordered results
        context_str = deduplicate_and_format_sources(
            web_research_results, max_tokens_per_source=max_tokens_per_source, include_raw_content=True
        )
        
        return {"property_research_context": context_str, "documents": documents}

    async def run(self, state: PropertyResearchGraphState, config: RunnableConfig):
        return await self.web_research(state, config)
