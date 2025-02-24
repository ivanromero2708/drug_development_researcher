# Filename: app_professional_with_config_reset.py

import streamlit as st
import uuid
import os
import asyncio
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command
from streamlit import components

from src.graph_final import drug_development_researcher_graph
from src.configuration import Configuration
from src.state import DrugDevelopmentResearchGraphState, PotentialRLD, RLD


def reset_app():
    """Clears session state and forcibly reloads the page by injecting a tiny piece of JS."""
    st.session_state.clear()
    components.v1.html("<script>parent.window.location.reload();</script>")
    st.stop()


# ---------------------------------------------
# Streamlit Page Layout and Branding
# ---------------------------------------------
st.set_page_config(page_title="Pharma Deep Researcher w/ Config", layout="wide")

# Try to load your corporate logo
logo_path = "procaps_logo.png"  # adjust as needed
try:
    st.sidebar.image(logo_path, use_container_width=True)
except Exception as e:
    st.sidebar.markdown("**[Procaps S.A. Logo]**")

st.sidebar.title("Pharma Deep Researcher")
st.sidebar.markdown(
    """
    <div style="font-size:0.9em">
    This application runs the entire drug development pipeline, with an **Advanced Configuration** panel for expert users.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------
# Helper: Initialize the Graph State
# ---------------------------------------------
def initialize_graph_state(
    pdf_path: str,
    apis_text_information: str,
    is_rld_combination: str,
    is_supplement: str,
) -> DrugDevelopmentResearchGraphState:
    """
    Create our initial typed state dictionary for the pipeline.
    """
    return {
        "input_documents": [pdf_path],
        "apis_text_information": apis_text_information,
        "is_rld_combination": is_rld_combination,
        "is_supplement": is_supplement,
        # The rest of the pipeline placeholders:
        "apis": [],
        "product_information": None,
        "literature_research_api_data": [],
        "RLDs": [],
        "potential_RLDs": [],
        "selected_RLDs": [],
        "feedback_decision": "",
        "patent_background_restrictions": "",
        "rld_packaging_descriptions": "",
        "context_for_tpl": {},
        "report_docx_dir_string": "",
    }


# ---------------------------------------------
# Helper: Run the Graph until Next Interrupt or End
# ---------------------------------------------
async def run_before_interruption(initial_state, thread_info):
    # Run the graph until an interrupt is reached.
    async for event in drug_development_researcher_graph.astream(
        initial_state, thread_info, stream_mode="updates"
    ):
        pass
    # Extraction Logic after Interruption
    interrupt_payload = event["__interrupt__"]
    potential_RLDs_interrupted_raw = interrupt_payload[0].value["potential_RLDs"]
    potential_RLDs = [
        rld for sublist in potential_RLDs_interrupted_raw for rld in sublist
    ]
    current_RLDs = interrupt_payload[0].value["RLDs"]
    return potential_RLDs, current_RLDs


async def run_after_interruption(human_response, thread_info):
    # Resume the graph with the human response.
    async for event in drug_development_researcher_graph.astream(
        Command(resume=human_response), thread_info, stream_mode="updates"
    ):
        pass
    # Extraction Logic after Interruption
    interrupt_payload = event["__interrupt__"]
    potential_RLDs_interrupted_raw = interrupt_payload[0].value["potential_RLDs"]
    potential_RLDs = [
        rld for sublist in potential_RLDs_interrupted_raw for rld in sublist
    ]
    current_RLDs = interrupt_payload[0].value["RLDs"]
    return potential_RLDs, current_RLDs


# ---------------------------------------------
# MAIN UI
# ---------------------------------------------
async def main():
    st.title("Pharma Deep Researcher — with Advanced Config")
    st.markdown(
        """
        This interface runs the end-to-end drug development pipeline
        and allows you to adjust advanced configuration parameters.
        """
    )

    # Initialize session state variables
    if "thread_id" not in st.session_state:
        st.session_state["thread_id"] = ""
    if "initial_run_done" not in st.session_state:
        st.session_state["initial_run_done"] = False
    if "flat_potential_rlds" not in st.session_state:
        st.session_state["flat_potential_rlds"] = []
    if "current_RLDs" not in st.session_state:
        st.session_state["current_RLDs"] = []
    if "human_response" not in st.session_state:
        st.session_state["human_response"] = None
    if "thread_info" not in st.session_state:
        st.session_state["thread_info"] = {}
    if "loop" not in st.session_state:
        st.session_state["loop"] = asyncio.new_event_loop()

    # 1) File Uploader
    st.subheader("1. Upload Available Product Information")
    uploaded_pdf = st.file_uploader(
        """Upload here a set of input files in several formats (**Microsoft Word**, **PDF**, **Images**).
For example:
1. **SOW** or **DMI** for Product (**Required**).
2. API **DMFs** (**Optional**)
3. **CoA** for APIs (**Optional**)
        """,
        type=["pdf"],
    )
    pdf_path = ""
    if uploaded_pdf is not None:
        os.makedirs("temp_uploads", exist_ok=True)
        pdf_path = os.path.join("temp_uploads", uploaded_pdf.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_pdf.getbuffer())
        st.success(f"Uploaded: {uploaded_pdf.name}")

    # 2) Text Input for APIs Info
    st.subheader(
        "2. Describe APIs complete name, desired dosage form, and route of administration."
    )
    apis_text_information = st.text_area(
        "**Example 1**: '**Dronabinol** in Soft Gelatin Capsules, **Acetazolamide** in Tablets, all oral route \n\n **Example 2**: '**Vonoprazan Fumarate** in tablets, oral route of administration'",
        height=100,
        placeholder="Ingredient complete name (including if it is a base or salt form), dosage form (Per each ingredient), and route of administration (Per each ingredient in the product)",
    )

    # 3) Additional toggles
    st.subheader("3. Additional Configuration")
    colA, colB = st.columns(2)
    with colA:
        is_supplement_sel = st.radio(
            "Is this product a supplement?", ["No", "Yes"], index=0
        )
    with colB:
        is_rld_combination_sel = st.radio(
            "Is the Reference Product a Fixed Dose Combination?", ["No", "Yes"], index=0
        )

    # 4) Advanced Configuration in Sidebar
    st.sidebar.subheader("Advanced Configuration")
    with st.sidebar.expander("Show/Hide Config", expanded=False):
        default_config = Configuration()  # get default values
        n_queries = st.number_input(
            "Number of sub-queries (for property research)",
            min_value=1,
            max_value=20,
            value=default_config.number_of_queries,
            step=1,
        )
        max_results = st.number_input(
            "Max Tavily results per query",
            min_value=1,
            max_value=20,
            value=default_config.max_results_query,
            step=1,
        )
        max_tokens_src = st.number_input(
            "Max tokens per source excerpt",
            min_value=100,
            max_value=2000,
            value=default_config.max_tokens_per_source,
            step=50,
        )
        lang_extraction = st.selectbox(
            "Language for extraction",
            ["english", "spanish", "french", "german"],
            index=0,
        )
        lang_report = st.selectbox(
            "Language for final report",
            ["english", "spanish", "french", "german"],
            index=0,
        )
        local_ob_path = st.text_input(
            "Local Orange Book ZIP path",
            value=default_config.local_orange_book_zip_path,
        )
        new_tavily_key = st.text_input(
            "TAVILY_API_KEY (leave blank to use .env or system default)",
            value="",
            type="password",
        )

    # 5) Run Pipeline (first execution: until the interrupt)
    if st.button("Initialize"):
        if not pdf_path:
            st.warning("Please upload a PDF first!")
            return

        new_thread_id = str(uuid.uuid4())
        st.session_state["thread_id"] = new_thread_id
        st.success(f"New study initiated, Thread ID: {new_thread_id}")

        user_config = Configuration(
            number_of_queries=n_queries,
            max_results_query=max_results,
            max_tokens_per_source=max_tokens_src,
            language_for_extraction=lang_extraction,
            language_for_report=lang_report,
            local_orange_book_zip_path=local_ob_path,
        )
        if new_tavily_key.strip():
            user_config.TAVILY_API_KEY = new_tavily_key.strip()

        initial_state = initialize_graph_state(
            pdf_path=pdf_path,
            apis_text_information=apis_text_information,
            is_rld_combination=is_rld_combination_sel,
            is_supplement=is_supplement_sel,
        )
        st.session_state["report_docx"] = ""
        thread_info = {
            "configurable": {"thread_id": new_thread_id, **user_config.__dict__}
        }
        st.session_state["thread_info"] = thread_info

        loop = st.session_state["loop"]
        flat_rlds, current_RLDs = await run_before_interruption(
            initial_state, thread_info
        )

        st.session_state["flat_potential_rlds"] = flat_rlds
        st.session_state["current_RLDs"] = current_RLDs
        # Set an empty human_response to prompt the user.
        st.session_state["human_response"] = {}
        st.session_state["initial_run_done"] = True

    # ---------------------------------------------
    # Display interruption and collect human feedback
    # ---------------------------------------------
    if st.session_state.get("initial_run_done"):
        st.warning("**Pipeline interrupted** at the Formulator Feedback node!")
        st.subheader("**Formulator Feedback Required**")

        st.write("### Potential Reference Products for DailyMed Research:")
        if st.session_state["flat_potential_rlds"]:
            for i, rld in enumerate(st.session_state["flat_potential_rlds"]):
                st.markdown(
                    f"""
                **[{i}]**  
                - Title: {rld.title}  
                - API: {rld.api_name}  
                - Brand: {rld.brand_name}  
                - Manufacturer: {rld.manufacturer}  
                """
                )
        else:
            st.info("No potential RLDs found.")

        st.write("### **Current RLDs** discovered in the Orange Book Database:")
        for i, rld in enumerate(st.session_state["current_RLDs"]):
            st.markdown(
                f"""
                **RLD {i}**:  
                - API: {rld.api_name}  
                - Brand: {rld.brand_name}  
                - Dosage Form: {rld.rld_dosage_form}  
                - Manufacturer: {rld.manufacturer}
                """
            )

        # Feedback decision select box and extra inputs as needed.
        decision = st.selectbox(
            """### Choose a feedback decision to continue
1. **Retry with API name**
2. **Retry with dosage forms**
3. **Proceed to DailyMed Research AS IS**
4. **Proceed to DailyMed Research with SELECTED APIs**
            """,
            [
                "Retry with API name",
                "Retry with dosage forms",
                "Proceed to DailyMed Research AS IS",
                "Proceed to DailyMed Research with SELECTED APIs",
            ],
            key="main_decision",
        )

        # Depending on the decision, show additional input fields.
        if decision == "Retry with dosage forms":
            st.info("Change dosage forms for certain RLDs by matching their API names.")
            api_list_input = st.text_input(
                "API names to update (comma-separated):", key="api_list_input"
            )
            dosage_list_input = st.text_input(
                "New dosage forms (comma-separated, same length as APIs):",
                key="dosage_list_input",
            )
        if decision == "Retry with API name":
            st.info("Reset brand_name to API name for specified RLDs.")
            retry_api_input = st.text_input(
                "API names to reset brand name (comma-separated):",
                key="retry_api_input",
            )
        if decision == "Proceed to DailyMed Research with SELECTED APIs":
            st.info("Enter indexes of potential RLDs to keep for enrichment.")
            selected_indexes_str = st.text_input(
                "Indexes (e.g., '0,2'):", key="selected_indexes_str"
            )

        if st.button("Resume Pipeline", key="resume_pipeline"):
            human_response = {"feedback_decision": decision}
            if decision == "Retry with API name":
                to_reset = [
                    x.strip()
                    for x in st.session_state.get("retry_api_input", "").split(",")
                    if x.strip()
                ]
                current_RLDs = st.session_state["current_RLDs"]
                for rld_obj in current_RLDs:
                    if rld_obj.api_name in to_reset:
                        rld_obj.brand_name = rld_obj.api_name
                human_response["RLDs"] = current_RLDs

            elif decision == "Retry with dosage forms":
                apis_arr = [
                    x.strip()
                    for x in st.session_state.get("api_list_input", "").split(",")
                    if x.strip()
                ]
                dosage_arr = [
                    x.strip()
                    for x in st.session_state.get("dosage_list_input", "").split(",")
                    if x.strip()
                ]
                mapping = {}
                for i in range(min(len(apis_arr), len(dosage_arr))):
                    mapping[apis_arr[i]] = dosage_arr[i]
                current_RLDs = st.session_state["current_RLDs"]
                for rld_obj in current_RLDs:
                    if rld_obj.api_name in mapping:
                        rld_obj.rld_dosage_form = mapping[rld_obj.api_name]
                human_response["RLDs"] = current_RLDs

            elif decision == "Proceed to DailyMed Research AS IS":
                human_response["selected_RLDs"] = st.session_state[
                    "flat_potential_rlds"
                ]

            elif decision == "Proceed to DailyMed Research with SELECTED APIs":
                selected_indexes = []
                try:
                    selected_indexes = [
                        int(x.strip())
                        for x in st.session_state.get("selected_indexes_str", "").split(
                            ","
                        )
                        if x.strip().isdigit()
                    ]
                except Exception:
                    selected_indexes = []
                chosen_rlds = [
                    st.session_state["flat_potential_rlds"][i]
                    for i in selected_indexes
                    if i < len(st.session_state["flat_potential_rlds"])
                ]
                human_response["selected_RLDs"] = chosen_rlds

            st.session_state["human_response"] = human_response

            # --- Emulate the while loop ---
            # In the CLI test, the while loop continues until the decision is final (i.e. enrich_as_is or enrich_selected)
            final_decisions = [
                "Proceed to DailyMed Research AS IS",
                "Proceed to DailyMed Research with SELECTED APIs",
            ]
            if human_response["feedback_decision"] not in final_decisions:
                # Run the graph again using the human response
                thread_info = st.session_state["thread_info"]
                loop = st.session_state["loop"]
                flat_rlds, current_RLDs = await run_after_interruption(
                    human_response, thread_info
                )

                st.session_state["flat_potential_rlds"] = flat_rlds
                st.session_state["current_RLDs"] = current_RLDs
                # Force a rerun so that the updated RLDs are displayed and the user can choose again.
                st.rerun()
            else:
                # --- Final Resume Execution (third execution) ---
                thread_info = st.session_state["thread_info"]
                resumed_events = []
                async for event in drug_development_researcher_graph.astream(
                    Command(resume=human_response), thread_info, stream_mode="updates"
                ):
                    resumed_events.append(event)
                st.success("Pipeline resumed and finished successfully!")
                final_state = drug_development_researcher_graph.get_state(
                    thread_info
                ).values
                st.session_state["report_docx"] = final_state.get(
                    "report_docx_dir_string", ""
                )
                st.write("**Final Pipeline State**:", final_state)
                # 7) If final report is available, let user download
                if st.session_state.get("report_docx"):
                    doc_path = st.session_state["report_docx"]
                    if os.path.exists(doc_path):
                        with open(doc_path, "rb") as f:
                            st.download_button(
                                "Download .docx",
                                f,
                                file_name=os.path.basename(doc_path),
                            )
                    else:
                        st.error(
                            "Report file not found on disk. Possibly the pipeline didn't generate it."
                        )

    # 8) Add a button to reset the entire app
    st.markdown("---")
    if st.button("Reset App", key="reset_app"):
        reset_app()


if __name__ == "__main__":
    asyncio.run(main())
