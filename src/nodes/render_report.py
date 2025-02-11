from src.configuration import Configuration
from src.state import DrugDevelopmentResearchGraphState
from langchain_core.runnables import RunnableConfig
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from docx import Document
import json
import os

class RenderReport:
    def __init__(self):
        self.configurable = None
    
    def render_report(self, state: DrugDevelopmentResearchGraphState, config: RunnableConfig):
        
        # Template directory
        template_doc = DocxTemplate("C:/Users/Ivan/OneDrive - Grupo Procaps/Portafolio NTF/16 - I&D 4.0/2. Investigación de Literatura - Degradación de APIs/1.2 MVP/Bibliographic_Revision_Template.docx")
        
        template_doc.render(json.loads(state["context_for_tpl"]))
        
       # Asegurarse de que el directorio "output" exista
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Utilizamos comillas simples dentro del f-string para acceder a la propiedad
        product_name = state["product_information"].product_name
        output_report_filename = os.path.join(output_dir, f"Research report for {product_name}.docx")
        
        template_doc.save(output_report_filename)
        
        return {"report_docx_dir_string": output_report_filename}
    
    def run(self, state: DrugDevelopmentResearchGraphState, config: RunnableConfig):
        return self.render_report(state, config)