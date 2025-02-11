import asyncio
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration
from src.literature_research_agent.state import LiteratureResearchGraphState
from src.state import DocumentClusters
from src.literature_research_agent.prompts import PROMPT_CLUSTER_RELATED_DOCS

# -------------------------------
# Clustering Node


class ClusterRelatedDocs:
    def __init__(self):
        self.configurable = None  # Will be set in cluster()

    async def cluster(
        self, state: LiteratureResearchGraphState, config: RunnableConfig
    ) -> Dict[str, Any]:
        """
        Reviews the retrieved document content in state["documents"] and clusters the documents
        by their relevance to each API property.

        Desired API properties (from APILiteratureData):
            - polymorphs
            - scheme_of_degradation_route
            - stability_indicators
            - impurities
            - biopharmaceutical_classification
            - hygroscopicity
            - chirality_or_specific_optical_rotation
            - glass_transition_temperature
            - degradation_temperature
            - rld_special_characteristics
            - rld_manufacturing_process_info
        """
        # Extract context from state
        API = state["API"]
        product_information = state["product_information_child"]
        product_dosage_form = product_information.product_dosage_form
        route_of_administration = product_information.route_of_administration
        documents = state["documents"]

        # Get configuration and initialize the LLM
        configurable = Configuration.from_runnable_config(config)
        llm = ChatOpenAI(model=configurable.gpt4omini, temperature=0)
        structured_llm = llm.with_structured_output(DocumentClusters)

        # Prepare a list of retrieved documents (limit to 25 to avoid prompt overload)
        doc_list = []
        for url, doc in documents.items():
            content = doc.get("content", "")
            doc_list.append({"url": url, "snippet": content})
        # Uncomment the next line if you wish to limit the number of documents passed to the prompt.
        # doc_list = doc_list[:25]

        human_instructions = PROMPT_CLUSTER_RELATED_DOCS.format(
            API=API,
            product_dosage_form=product_dosage_form,
            route_of_administration=route_of_administration,
            doc_list=doc_list,
        )

        # Create system and human messages for the LLM
        system_msg = SystemMessage(
            content="You are an expert in pharmaceutical literature analysis."
        )
        human_msg = HumanMessage(content=human_instructions)

        # Call the LLM with structured output
        response = await structured_llm.ainvoke([system_msg, human_msg])
        clusters = response.clusters

        return {"document_clusters": clusters}

    async def check_property_clusters(
        self, state: LiteratureResearchGraphState, config: RunnableConfig
    ) -> Dict[str, Any]:
        """Identifies which clusters contain documents for our target properties."""
        clusters = state["document_clusters"]
        target_properties = [
            "polymorphs",
            "scheme_of_degradation_route",
            "stability_indicators",
            "impurities",
            "biopharmaceutical_classification",
            "hygroscopicity",
            "chirality_or_specific_optical_rotation",
            "glass_transition_temperature",
            "degradation_temperature",
            "rld_special_characteristics",
            "rld_manufacturing_process_info",
        ]

        relevant_clusters = []
        for idx, cluster in enumerate(clusters):
            # Check if cluster matches target property AND has documents
            if cluster.property in target_properties and len(cluster.cluster) > 0:
                relevant_clusters.append(idx)

        return {"chosen_clusters": relevant_clusters}

    async def run(
        self, state: LiteratureResearchGraphState, config: RunnableConfig
    ) -> Dict[str, Any]:
        """Updated run method with cluster checking"""
        cluster_result = await self.cluster(state, config)
        state["document_clusters"] = cluster_result["document_clusters"]

        # Add property cluster verification
        verification_result = await self.check_property_clusters(state, config)

        result = {"chosen_clusters": verification_result["chosen_clusters"]}
        result.update(cluster_result)

        return result

