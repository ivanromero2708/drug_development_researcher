import streamlit as st
import asyncio, os, json, uuid
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command  # Per docs: import Command from langgraph.types
from src.graph_final import drug_development_researcher_graph
from src.configuration import Configuration
from src.state import DrugDevelopmentResearchGraphState

# --- Custom CSS for a beautiful UI ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
body {
    background-color: #eef2f7;
    font-family: 'Inter', sans-serif;
    margin: 0;
    padding: 0;
}
header {
    text-align: center;
    padding: 20px;
    background-color: #4CAF50;
    color: white;
    font-size: 2rem;
}
.sidebar .sidebar-content {
    background-image: linear-gradient(180deg, #8ec5fc, #e0c3fc);
    color: white;
}
.stButton>button {
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 10px 20px;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# --- Helper to initialize graph state (including APIs text info) ---
def initialize_state(pdf_path: str, apis_text: str) -> DrugDevelopmentResearchGraphState:
    state: DrugDevelopmentResearchGraphState = {
        "input_documents": [pdf_path],
        "apis_text_information": apis_text,
        "is_rld_combination": "N",
        "is_supplement": "N",
        "apis": [],
        "api_literature_data": [],
        "patent_background_restrictions": "",
        "rld_packaging_descriptions": "",
        "context_for_tpl": {},
        "report_docx_dir_string": "",
        "feedback_decision": "",
        "potential_RLDs": [],
        "selected_RLDs": []
    }
    return state

# --- Async function to run graph until a human interrupt is encountered ---
async def run_until_interrupt(state: DrugDevelopmentResearchGraphState, config: Configuration, thread_info: dict):
    events = []
    interrupt_payload = None
    async for event in drug_development_researcher_graph.astream(
        state, thread_info, stream_mode="values", subgraphs=True
    ):
        events.append(event)
        # When a node uses interrupt(), it emits an "__interrupt__" key.
        if "__interrupt__" in event:
            interrupt_payload = event["__interrupt__"]
            break
    return events, interrupt_payload

# --- Async function to resume execution using Command ---
async def resume_execution(resume_value, thread_info: dict):
    resumed_events = []
    async for event in drug_development_researcher_graph.astream(
        Command(resume=resume_value), thread_info, stream_mode="values"
    ):
        resumed_events.append(event)
    return resumed_events

def main():
    st.header("Pharma Deep Researcher")
    st.sidebar.title("Settings & Actions")
    
    # Action selection
    action_option = st.sidebar.radio("Select Action:", 
                                     ("Upload PDF", "Run Pipeline", "View Report"))
    
    # Configuration controls: thread ID (generate a new UUID if blank) and APIs text info.
    thread_input = st.sidebar.text_input("Thread ID (leave blank for new)", value="")
    if thread_input.strip() == "":
        generated_thread_id = str(uuid.uuid4())
        st.sidebar.info(f"Generated Thread ID: {generated_thread_id}")
        custom_thread_id = generated_thread_id
    else:
        custom_thread_id = thread_input.strip()
    
    apis_text_input = st.sidebar.text_area(
        "APIs Text Information", 
        value="Vonoprazan Fumarate in tablet in the oral rout of administration",
        height=100
    )
    
    # Upload PDF
    if action_option == "Upload PDF":
        st.subheader("Upload Product Info PDF")
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
        if uploaded_file is not None:
            os.makedirs("temp", exist_ok=True)
            pdf_path = os.path.join("temp", uploaded_file.name)
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Uploaded: {uploaded_file.name}")
            st.session_state["pdf_path"] = pdf_path
    
    # Run Pipeline
    elif action_option == "Run Pipeline":
        st.subheader("Run Research Pipeline")
        if "pdf_path" not in st.session_state:
            st.error("Please upload a PDF first!")
        else:
            pdf_path = st.session_state["pdf_path"]
            st.write("Initializing state...")
            state = initialize_state(pdf_path, apis_text_input)
            config = Configuration()
            thread_info = {"configurable": {"thread_id": custom_thread_id}}
            
            st.info("Running research graph... Please wait.")
            events, interrupt_payload = asyncio.run(run_until_interrupt(state, config, thread_info))
            st.markdown("### Graph Events Until Interrupt")
            st.json(events)
            
            if interrupt_payload:
                st.markdown("## Human Intervention Required")
                st.write("Interrupt Payload:")
                st.json(interrupt_payload)
                
                # Let the user select an action and, if needed, provide additional input.
                chosen_action = st.selectbox("Select Action:", options=["retry_api", "retry_dosage", "enrich"])
                resume_value = None
                if chosen_action == "retry_dosage":
                    new_dosage = st.text_input("Enter new dosage form:")
                    if new_dosage:
                        resume_value = {"option": "retry_dosage", "new_dosage_form": new_dosage}
                    else:
                        st.warning("Please provide a new dosage form to continue with 'retry_dosage'.")
                        return
                else:
                    resume_value = chosen_action  # "retry_api" or "enrich"
                
                if st.button("Resume Graph"):
                    st.info("Updating state and resuming graph execution...")
                    # Update state at the formulator feedback node.
                    drug_development_researcher_graph.update_state(
                        thread_info,
                        {
                            "feedback_decision": "go_enrich_accept" if chosen_action == "enrich" else "retry_daily_med",
                            "selected_RLDs": []  # Replace with UI selections if available.
                        },
                        as_node="formulator_feedback_product_research"
                    )
                    # Resume execution using Command(resume=resume_value)
                    resumed_events = asyncio.run(resume_execution(resume_value, thread_info))
                    st.markdown("### Resumed Graph Events")
                    st.json(resumed_events)
                    
                    final_state = drug_development_researcher_graph.get_state(thread_info).values
                    st.success("Research pipeline finished!")
                    st.markdown("#### Final Graph State")
                    st.json(final_state)
                    st.session_state["report_docx"] = final_state.get("report_docx_dir_string", "")
            else:
                st.info("Graph executed completely without interruption.")
                final_state = drug_development_researcher_graph.get_state(thread_info).values
                st.markdown("#### Final Graph State")
                st.json(final_state)
    
    # View Outputs
    elif action_option == "View Report":
        st.subheader("View and Download Report")
        if "report_docx" not in st.session_state or not st.session_state["report_docx"]:
            st.error("No report available. Run the pipeline first.")
        else:
            report_path = st.session_state["report_docx"]
            st.write(f"Report file: {report_path}")
            if os.path.exists(report_path):
                with open(report_path, "rb") as file:
                    st.download_button("Download Report", file, file_name=os.path.basename(report_path))
            else:
                st.error("Report file not found on disk.")

if __name__ == "__main__":
    main()
