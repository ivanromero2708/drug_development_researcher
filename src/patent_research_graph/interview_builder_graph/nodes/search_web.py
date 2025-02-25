
from ..prompts import search_instructions
from langchain_community.tools.tavily_search import TavilySearchResults

from tavily import AsyncTavilyClient
from src.patent_research_graph.interview_builder_graph.state import InterviewState, SearchQuery
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration
from langchain_openai import ChatOpenAI

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

class SearchWeb:
    def __init__(self) -> None:
        self.tavily_client = AsyncTavilyClient()
        
    async def search_web(self, state: InterviewState, config: RunnableConfig):
        """ Retrieve docs from web search """
        # Get configuration and initialize the LLM
        configurable = Configuration.from_runnable_config(config)
        max_results_query = configurable.max_results_query
        max_tokens_per_source = configurable.max_tokens_per_source
        llm = ChatOpenAI(model=configurable.gpt4omini, temperature=0)
        
        # Search query
        structured_llm = llm.with_structured_output(SearchQuery)        
        search_query = structured_llm.invoke([search_instructions]+state['messages'])
        
        # Search
        response = await self.tavily_client.search(
            query = search_query.search_query, 
            max_results = max_results_query,
            include_raw_content = True,
            )
        
        # Ensure response contains 'results'
        web_research_results = response.get("results", [])
        
        # Ordenar los resultados por "score" de mayor a menor
        web_research_results = sorted(web_research_results, key=lambda x: x.get("score", 0), reverse=True)
        
        # Deduplicate and store documents in state by URL
        documents = {}
        for doc in web_research_results:
            url = doc.get("url")
            if url and url not in documents:
                documents[url] = doc
        
        # Create the context string using the deduplicated and ordered results
        formatted_search_docs = deduplicate_and_format_sources(
            web_research_results, max_tokens_per_source=max_tokens_per_source, include_raw_content=True
        )
        
        # Write the context to state
        return {"context": [formatted_search_docs]}
    
    async def run(self, state: InterviewState, config: RunnableConfig):
        return await self.search_web(state, config)
