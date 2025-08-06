import openai
import time
import os
import tempfile
import glob
import json


class AssistantManager:
    """Manages the OpenAI Assistant and Vector Store for API mapping assistance."""

    def __init__(self, api_key):
        """Initialize the AssistantManager with OpenAI API key."""
        self.client = openai.OpenAI(api_key=api_key)
        self.config_file = ".assistant_config.json"

    def get_persistent_config_path(self):
        """Get the path to the persistent configuration file."""
        return os.path.join(os.path.dirname(__file__), self.config_file)

    def load_persistent_config(self):
        """Load persistent configuration from file."""
        config_path = self.get_persistent_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_persistent_config(self, config):
        """Save persistent configuration to file."""
        config_path = self.get_persistent_config_path()
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save configuration: {e}")
            return False

    def get_knowledge_base_files(self):
        """Get all files from the knowledge_base folder."""
        knowledge_base_path = os.path.join(
            os.path.dirname(__file__), "knowledge_base")
        if not os.path.exists(knowledge_base_path):
            raise FileNotFoundError("Knowledge base folder not found!")

        files = []
        for ext in ['*.md', '*.txt', '*.pdf']:
            files.extend(glob.glob(os.path.join(knowledge_base_path, ext)))
        return files

    def create_persistent_vector_store(self):
        """Create or retrieve the persistent vector store with knowledge base files."""
        try:
            config = self.load_persistent_config()

            # Check if we have a stored vector store ID and verify it still exists
            if "vector_store_id" in config:
                try:
                    vector_store = self.client.vector_stores.retrieve(
                        config["vector_store_id"])
                    return vector_store.id, "retrieved"
                except Exception as e:
                    print(f"Previous vector store no longer exists: {e}")
                    config.pop("vector_store_id", None)
                    self.save_persistent_config(config)

            vector_store = self.client.vector_stores.create(
                name="API Mapping Assistant Knowledge Base"
            )

            kb_files = self.get_knowledge_base_files()
            if kb_files:
                file_streams = [open(path, "rb") for path in kb_files]
                self.client.vector_stores.file_batches.upload_and_poll(
                    vector_store_id=vector_store.id,
                    files=file_streams
                )
                for stream in file_streams:
                    stream.close()

            # Save the vector store ID to persistent config
            config["vector_store_id"] = vector_store.id
            config["created_at"] = time.time()
            config["knowledge_base_files"] = len(kb_files) if kb_files else 0
            self.save_persistent_config(config)

            return vector_store.id, "created"

        except Exception as e:
            raise Exception(f"Error creating vector store: {e}")

    def get_system_prompt(self):
        """Load the system prompt from the system-prompt.txt file."""
        try:
            system_prompt_path = os.path.join(
                os.path.dirname(__file__), "system-prompt.txt")
            if os.path.exists(system_prompt_path):
                with open(system_prompt_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            else:
                # Fallback prompt if file doesn't exist
                return """You are an expert API mapping assistant specializing in compliance screening APIs. 

Your primary role is to:
1. Help users understand how to map their business data to compliance screening API endpoints
2. Provide guidance on data transformation and field mapping
3. Answer questions about API integration and best practices
4. Explain compliance screening concepts and requirements

You have access to comprehensive knowledge base documentation about the compliance screening APIs. Use this knowledge to provide accurate, detailed guidance.

When users upload their business data files, analyze them and provide specific mapping recommendations. Always be helpful, accurate, and provide practical implementation guidance."""
        except Exception as e:
            print(f"Error reading system prompt file: {e}")
            return "You are an AI assistant specializing in API mapping and compliance screening."

    def create_persistent_assistant(self, vector_store_id):
        """Create or retrieve the persistent assistant."""
        try:
            config = self.load_persistent_config()

            # Check if we have a stored assistant ID and verify it still exists
            if "assistant_id" in config:
                try:
                    assistant = self.client.beta.assistants.retrieve(
                        config["assistant_id"])
                    return assistant.id, "retrieved"
                except Exception as e:
                    print(f"Previous assistant no longer exists: {e}")
                    # Remove invalid ID from config
                    config.pop("assistant_id", None)
                    self.save_persistent_config(config)

            assistant = self.client.beta.assistants.create(
                name="API Mapping Assistant",
                instructions=self.get_system_prompt(),
                model="gpt-4.1-2025-04-14"
                tools=[{"type": "file_search"}],
                tool_resources={"file_search": {
                    "vector_store_ids": [vector_store_id]
                }},
            )

            config["assistant_id"] = assistant.id
            config["assistant_created_at"] = time.time()
            self.save_persistent_config(config)

            return assistant.id, "created"

        except Exception as e:
            raise Exception(f"Error creating assistant: {e}")

    def initialize_assistant(self):
        """Initialize the assistant and vector store. Returns (vector_store_id, assistant_id, status)."""
        try:
            vector_store_id, vs_status = self.create_persistent_vector_store()

            assistant_id, assistant_status = self.create_persistent_assistant(
                vector_store_id)

            if vs_status == "retrieved" and assistant_status == "retrieved":
                status = "retrieved"
            elif vs_status == "created" or assistant_status == "created":
                status = "created"
            else:
                status = "mixed"

            return vector_store_id, assistant_id, status

        except Exception as e:
            raise Exception(f"Failed to initialize assistant: {e}")

    def create_thread(self):
        """Create a new conversation thread."""
        try:
            thread = self.client.beta.threads.create()
            return thread.id
        except Exception as e:
            raise Exception(f"Error creating thread: {e}")

    def add_user_files_to_vector_store(self, vector_store_id, uploaded_files):
        """Add user's business data files to the existing vector store."""
        try:
            file_paths = []
            for uploaded_file in uploaded_files:
                temp_dir = tempfile.gettempdir()
                temp_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                file_paths.append(temp_path)

            file_streams = [open(path, "rb") for path in file_paths]

            file_batch = self.client.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store_id,
                files=file_streams
            )

            for stream in file_streams:
                stream.close()

            for path in file_paths:
                try:
                    os.remove(path)
                except:
                    pass

            return True

        except Exception as e:
            raise Exception(f"Error adding files to vector store: {e}")

    def send_message(self, thread_id, message):
        """Send a message to the thread."""
        try:
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message,
            )
            return True
        except Exception as e:
            raise Exception(f"Error sending message: {e}")

    def run_assistant(self, thread_id, assistant_id):
        """Run the assistant and return the response."""
        try:
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=thread_id,
                assistant_id=assistant_id,
            )

            if run.status == 'completed':
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread_id)

                assistant_response = messages.data[0].content[0].text.value
                return assistant_response, "completed"
            else:
                return None, run.status

        except Exception as e:
            raise Exception(f"Error running assistant: {e}")

    def cleanup_persistent_resources(self):
        """Clean up persistent resources (vector store and assistant)."""
        config = self.load_persistent_config()
        results = []

        try:
            if "vector_store_id" in config:
                try:
                    self.client.vector_stores.delete(config["vector_store_id"])
                    results.append(("vector_store", "deleted"))
                except Exception as e:
                    results.append(("vector_store", f"error: {e}"))

            if "assistant_id" in config:
                try:
                    self.client.beta.assistants.delete(config["assistant_id"])
                    results.append(("assistant", "deleted"))
                except Exception as e:
                    results.append(("assistant", f"error: {e}"))

            config_path = self.get_persistent_config_path()
            if os.path.exists(config_path):
                os.remove(config_path)
                results.append(("config_file", "removed"))

            return results

        except Exception as e:
            raise Exception(f"Error during cleanup: {e}")

    def get_system_status(self):
        """Get the current system status information."""
        config = self.load_persistent_config()

        status = {
            "has_config": bool(config),
            "vector_store_active": "vector_store_id" in config,
            "assistant_active": "assistant_id" in config,
            "config": config
        }

        return status
