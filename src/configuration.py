import os
from dataclasses import dataclass, field, fields
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
from typing_extensions import Annotated
from dataclasses import dataclass
import os, getpass
from dotenv import load_dotenv

load_dotenv()  # Cargar variables de entorno desde .env

@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the chatbot."""
    gpt4o: str = "gpt-4o"
    gpt4omini: str = "gpt-4o-mini"
    o3mini: str = "o3-mini"
    claude_35_sonnet: str = "claude-3-5-sonnet-latest"
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY")
    number_of_queries: int = 9
    max_results_query: int = 5
    max_tokens_per_source: int = 5000
    language_for_extraction: str = "english"
    language_for_report: str = "english"
    
    @classmethod
    def from_runnable_config(cls, config):
        """Convierte un RunnableConfig en una instancia de Configuration"""
        configurable = config.configurable if hasattr(config, "configurable") else {}
        return cls(**configurable)