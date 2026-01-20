"""
Chat App for Langgraph Agents using Streamlit.

This is a basic chat app/UI for interacting with Langgraph Agents via the Langgraph Server API. The app allows you to connect any Langgraph agents to a web UI, manage conversations, stream responses, and more.

This is a great starting point for learning how to build a full-stack AI application.
"""
import json
import streamlit as st
from pathlib import Path
from api import (
    get_thread_state,
    run_thread_events,
)
from utils import render_initial_message
from sidebar import render_sidebar
from state import initialize_session_state


initialize_session_state(user_id="valdrin")

# Perform deferred rerun if requested by interrupt/resume callbacks
if st.session_state.get("trigger_rerun", False):
    st.session_state.trigger_rerun = False
    st.rerun()


def handle_resume_if_needed():
    """
    If a resume is in progress, perform it (using Command(resume=...)),
    and then rerun to refresh the thread state and UI.
    """
    if not st.session_state.is_resuming:
        return

    resume_payload = st.session_state.resume_payload or {}

    # Clear interrupt BEFORE resuming so we don't gate the UI during the streaming pass
    st.session_state.pending_interrupt = None
    st.session_state.pending_payload = None
    st.session_state.is_resuming = False
    st.session_state.resume_payload = None

    with st.chat_message("assistant"):
        buffer = ""
        placeholder = st.empty()
        for kind, data in run_thread_events(
            st.session_state.active_assistant_id,
            st.session_state.selected_thread_id,
            initial_input=None,
            resume_payload=resume_payload,
        ):
            if kind == "ai_chunk":
                buffer += data or ""
                placeholder.markdown(buffer)
            elif kind == "interrupt":
                # New interrupt: stash & rerun so the controls show next run
                val = (data or {}).get(
                    "value", {}) if isinstance(data, dict) else {}
                st.session_state.pending_interrupt = data
                st.session_state.pending_payload = val
                st.rerun()
            elif kind == "done":
                break
            else:
                pass

    # After finishing resume streaming, rerun to refresh thread state & normal UI
    st.rerun()


