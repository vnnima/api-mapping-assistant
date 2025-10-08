import streamlit as st
from api import get_assistants, search_threads


def initialize_session_state(user_id: str):
    """
    Initialize the session state with the user ID and other data we need to manage the chat app.
    """

    if "user_id" not in st.session_state:
        st.session_state.user_id = user_id

    if "assistants" not in st.session_state:
        assistants_list = get_assistants()
        st.session_state.assistants = {
            a["name"]: a["assistant_id"] for a in assistants_list
        }

    if "active_assistant_id" not in st.session_state:
        assistant_ids = list(st.session_state.assistants.values())
        st.session_state.active_assistant_id = assistant_ids[0] if assistant_ids else None

    if "active_assistant" not in st.session_state:
        assistant_names = list(st.session_state.assistants.keys())
        st.session_state.active_assistant = assistant_names[0] if assistant_names else None

    if "threads" not in st.session_state:
        st.session_state.threads = []
        threads = search_threads(st.session_state.user_id)
        st.session_state.threads = threads
        # Keep backward compatibility with thread_ids
        st.session_state.thread_ids = [
            thread["thread_id"] for thread in threads]

    if "selected_thread_id" not in st.session_state:
        if st.session_state.thread_ids:
            st.session_state.selected_thread_id = st.session_state.thread_ids[-1]
        else:
            st.session_state.selected_thread_id = None

    if "thread_state" not in st.session_state:
        st.session_state.thread_state = {}

    if "pending_interrupt" not in st.session_state:
        st.session_state.pending_interrupt = None
    if "pending_payload" not in st.session_state:
        st.session_state.pending_payload = None

    if "is_resuming" not in st.session_state:
        st.session_state.is_resuming = False
    if "resume_payload" not in st.session_state:
        st.session_state.resume_payload = None

    # Generic rerun trigger for callbacks (avoid calling st.rerun() inside them)
    if "trigger_rerun" not in st.session_state:
        st.session_state.trigger_rerun = False
