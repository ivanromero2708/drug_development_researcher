from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig

from src.product_research_graph.product_enrichment_graph.state import (
    ProductReportSection,
    GenerateProductContentGraphState,
)

from src.configuration import Configuration

from src.product_research_graph.product_enrichment_graph.prompts import (
    SYSTEM_PROMPT_GENERATE_RLD_CONTENT,
    HUMAN_PROMPT_GENERATE_RLD_CONTENT,
)


from src.product_research_graph.state import (
    DrugLabelDoc,
)

class GenerateRLDContent:
    def __init__(self):
        self.configurable = None
    
    def extract_rld_report_section(self, drug_label_doc: DrugLabelDoc, doc_field: str) -> str:
        """
        Retrieve the requested doc_field from the drug_label_doc.
        If the field doesn't exist, return an empty string.
        """
        return getattr(drug_label_doc, doc_field, "")  # <-- changed logic
    
    def generate_rld_content(self, state: GenerateProductContentGraphState, config: RunnableConfig):
        
        # 1) Extract main data from state
        API_name = state["selected_RLD"].api_name
        drug_label_doc = state["drug_label_doc"]
        product_report_section = state["product_report_section"]

        # 2) Get configuration + LLM
        configurable = Configuration.from_runnable_config(config)
        llm = ChatOpenAI(model=configurable.gpt4omini, temperature=0)
        
        # 3) Retrieve examples + mapping
        HUMAN_MESSAGE_EXAMPLE1_RLD = configurable.HUMAN_MESSAGE_EXAMPLE1_RLD
        AI_MESSAGE_EXAMPLE1_RLD = configurable.AI_MESSAGE_EXAMPLE1_RLD
        HUMAN_MESSAGE_EXAMPLE2_RLD = configurable.HUMAN_MESSAGE_EXAMPLE2_RLD
        AI_MESSAGE_EXAMPLE2_RLD = configurable.AI_MESSAGE_EXAMPLE2_RLD
        MAPPING_DRUG_LABEL_SECTION = configurable.MAPPING_DRUG_LABEL_SECTION
        
        # 4) Set up structured output
        structured_llm = llm.with_structured_output(ProductReportSection)
        
        system_msg = SystemMessage(
            content=SYSTEM_PROMPT_GENERATE_RLD_CONTENT.format(
                product_report_section = product_report_section,
            )
        )
        
        # 5) Prepare examples for the chosen rld_report_section
        #    e.g. "API_name_with_UNII", "inactive_ingredients_with_UNII_str", etc.
        example_human_msg_1 = HUMAN_MESSAGE_EXAMPLE1_RLD.get(product_report_section, "")
        example_ai_msg_1 = AI_MESSAGE_EXAMPLE1_RLD.get(product_report_section, "")
        example_human_msg_2 = HUMAN_MESSAGE_EXAMPLE2_RLD.get(product_report_section, "")
        example_ai_msg_2 = AI_MESSAGE_EXAMPLE2_RLD.get(product_report_section, "")
        
        human_msg_example1 = HumanMessage(content=example_human_msg_1)
        ai_msg_example1 = AIMessage(content=example_ai_msg_1)
        human_msg_example2 = HumanMessage(content=example_human_msg_2)
        ai_msg_example2 = AIMessage(content=example_ai_msg_2)
        
        # 6) Determine which field in drug_label_doc to use
        #    e.g. "how_supplied_storage_handling" for "rld_how_supplied"
        doc_field = MAPPING_DRUG_LABEL_SECTION.get(product_report_section, "product_info_str")
        
        # 7) Extract that field from the doc
        doc_content = self.extract_rld_report_section(drug_label_doc, doc_field)
        
        # 8) Build the final human message with the relevant doc content
        human_msg = HumanMessage(
            content=HUMAN_PROMPT_GENERATE_RLD_CONTENT.format(
                API_name=API_name,
                drug_label_doc_info=doc_content,  # <-- now uses the actual doc content
            )
        )
        
        # 9) Invoke the LLM with examples + final user message
        response = structured_llm.invoke([
            system_msg,
            human_msg_example1,
            ai_msg_example1,
            human_msg_example2,
            ai_msg_example2,
            human_msg
        ])
        
        structured_response = ProductReportSection(
            product_report_section=product_report_section,            
            research_report=response.research_report,
        )
        
        # 10) Return the structured output as a pydantic model
        return {"product_research_data": [structured_response]}  # <-- changed
    
    def run(self, state: GenerateProductContentGraphState, config: RunnableConfig):
        return self.generate_rld_content(state, config)
