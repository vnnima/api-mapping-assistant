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

    match (agent_name):
        case "API Mapping Assistant":
            with st.chat_message("assistant"):
                st.markdown("Hello! I am your **AEB API Mapping Assistant**. "
                            "I help you cleanly integrate the **TCM Screening API** into your system.\n\n"
                            "Would you like to start with the integration? (Yes/No)")
        case "Request Validation Assistant":
            with st.chat_message("assistant"):
                st.markdown("Hello! I am your **AEB API Mapping Assistant**. "
                            "I help you check if your call to the Screening API is correct.")
        case "QnA Assistant":
            with st.chat_message("assistant"):
                st.markdown("Hello! I am your **AEB API Mapping Assistant**. "
                            "You can ask me general questions about the Screening API."
                            )
        case "Error Detection Assistant":
            with st.chat_message("assistant"):
                st.markdown("Hello! I am your **AEB API Mapping Assistant**. "
                            "I help you explain errors when using the Screening API."
                            "Would you like to start with the integration? (Yes/No)")
        case _:
            ...
