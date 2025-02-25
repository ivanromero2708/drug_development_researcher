import os
import json
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from docx import Document
from src.configuration import Configuration
from src.state import DrugDevelopmentResearchGraphState
from langchain_core.runnables import RunnableConfig


class RenderReport:
    def __init__(self):
        self.configurable = None

    def render_report(
        self, state: DrugDevelopmentResearchGraphState, config: RunnableConfig
    ):
        # Get the absolute path to the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the full path to your template
        template_path = os.path.join(
            current_dir,
            "templates",
            "Bibliographic_Revision_Template.docx"
        )

        # Optional check to verify the file actually exists
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found at {template_path}")

        # Load the docx template
        template_doc = DocxTemplate(template_path)

        # Render the template using data from state
        template_doc.render(json.loads(state["context_for_tpl"]))

        # Ensure the 'output' directory exists
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Build the output filename from product name
        product_name = state["product_information"].product_name
        output_report_filename = os.path.join(
            output_dir,
            f"Research report for {product_name}.docx"
        )

        # Save the rendered document
        template_doc.save(output_report_filename)

        return {"report_docx_dir_string": output_report_filename}

    def run(self, state: DrugDevelopmentResearchGraphState, config: RunnableConfig):
        return self.render_report(state, config)
