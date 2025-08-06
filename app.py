import streamlit as st
import time
from assistant_manager import AssistantManager

st.set_page_config(
    page_title="API Mapping Assistant",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("🛡️ API Mapping Assistant")
st.caption(
    "I'll help you map your business data to our compliance screening APIs. Upload your business data and ask me questions!")

def get_openai_client():
    """Get OpenAI API key from secrets."""
    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API key not found. Please add it to your secrets.")
        st.stop()
    return api_key


def initialize_session_state():
    """Initializes session state variables if they don't exist."""
    defaults = {
        "messages": [],
        "thread_id": None,
        "assistant_id": None,
        "vector_store_id": None,
        "assistant_ready": False,
        "uploaded_files_count": 0,
        "assistant_manager": None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def display_system_status(assistant_manager):
    """Display the system status in an expander."""
    status = assistant_manager.get_system_status()

    if status["has_config"]:
        with st.expander("🔧 System Status", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                if status["vector_store_active"]:
                    st.success("📚 Vector Store: Active")
                    st.caption(
                        f"ID: {status['config']['vector_store_id'][:20]}...")
                    if "knowledge_base_files" in status["config"]:
                        st.caption(
                            f"Knowledge base files: {status['config']['knowledge_base_files']}")

                if status["assistant_active"]:
                    st.success("🤖 Assistant: Active")
                    st.caption(
                        f"ID: {status['config']['assistant_id'][:20]}...")

            with col2:
                if "created_at" in status["config"]:
                    created_time = time.strftime(
                        "%Y-%m-%d %H:%M:%S",
                        time.localtime(status["config"]["created_at"])
                    )
                    st.info(f"Created: {created_time}")

                if st.button("🗑️ Reset System", help="Delete all persistent resources and start fresh"):
                    try:
                        results = assistant_manager.cleanup_persistent_resources()
                        for resource, result in results:
                            if "error" in result:
                                st.warning(f"{resource}: {result}")
                            else:
                                st.success(f"✅ {resource}: {result}")

                        # Clear session state
                        for key in ["assistant_id", "vector_store_id", "assistant_ready", "thread_id", "messages"]:
                            if key in st.session_state:
                                del st.session_state[key]

                        st.success(
                            "System reset complete! Refresh the page to restart.")
                        st.stop()
                    except Exception as e:
                        st.error(f"Error during cleanup: {e}")


def initialize_assistant(assistant_manager):
    """Initialize the assistant and show appropriate progress messages."""
    try:
        # Check current status
        status = assistant_manager.get_system_status()
        reusing_resources = status["vector_store_active"] and status["assistant_active"]

        if reusing_resources:
            with st.spinner("🔄 Connecting to existing assistant and knowledge base..."):
                vector_store_id, assistant_id, init_status = assistant_manager.initialize_assistant()
                thread_id = assistant_manager.create_thread()

                st.session_state.vector_store_id = vector_store_id
                st.session_state.assistant_id = assistant_id
                st.session_state.thread_id = thread_id
                st.session_state.assistant_ready = True
                st.rerun()
        else:
            with st.spinner("🚀 Setting up API Mapping Assistant with knowledge base... This will only take a moment and is done once."):
                vector_store_id, assistant_id, init_status = assistant_manager.initialize_assistant()
                thread_id = assistant_manager.create_thread()

                # Show loading progress for knowledge base
                if init_status == "created":
                    kb_files = assistant_manager.get_knowledge_base_files()
                    st.info(
                        f"📚 Loading {len(kb_files)} knowledge base files...")

                st.session_state.vector_store_id = vector_store_id
                st.session_state.assistant_id = assistant_id
                st.session_state.thread_id = thread_id
                st.session_state.assistant_ready = True
                st.rerun()

    except Exception as e:
        st.error(f"Failed to initialize assistant: {e}")
        st.stop()


def handle_file_upload(assistant_manager):
    """Handle the file upload functionality in the sidebar."""
    st.header("📁 Upload Your Business Data")

    if st.session_state.assistant_ready:
        st.success("✅ Assistant is ready!")

        # File uploader for user's business data
        uploaded_files = st.file_uploader(
            "Upload your business data files",
            accept_multiple_files=True,
            type=['pdf', 'txt', 'md', 'docx', 'csv', 'xlsx'],
            help="Upload your business data files for mapping analysis."
        )

        if uploaded_files and st.button("Add Files to Analysis"):
            with st.spinner("Adding your files to the knowledge base..."):
                try:
                    assistant_manager.add_user_files_to_vector_store(
                        st.session_state.vector_store_id,
                        uploaded_files
                    )
                    st.session_state.uploaded_files_count += len(
                        uploaded_files)
                    st.success(
                        f"✅ Added {len(uploaded_files)} files! Total files: {st.session_state.uploaded_files_count}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error uploading files: {e}")

        if st.session_state.uploaded_files_count > 0:
            st.info(
                f"📊 {st.session_state.uploaded_files_count} business data files uploaded")

        # Reset conversation button
        if st.button("🔄 Reset Conversation"):
            try:
                thread_id = assistant_manager.create_thread()
                st.session_state.thread_id = thread_id
                st.session_state.messages = []
                st.success("Conversation reset!")
                st.rerun()
            except Exception as e:
                st.error(f"Error resetting conversation: {e}")
    else:
        st.warning("⏳ Initializing assistant...")


def display_welcome_message():
    """Display the welcome message when no conversation has started."""
    with st.chat_message("assistant"):
        welcome_msg = """👋 **Welcome to the API Mapping Assistant!**

I'm here to help you map your business data to our compliance screening APIs. Here's what I can do:

🔍 **Analyze your data structure** and recommend API mappings
📋 **Explain API endpoints** and their requirements  
🛠️ **Provide implementation guidance** and best practices

**To get started:**
1. Upload your ERP data files using the sidebar
2. Ask me questions about Compliance Screening API mapping
3. Get specific recommendations for your data

Try asking: *"How do I map customer data to the screening API?"* or *"What fields are required for entity screening?"*"""
        st.markdown(welcome_msg)


def handle_chat_interaction(assistant_manager):
    """Handle the main chat interface."""
    if not st.session_state.assistant_ready:
        st.info(
            "🚀 Setting up your API Mapping Assistant... This may take a moment on first launch.")
        return

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if not st.session_state.messages:
        display_welcome_message()

    if prompt := st.chat_input("Ask me about API mapping, upload your data, or any compliance questions..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("🤔 Analyzing and preparing response..."):
            try:
                assistant_manager.send_message(
                    st.session_state.thread_id, prompt)

                response, status = assistant_manager.run_assistant(
                    st.session_state.thread_id,
                    st.session_state.assistant_id
                )

                if status == "completed":
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response})
                    with st.chat_message("assistant"):
                        st.markdown(response)
                else:
                    st.error(
                        f"❌ The assistant run failed with status: {status}")

            except Exception as e:
                st.error(
                    f"❌ An error occurred while communicating with the assistant: {e}")

def main():
    """Main application entry point."""
    initialize_session_state()

    api_key = get_openai_client()

    if st.session_state.assistant_manager is None:
        st.session_state.assistant_manager = AssistantManager(api_key)

    assistant_manager = st.session_state.assistant_manager

    display_system_status(assistant_manager)

    if not st.session_state.assistant_ready:
        initialize_assistant(assistant_manager)

    with st.sidebar:
        handle_file_upload(assistant_manager)

    handle_chat_interaction(assistant_manager)


if __name__ == "__main__":
    main()