def render_interrupt_controls_if_pending() -> bool:
    """
    Render interrupt controls (Continue + Ask) if an interrupt is pending.
    Returns True if controls were rendered (i.e., an interrupt is active).
    """
    if st.session_state.pending_interrupt is None:
        return False

    if not st.session_state.pending_payload:
        st.error("Interrupt payload is missing or invalid.")
        return False

    if st.session_state.pending_payload['type'] == "start_or_question":
        # Initial interrupt - offer to start the flow. Questions are disabled
        # here: user must press Start to proceed.
        prompt_text = st.session_state.pending_payload.get(
            'prompt', "Welcome! Click 'Start' to begin the guided API mapping process.")
        st.info(f"**Welcome**\n\n{prompt_text}")

        def _resume_start():
            st.session_state.resume_payload = {"decision": "start"}
            st.session_state.is_resuming = True
            st.session_state.trigger_rerun = True

        st.button("🚀 Start", type="primary", key="interrupt_start",
                  on_click=_resume_start)

        # Return True to indicate the interrupt is active and block chat input
        return True

    elif st.session_state.pending_payload['type'] == "ask_endpoints":
        # Handle endpoint asking with input fields for test and prod URLs
        prompt_text = st.session_state.pending_payload.get(
            'prompt', "Please provide the AEB RZ Endpoints.")
        title = st.session_state.pending_payload.get(
            'title', "Step 1: AEB RZ Endpoints")
        st.info(f"**{title}**\n\n{prompt_text}")

        # Use session state to surface endpoint submit errors inline (near the inputs)
        if "endpoint_submit_error" not in st.session_state:
            st.session_state["endpoint_submit_error"] = None

        def _resume_with_endpoints():
            test_url = st.session_state.get("test_url_input", "").strip()
            prod_url = st.session_state.get("prod_url_input", "").strip()

            # Validate locally and store error in session state so it renders inline
            if not test_url and not prod_url:
                st.session_state["endpoint_submit_error"] = "Please provide at least one endpoint URL."
                return

            # Clear any previous error and resume
            st.session_state["endpoint_submit_error"] = None
            st.session_state.resume_payload = {
                "test_url": test_url,
                "prod_url": prod_url
            }
            st.session_state.is_resuming = True
            st.session_state.trigger_rerun = True

        def _resume_skip_endpoints():
            st.session_state.resume_payload = {"response": "skip"}
            st.session_state.is_resuming = True
            st.session_state.trigger_rerun = True

        st.text_input("Test Endpoint URL:", key="test_url_input",
                      placeholder="https://test.aeb.com/...")
        st.text_input("Production Endpoint URL:", key="prod_url_input",
                      placeholder="https://prod.aeb.com/...")

        col1, col2 = st.columns(2)
        with col1:
            st.button("✅ Submit Endpoints", type="primary", key="interrupt_submit_endpoints",
                      on_click=_resume_with_endpoints)
        with col2:
            st.button("⏭️ Skip (use default endpoints)", key="interrupt_skip_endpoints",
                      on_click=_resume_skip_endpoints)

        # If there's a validation error from submit, show it inline below the controls
        if st.session_state.get("endpoint_submit_error"):
            st.error(st.session_state.get("endpoint_submit_error"))

        st.write("")
        st.write("Or ask a question below ⬇️")

        # Return False to allow chat input
        return False

    elif st.session_state.pending_payload['type'] == "ask_client":
        # Handle client code asking with input field, skip, and question options
        prompt_text = st.session_state.pending_payload.get(
            'prompt', "Please provide your clientIdentCode or skip to use default.")
        title = st.session_state.pending_payload.get(
            'title', "Step 2: Client Name")
        st.info(f"**{title}**\n\n{prompt_text}")

        if "client_ident_code_error" not in st.session_state:
            st.session_state["client_ident_code_error"] = None

        def _resume_with_client_code():
            client_code = st.session_state.get("client_code_input", "").strip()

            if not client_code:
                st.session_state["client_ident_code_error"] = "Please provide a client code or use the skip button."
                return

            st.session_state.resume_payload = {"client_code": client_code}
            st.session_state.is_resuming = True
            st.session_state.trigger_rerun = True

        def _resume_skip_client():
            st.session_state.resume_payload = {"response": "skip"}
            st.session_state.is_resuming = True
            st.session_state.trigger_rerun = True

        st.text_input("Client Code (clientIdentCode):",
                      key="client_code_input", placeholder="e.g., APITEST")

        col1, col2 = st.columns(2)
        with col1:
            st.button("✅ Submit Client Code", type="primary", key="interrupt_submit_client",
                      on_click=_resume_with_client_code)
        with col2:
            st.button("⏭️ Skip (use APITEST)", key="interrupt_skip_client",
                      on_click=_resume_skip_client)

        if st.session_state.get("client_ident_code_error"):
            st.error(st.session_state.get("client_ident_code_error"))

        st.write("")
        st.write("Or ask a question below ⬇️")

        # Return False to allow chat input
        return False

    elif st.session_state.pending_payload['type'] == "ask_wsm":
        # Handle WSM asking with skip/question options
        prompt_text = st.session_state.pending_payload.get(
            'prompt', "Is the WSM user already set up?")
        title = st.session_state.pending_payload.get(
            'title', "Step 3: WSM User")
        st.info(f"**{title}**\n\n{prompt_text}")

        col1, col2, col3 = st.columns(3)

        def _resume_yes_wsm():
            st.session_state.resume_payload = {"response": "yes"}
            st.session_state.is_resuming = True
            st.session_state.trigger_rerun = True

        def _resume_no_wsm():
            st.session_state.resume_payload = {"response": "no"}
            st.session_state.is_resuming = True
            st.session_state.trigger_rerun = True

        with col1:
            st.button("✅ Yes", key="interrupt_yes_wsm",
                      on_click=_resume_yes_wsm)

        with col2:
            st.button("❌ No/Skip", key="interrupt_no_wsm",
                      on_click=_resume_no_wsm)

        with col3:
            st.write("Or ask a question below ⬇️")

        # Return False to allow chat input
        return False

    elif st.session_state.pending_payload['type'] == "get_api_data":
        prompt_text = st.session_state.pending_payload[
            'prompt'] or "Please provide your system name, process, and existing API metadata (e.g., JSON schema, XML example, CSV structure, OpenAPI/Swagger definition)."
        st.info(f"**System info:**\n\n{prompt_text}")

        col = st.container()

        def _resume_with_api_data():
            system_name = st.session_state.get("system_name", "").strip()
            process = st.session_state.get("process", "").strip()
            api_metadata_file = st.session_state.get("api_metadata_file")

            if not system_name or not process or not api_metadata_file:
                st.error(
                    "Please fill in all fields and upload a file.")
                return

            file_content = api_metadata_file.getvalue()
            if isinstance(file_content, bytes):
                try:
                    file_content = file_content.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        file_content = file_content.decode('latin-1')
                    except UnicodeDecodeError:
                        st.error(
                            "Could not decode file. Please ensure it's a text file with UTF-8 or Latin-1 encoding.")
                        return

            payload = {
                "system_name": system_name,
                "process": process,
                "api_metadata_filename": api_metadata_file.name,
                "api_metadata_content": file_content,
            }
            st.session_state.resume_payload = payload
            st.session_state.is_resuming = True
            st.session_state.trigger_rerun = True

        with col:
            st.text_input("System name:", key="system_name")
            st.text_input("Process:", key="process")
            st.file_uploader("Upload existing API metadata:",
                             type=["json", "xml", "csv", "yaml", "txt"], key="api_metadata_file")
            st.button("Send data", type="primary",
                      on_click=_resume_with_api_data)

        return True
    elif st.session_state.pending_payload['type'] in ["show_general_info", "show_screening_variants", "show_responses"]:
        # Handle yes/no/skip interrupts for information display
        prompt_text = st.session_state.pending_payload.get(
            'prompt', "Would you like to see this information?")
        title = st.session_state.pending_payload.get(
            'title', "Information Option")
        st.info(f"**{title}**\n\n{prompt_text}")

        col1, col2, col3 = st.columns(3)

        def _resume_yes():
            st.session_state.resume_payload = {"response": "yes"}
            st.session_state.is_resuming = True
            st.session_state.trigger_rerun = True

        def _resume_skip():
            st.session_state.resume_payload = {"response": "skip"}
            st.session_state.is_resuming = True
            st.session_state.trigger_rerun = True

        with col1:
            st.button("✅ Yes, show", key="interrupt_yes",
                      on_click=_resume_yes)

        with col2:
            st.button("⏭️ Skip", key="interrupt_skip",
                      on_click=_resume_skip)

        with col3:
            st.write("Or type a question below ⬇️")

        # Return False to allow chat input
        return False

    else:
        prompt_text = st.session_state.pending_payload[
            'prompt'] or "Input required: Press `continue` or ask a question."
        st.info(f"**Interrupt**\n\n{prompt_text}")

        col1, col2 = st.columns([1, 2])

        def _resume_continue():
            st.session_state.resume_payload = {"continue": True}
            st.session_state.is_resuming = True
            st.session_state.trigger_rerun = True

        with col1:
            st.button("▶️ Continue", type="primary", key="interrupt_continue",
                      on_click=_resume_continue)

        with col2:
            st.write("Or type a question below ⬇️")

        # Return False to allow chat input for questions
        return False


