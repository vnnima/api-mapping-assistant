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

    if st.session_state.pending_payload['type'] == "get_api_data":
        prompt_text = st.session_state.pending_payload[
            'prompt'] or "Bitte geben Sie Ihren Systemnamen, Prozess und bestehenden API-Metadaten an (z.B. JSON-Schema, XML-Beispiel, CSV-Struktur, OpenAPI/Swagger Definition)."
        st.info(f"**Interrupt**\n\n{prompt_text}")

        col = st.container()

        def _resume_with_api_data():
            system_name = st.session_state.get("system_name", "").strip()
            process = st.session_state.get("process", "").strip()
            api_metadata_file = st.session_state.get("api_metadata_file")

            if not system_name or not process or not api_metadata_file:
                st.error(
                    "Bitte füllen Sie alle Felder aus und laden Sie eine Datei hoch.")
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
            st.text_input("Systemname:", key="system_name")
            st.text_input("Prozess:", key="process")
            st.file_uploader("Bestehende API-Metadaten hochladen:",
                             type=["json", "xml", "csv", "yaml", "txt"], key="api_metadata_file")
            st.button("Daten senden 💬", on_click=_resume_with_api_data)

        return True
    elif st.session_state.pending_payload['type'] in ["show_general_info", "show_screening_variants", "show_responses"]:
        # Handle yes/no/skip interrupts for information display
        prompt_text = st.session_state.pending_payload.get(
            'prompt', "Möchten Sie diese Information sehen?")
        st.info(f"**Information Option**\n\n{prompt_text}")

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
            st.button("✅ Ja, zeigen", key="interrupt_yes",
                      on_click=_resume_yes)

        with col2:
            st.button("⏭️ Überspringen", key="interrupt_skip",
                      on_click=_resume_skip)

        return True

    else:
        prompt_text = st.session_state.pending_payload[
            'prompt'] or "Eingabe benötigt: Drücken sie `weiter` oder stellen sie eine Frage."
        st.info(f"**Interrupt**\n\n{prompt_text}")

        col1, col2 = st.columns([1, 3])

        def _resume_continue():
            st.session_state.resume_payload = {"continue": True}
            st.session_state.is_resuming = True
            st.session_state.trigger_rerun = True

        with col1:
            st.button("Weiter ▶️", key="interrupt_continue",
                      on_click=_resume_continue)

        def _resume_question():
            q = st.session_state.get("interrupt_question_text", "")
            if q.strip():
                st.session_state.resume_payload = {"question": q.strip()}
                st.session_state.is_resuming = True
                st.session_state.trigger_rerun = True

        with col2:
            st.text_input("Frage stellen:", key="interrupt_question_text")
            st.button("Frage senden 💬", on_click=_resume_question)

        return True


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

render_initial_message(st.session_state.active_assistant,
                       st.session_state.thread_state)

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

# User should not input text in chat when there is an interrupt or when no thread is selected
# Note: thread_state can be an empty dict {} for new threads, which is still valid
chat_disabled = interrupt_active or st.session_state.selected_thread_id is None
prompt = st.chat_input("Send a message...", disabled=chat_disabled)

if prompt and not interrupt_active:
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
