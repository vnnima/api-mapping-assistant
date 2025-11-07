import streamlit as st
from api import get_thread_state, create_thread, delete_thread


def render_sidebar():
    assistant_options = []
    for key in sorted(list(st.session_state.assistants.keys())):
        if key == "Request Validation Assistant":
            assistant_options.append(f"{key} - 🛠️ Do not use")
        else:
            assistant_options.append(key)

    assistant = st.selectbox("Select Assistant", assistant_options)

    previous_assistant = st.session_state.get("active_assistant")
    assistant_changed = previous_assistant is not None and previous_assistant != assistant

    st.session_state.active_assistant = assistant

    st.session_state.active_assistant_id = st.session_state.assistants.get(
        assistant)

    if assistant_changed:
        st.session_state.thread_state = {}
        st.session_state.selected_thread_id = None
        # Clear any pending interrupts when switching assistants
        st.session_state.pending_interrupt = None
        st.session_state.pending_payload = None
        st.session_state.is_resuming = False
        st.session_state.resume_payload = None

    st.title("Conversations")
    st.caption("A TCM chatbot to assist with API mapping.")

    if st.button("Create New Conversation"):
        _create_new_thread(user_id=st.session_state.user_id)

    if st.session_state.thread_ids:
        def _on_select_thread():
            st.session_state.thread_state = get_thread_state(
                st.session_state.selected_thread_id)

        # Ensure selected thread exists
        if (
            "selected_thread_id" not in st.session_state
            or st.session_state.selected_thread_id not in st.session_state.thread_ids
        ):
            # Use first thread (oldest) if current selection is invalid
            st.session_state.selected_thread_id = st.session_state.thread_ids[0]

        st.radio(
            "Select Conversation",
            options=st.session_state.thread_ids,
            format_func=format_thread_name,
            key="selected_thread_id",
            on_change=_on_select_thread,
        )

    if st.button("Delete Conversation", type="primary"):
        if st.session_state.selected_thread_id:
            _delete_thread_and_update_state(
                st.session_state.selected_thread_id)


def format_thread_name(thread_id: str) -> str:
    """Format thread name for display in conversation selector."""
    thread = next(
        (t for t in st.session_state.threads if t["thread_id"] == thread_id), None)

    if thread:
        if "created_at" in thread:
            try:
                import datetime
                if isinstance(thread["created_at"], str):
                    dt = datetime.datetime.fromisoformat(
                        thread["created_at"].replace("Z", "+00:00"))
                else:
                    dt = datetime.datetime.fromtimestamp(thread["created_at"])
                date_str = dt.strftime("%Y-%m-%d %H:%M")
                return f"{date_str} ({thread_id[:8]})"
            except (ValueError, TypeError, KeyError):
                pass

        if "metadata" in thread and thread["metadata"]:
            metadata = thread["metadata"]
            if "title" in metadata:
                return f"{metadata['title']} ({thread_id[:8]})"
            if "name" in metadata:
                return f"{metadata['name']} ({thread_id[:8]})"

    return thread_id[:8]


def _create_new_thread(user_id: str):
    # Create thread with the current assistant name stored in metadata
    thread = create_thread(user_id, st.session_state.active_assistant)
    # Insert at the beginning of the list (index 0) instead of appending
    st.session_state.threads.insert(0, thread)
    st.session_state.thread_ids.insert(0, thread["thread_id"])
    st.session_state.selected_thread_id = thread["thread_id"]

    # Clear any pending interrupts when creating new thread
    st.session_state.pending_interrupt = None
    st.session_state.pending_payload = None
    st.session_state.is_resuming = False
    st.session_state.resume_payload = None

    # Get the thread state - for a new thread this will be empty
    st.session_state.thread_state = get_thread_state(thread["thread_id"])

    # Mark that we need to initialize this thread on next interaction
    st.session_state.thread_needs_init = True

    # Don't set trigger_rerun - Streamlit will rerun automatically after button callback


def _delete_thread_and_update_state(thread_id: str):
    delete_thread(thread_id)
    if thread_id in st.session_state.thread_ids:
        st.session_state.thread_ids.remove(thread_id)
    st.session_state.threads = [
        t for t in st.session_state.threads if t["thread_id"] != thread_id]
    st.session_state.thread_state = {}
    # Clear any pending interrupts when deleting thread
    st.session_state.pending_interrupt = None
    st.session_state.pending_payload = None
    st.session_state.is_resuming = False
    st.session_state.resume_payload = None
    # If we deleted the selected thread, pick a new one
    if st.session_state.thread_ids:
        # Select the first remaining thread
        st.session_state.selected_thread_id = st.session_state.thread_ids[0]
    else:
        st.session_state.selected_thread_id = None
    # Don't set trigger_rerun - Streamlit will rerun automatically after button callback
