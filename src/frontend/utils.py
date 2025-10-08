import streamlit as st


def render_initial_message(agent_name: str | None, thread_state: dict | None) -> None:
    if not thread_state:
        st.write("Create a new conversation to start chatting...")
        return

    match (agent_name):
        case "API Mapping Assistant":
            with st.chat_message("assistant"):
                st.markdown("Hallo! Ich bin dein **AEB API Mapping Assistant**. "
                            "Ich helfe dir dabei, die **TCM Screening API** sauber in dein System zu integrieren.\n\n"
                            "Möchtest du mit der Integration beginnen? (Ja/Nein)")
        case "Request Validation Assistant":
            with st.chat_message("assistant"):
                st.markdown("Hallo! Ich bin dein **AEB API Mapping Assistant**. "
                            "Ich helfe dir zu prüfen, ob dein Aufruf an die Screening API korrekt ist.")
        case "QnA Assistant":
            with st.chat_message("assistant"):
                st.markdown("Hallo! Ich bin dein **AEB API Mapping Assistant**. "
                            "Du kannst mir allgmeine Fragen zur Screening API stellen."
                            )
        case "Error Detection Assistant":
            with st.chat_message("assistant"):
                st.markdown("Hallo! Ich bin dein **AEB API Mapping Assistant**. "
                            "Ich helfe dir dabei Fehler bei der Nutzung der Screening API zu erklären."
                            "Möchtest du mit der Integration beginnen? (Ja/Nein)")
        case _:
            ...
