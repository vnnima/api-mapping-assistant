import streamlit as st


def render_initial_message(agent_name: str | None, thread_state: dict | None) -> None:
    """
    Render the initial assistant message for new threads.
    This provides a welcoming message to start the conversation.
    The message is always shown (even if there are subsequent messages) to maintain conversation history.
    """
    if not thread_state:
        st.write("Create a new conversation to start chatting...")
        return

    # Get the assistant name from thread metadata if available
    # This ensures we show the correct greeting for the assistant that created this thread
    actual_agent_name = agent_name

    # Check thread-level metadata first
    if "metadata" in thread_state and thread_state["metadata"]:
        metadata = thread_state["metadata"]
        if "assistant_name" in metadata:
            actual_agent_name = metadata["assistant_name"]

    # Also check in values.metadata as fallback
    if "values" in thread_state and isinstance(thread_state["values"], dict):
        metadata = thread_state["values"].get("metadata", {})
        if metadata and "assistant_name" in metadata:
            actual_agent_name = metadata["assistant_name"]

    # Check if there are already messages in the thread
    messages = []
    if "values" in thread_state and isinstance(thread_state["values"], dict):
        messages = thread_state["values"].get("messages", [])
    elif "values" in thread_state and isinstance(thread_state["values"], list):
        for item in thread_state["values"]:
            if isinstance(item, dict) and "messages" in item:
                messages = item["messages"]
                break

    # Only show initial message if thread is empty OR if the first message is from the user
    # (meaning our greeting wasn't saved to the backend)
    should_show_greeting = False
    if not messages:
        # Empty thread - show greeting
        should_show_greeting = True
    elif messages and messages[0].get("type") != "ai":
        # First message is not from AI - show greeting before it
        should_show_greeting = True

    if not should_show_greeting:
        return

    match (actual_agent_name):
        case "API mapping":
            with st.chat_message("assistant"):
                st.markdown("Welcome to the **API Mapping Assistant**. This assistant guides you step by step through all the relevant steps required to technically connect your partner or host system to Compliance Screening via an API.\n\n"
                            "Additionally you can ask me general questions about the integration or the API during each step."
                            )
        # case "API questions and answers":
        #     with st.chat_message("assistant"):
        #         st.markdown("Hello! I am your **AEB API Mapping Assistant**. "
        #                     "You can ask me general questions about the Screening API."
        #                     )
        # case "API error analysis":
        #     with st.chat_message("assistant"):
        #         st.markdown("Hello! I am your **AEB API Mapping Assistant**. "
        #                     "I help you explain errors when using the Screening API."
        #                     )
        case _:
            ...