with st.sidebar:
    render_sidebar()


# Determine which assistant to display in the title
# Use the assistant from the thread metadata if available, otherwise use the active assistant
display_assistant = st.session_state.active_assistant

# Load latest thread state FIRST before rendering anything
if (st.session_state.selected_thread_id and
        st.session_state.selected_thread_id in st.session_state.thread_ids):
    st.session_state.thread_state = get_thread_state(
        st.session_state.selected_thread_id)
else:
    # Clear thread state if no valid thread is selected
    st.session_state.thread_state = {}

# Get the assistant name from thread metadata if available
if st.session_state.thread_state:
    # Check thread-level metadata first
    if "metadata" in st.session_state.thread_state and st.session_state.thread_state["metadata"]:
        metadata = st.session_state.thread_state["metadata"]
        if "assistant_name" in metadata:
            display_assistant = metadata["assistant_name"]

    # Also check in values.metadata as fallback
    if "values" in st.session_state.thread_state and isinstance(st.session_state.thread_state["values"], dict):
        metadata = st.session_state.thread_state["values"].get("metadata", {})
        if metadata and "assistant_name" in metadata:
            display_assistant = metadata["assistant_name"]

st.title(display_assistant)

handle_resume_if_needed()
render_initial_message(
    display_assistant,
    st.session_state.selected_thread_id,
)

# For new threads with no messages and no pending interrupt, trigger the initial run
if (st.session_state.selected_thread_id and
    not st.session_state.pending_interrupt and
        not st.session_state.get("initial_run_triggered", False)):

    messages = []
    if st.session_state.thread_state and "values" in st.session_state.thread_state and isinstance(st.session_state.thread_state["values"], dict):
        messages = st.session_state.thread_state["values"].get("messages", [])

    # If no messages yet, trigger initial run to get the welcome interrupt
    if not messages:
        st.session_state.initial_run_triggered = True
        with st.spinner("Initializing..."):
            for kind, data in run_thread_events(
                st.session_state.active_assistant_id,
                st.session_state.selected_thread_id,
                initial_input={},
                resume_payload=None,
            ):
                if kind == "interrupt":
                    val = (data or {}).get(
                        "value", {}) if isinstance(data, dict) else {}
                    st.session_state.pending_interrupt = data
                    st.session_state.pending_payload = val
                    break
        st.rerun()

