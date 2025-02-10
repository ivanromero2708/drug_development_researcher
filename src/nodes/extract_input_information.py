import asyncio
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_community.document_loaders import PyPDFLoader

from ..configuration import Configuration
from ..state import ProductInformation, DrugDevelopmentResearchGraphState
from ..prompts import PROMPT_EXTRACT_INPUT_INFORMATION

class ExtractInputInformation:
    """
    This node extracts product information from a PDF file.
    It expects the state to include an "input_documents" key whose value is a string (or a list of strings)
    representing the file path(s) to the PDF(s) containing product information.
    
    The node uses PyPDFLoader in "single" mode (with a custom pages delimiter) to read the entire PDF as one document,
    concatenates the content into a single string, and then uses a language model with structured output to extract
    the following fields into a ProductInformation model:
    
      - APIs
      - product_name
      - product_type
      - generic_name
      - product_strength
      - product_dosage_form
      - route_of_administration
      - product_dose
      - physical_characteristics
      - packaging_type
      - commercial_presentations
      - required_expiration_time
      - observations
      
    Any field not found should be returned as an empty string.
    """
    def __init__(self):
        pass

    def extract_input_information(self, state: DrugDevelopmentResearchGraphState, config: RunnableConfig) -> Dict[str, Any]:
        # Retrieve the PDF file path from the state.
        input_docs = state.get("input_documents")
        if not input_docs:
            raise ValueError("State must include an 'input_documents' key with a valid PDF file path.")
        if isinstance(input_docs, list):
            pdf_path = input_docs[0]
        else:
            pdf_path = input_docs

        # Use PyPDFLoader to load the PDF in "single" mode so that all pages are joined.
        loader = PyPDFLoader(
            file_path=pdf_path,
            mode="single",  # Do not split paragraphs across pages.
            pages_delimiter="\n-----PAGE BREAK-----\n"  # Custom page delimiter.
        )
        docs = loader.load()
        if not docs:
            raise ValueError("No content could be extracted from the PDF.")
        # In 'single' mode, docs should contain one document with all pages concatenated.
        product_input_information = docs[0].page_content

        # Initialize the language model using the configuration.
        conf = Configuration.from_runnable_config(config)
        llm = ChatOpenAI(model=conf.gpt4o, temperature=0)
        # Configure structured output for the ProductInformation model.
        structured_llm = llm.with_structured_output(ProductInformation)

        # Build the prompt.
        # PROMPT_EXTRACT_INPUT_INFORMATION is assumed to be a string with a placeholder {product_input_information}.
        human_instructions = PROMPT_EXTRACT_INPUT_INFORMATION.format(
            product_input_information=product_input_information
        )

        messages = [
            SystemMessage(content="Extract the product information as structured JSON following the provided keys."),
            HumanMessage(content=human_instructions)
        ]

        # Invoke the language model to extract the structured product information.
        product_info = structured_llm.invoke(messages)
        return {"product_information": product_info, "apis": product_info.APIs}

    def run(self, state: DrugDevelopmentResearchGraphState, config: RunnableConfig) -> Dict[str, Any]:
        return self.extract_input_information(state, config)
