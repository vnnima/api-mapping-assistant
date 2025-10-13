import streamlit as st


def render_initial_message(agent_name: str | None, thread_state: dict | None) -> None:
    if not thread_state:
        st.write("Create a new conversation to start chatting...")
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