if ts := st.session_state.thread_state:
    messages = []
    if "values" in ts and isinstance(ts["values"], dict):
        messages = ts["values"].get("messages", [])
    elif "values" in ts and isinstance(ts["values"], list):
        for item in ts["values"]:
            if isinstance(item, dict) and "messages" in item:
                messages = item["messages"]
                break

    for message in messages:
        if message.get("type") == "tool":
            with st.expander(f"🛠️ {message.get('name', 'tool')} < RESULTS > "):
                try:
                    json_message = json.loads(message.get("content") or "{}")
                    st.json(json_message)
                except Exception:
                    st.write(message.get("content") or "")
        elif message.get("type") == "ai" and message.get("tool_calls"):
            with st.chat_message("ai"):
                first_call = message["tool_calls"][0]
                st.markdown(f"🛠️ {first_call.get('name', 'tool')} < CALL >")
                st.json(first_call.get("args", {}))
        else:
            with st.chat_message(message.get("type", "ai")):
                st.markdown(message.get("content") or "")

interrupt_active = render_interrupt_controls_if_pending()

# Check if we have a special interrupt that allows chat input (for questions)
has_question_enabled_interrupt = (st.session_state.pending_interrupt is not None and
                                  st.session_state.pending_payload and
                                  st.session_state.pending_payload.get('type') in ["ask_endpoints", "ask_client", "ask_wsm", "show_general_info", "show_screening_variants", "show_responses", "question_or_continue"])

# User should not input text in chat when there is a blocking interrupt or when no thread is selected
# Note: thread_state can be an empty dict {} for new threads, which is still valid
chat_disabled = interrupt_active or st.session_state.selected_thread_id is None
prompt = st.chat_input("Send a message...", disabled=chat_disabled)

if prompt and not interrupt_active:
    # If there's an interrupt that allows questions, treat the message as a question
    if has_question_enabled_interrupt:
        interrupt_type = st.session_state.pending_payload.get('type')

        # For start_or_question, send decision="qa" to enter Q&A mode
        if interrupt_type == "start_or_question":
            st.session_state.resume_payload = {
                "decision": "qa", "question": prompt}
        # For ask_endpoints, treat input as a question
        elif interrupt_type == "ask_endpoints":
            st.session_state.resume_payload = {"question": prompt}
        # For ask_client, treat input as a question
        elif interrupt_type == "ask_client":
            st.session_state.resume_payload = {"question": prompt}
        # For ask_wsm, check if it's a simple yes/no or a question
        elif interrupt_type == "ask_wsm":
            prompt_lower = prompt.lower().strip()
            # If it's a simple yes/no answer, send as response
            if prompt_lower in {"yes", "no", "skip", "y", "n"}:
                st.session_state.resume_payload = {"response": prompt_lower}
            else:
                # Otherwise treat it as a question
                st.session_state.resume_payload = {"question": prompt}
        else:
            # For info interrupts, just send the question
            st.session_state.resume_payload = {"question": prompt}

        st.session_state.is_resuming = True
        st.session_state.pending_interrupt = None
        st.session_state.pending_payload = None
        st.rerun()

if prompt and not interrupt_active and not has_question_enabled_interrupt:
    with st.chat_message("user"):
        st.markdown(prompt)

    messages_to_send = [prompt]

    # Clear the init flag since we're now handling the first message
    if st.session_state.get("thread_needs_init", False):
        st.session_state.thread_needs_init = False

    # Stream assistant response and capture interrupts
    with st.chat_message("assistant"):
        buffer = ""
        placeholder = st.empty()
        received_content = False

        for kind, data in run_thread_events(
            st.session_state.active_assistant_id,
            st.session_state.selected_thread_id,
            initial_input={"messages": messages_to_send},
            resume_payload=None,
        ):
            if kind == "ai_chunk":
                buffer += data or ""
                placeholder.markdown(buffer)
                received_content = True
            elif kind == "interrupt":
                # Persist interrupt and rerun so the gate shows controls next run
                val = (data or {}).get(
                    "value", {}) if isinstance(data, dict) else {}
                st.session_state.pending_interrupt = data
                st.session_state.pending_payload = val
                st.rerun()
            elif kind == "done":
                break
            else:
                pass

        # If no content was received, show a placeholder
        if not received_content and not buffer:
            placeholder.markdown("_Thinking..._")

    st.rerun()
