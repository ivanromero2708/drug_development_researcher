import streamlit as st
import asyncio, os, json
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig
from src.graph import drug_development_researcher_graph
from src.configuration import Configuration
from src.state import DrugDevelopmentResearchGraphState

# Agregamos algo de CSS para acercarnos al estilo de OpenCanvas
st.markdown("""
<style>
body {
    background-color: #f8f9fa;
    font-family: 'Inter', sans-serif;
}
</style>
""", unsafe_allow_html=True)

# Función auxiliar para inicializar el estado del grafo
def initialize_state(pdf_path: str) -> DrugDevelopmentResearchGraphState:
    state: DrugDevelopmentResearchGraphState = {
        "input_documents": [pdf_path],
        "apis": [],
        "product_information": None,  # Este campo se debe llenar desde el nodo de extracción
        "api_literature_data": [],
        "patent_background_restrictions": "",
        "rld_packaging_descriptions": "",
        "context_for_tpl": {},
        "report_docx_dir_string": ""
    }
    return state

# Función asíncrona que ejecuta el grafo y retorna el estado final,
# siguiendo el patrón de "astream()" y "get_state()"
async def async_run_graph(state: DrugDevelopmentResearchGraphState, config: Configuration):
    thread_info = {"configurable": {"thread_id": "streamlit_thread"}}
    events = []
    async for event in drug_development_researcher_graph.astream(state, thread_info, stream_mode="values"):
        events.append(event)
    final_state = drug_development_researcher_graph.get_state(thread_info).values
    return final_state

def main():
    st.title("Pharma Deep Researcher")
    st.sidebar.header("Options")
    
    option = st.sidebar.radio("Select an action:", 
                              ("Upload Product Info PDF", "Run Research Pipeline", "View Outputs"))
    
    if option == "Upload Product Info PDF":
        st.subheader("Upload a PDF")
        uploaded_pdf = st.file_uploader("Choose a PDF file", type=["pdf"])
        if uploaded_pdf is not None:
            os.makedirs("temp", exist_ok=True)
            file_path = os.path.join("temp", uploaded_pdf.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_pdf.getbuffer())
            st.success(f"Uploaded file: {uploaded_pdf.name}")
            st.session_state["pdf_path"] = file_path

    elif option == "Run Research Pipeline":
        st.subheader("Run Research Pipeline")
        if "pdf_path" not in st.session_state:
            st.error("Please upload a product information PDF first.")
        else:
            pdf_path = st.session_state["pdf_path"]
            st.write("Initializing research state...")
            # Inicializa el estado con el PDF subido
            state = initialize_state(pdf_path)
            # Crea la configuración usando los valores por defecto
            config = Configuration()
            
            st.info("Running research graph... This may take a few moments.")
            # Ejecuta el grafo de forma asíncrona (usamos asyncio.run para llamar a la función async)
            final_state = asyncio.run(async_run_graph(state, config))
            
            st.success("Research pipeline finished!")
            # Guarda la ruta del informe generado en session_state
            report_path = final_state.get("report_docx_dir_string", "")
            st.session_state["report_docx"] = report_path
            # Si se retornó un informe consolidado en texto, lo mostramos en un text_area
            consolidated_report = final_state.get("consolidated_research_report", "")
            if consolidated_report:
                st.text_area("Consolidated Research Report", consolidated_report, height=300)
            else:
                st.info("No consolidated text report was returned.")
            st.markdown("### Estado Final del Grafo")
            st.json(final_state)

    elif option == "View Outputs":
        st.subheader("View and Download Report")
        if "report_docx" not in st.session_state or not st.session_state["report_docx"]:
            st.error("No report available. Please run the research pipeline first.")
        else:
            report_path = st.session_state["report_docx"]
            st.write(f"Final report file: {report_path}")
            if os.path.exists(report_path):
                with open(report_path, "rb") as file:
                    st.download_button("Download Report", file, file_name=os.path.basename(report_path))
            else:
                st.error("Report file not found on disk.")

if __name__ == "__main__":
    main()
