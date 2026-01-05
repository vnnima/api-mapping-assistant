"""
This file contains the API functions for the streamlit UI.

The easiest way to work with a Langgraph Server API in a frontend client is to use the langgraph_sdk: there are both python and javascript SDKs. Of course all of this can be done without the SDK by making requests via the requests or httpx libraries, but it's a convenient wrapper. In this example, we'll implement some of the core functions we need for a basic chat app. The complexity would grow if you want to add additional features such as human-in-the-loop.

To see the full API documentation, see your API docs at `http://localhost:2024/docs` once you've started the Langgraph Server.
"""
from langgraph_sdk import get_sync_client
from langgraph_sdk.schema import Command
from dotenv import load_dotenv
from typing import Iterator, Tuple, Literal, Dict, Any
import os

# Try to import streamlit for secrets (only available in streamlit environment)
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

load_dotenv()

# This can be a local or remote deployment URL, but it must point to a Langgraph Server
# langgraph_api = "http://localhost:2024"
langgraph_api = st.secrets.get("LANGGRAPH_API_URL") or "http://localhost:2024"

# Get the API key from environment variables or Streamlit secrets
api_key = None
if STREAMLIT_AVAILABLE and hasattr(st, 'secrets'):
    try:
        api_key = st.secrets.get("LANGSMITH_API_KEY")
    except:
        pass

if not api_key:
    api_key = os.getenv("LANGSMITH_API_KEY")

if not api_key:
    raise ValueError(
        "LANGSMITH_API_KEY environment variable or Streamlit secret is required for authentication")

# Clean the API key by stripping whitespace
api_key = api_key.strip()

# Validate the API key format
if not api_key.startswith("lsv2_"):
    raise ValueError(
        f"Invalid API key format. Expected to start with 'lsv2_', got: '{api_key[:10]}...'")

# Initialize the client with authentication headers
try:
    client = get_sync_client(
        url=langgraph_api,
        api_key=api_key  # This adds the x-api-key header automatically
    )
except Exception as e:
    raise ValueError(f"Failed to initialize LangGraph client: {e}")

EventKind = Literal["ai_chunk", "interrupt", "tool", "done", "other"]


def get_assistants():
    try:
        response = client.assistants.search()
        return response
    except Exception as e:
        raise RuntimeError(f"Failed to get assistants: {e}")


def create_thread(user_id: str, assistant_name: str | None = None):
    metadata = {"user_id": user_id}
    if assistant_name:
        metadata["assistant_name"] = assistant_name

    response = client.threads.create(metadata=metadata)
    return response


def search_threads(user_id: str):
    response = client.threads.search(
        metadata={
            "user_id": user_id,
        }
    )
    return response


def delete_thread(thread_id: str):
    response = client.threads.delete(thread_id)
    return response


def delete_all_threads(user_id: str):
    threads = search_threads(user_id)
    for thread in threads:
        delete_thread(thread["thread_id"])


def get_thread_state(thread_id: str):
    response = client.threads.get_state(thread_id)
    return response


def run_thread_stream(assistant_id: str, thread_id: str, input: dict[str, Any]):
    """
    This function processes the raw stream from the graph, yielding a string that can be rendered in the UI.

    Args:
        assistant_id (str): The assistant ID
        thread_id (str): The thread ID
        input (dict[str, Any]): The input to the graph

    Yields:
        str: The processed response from the graph
    """
    for chunk in client.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
        input=input,
        stream_mode="messages-tuple",
    ):

        # We're only interested in the messages event
        # You can add additional logic to handle other events such as metadata
        # Note that the payload of the chunk depends on the stream_mode
        if chunk.event == "messages":
            # yield chunk

            # We only want to yield AI messages
            # If you want to see the raw chunks, uncomment the `yield chunk` line above
            if chunk.data[0]["type"] == "AIMessageChunk":
                # If the AI message contains tool calls, we want to yield the tool call name and arguments
                if chunk.data[0]["tool_call_chunks"]:
                    tool_chunk = chunk.data[0]["tool_call_chunks"][0]
                    if tool_chunk["name"]:
                        yield tool_chunk["name"]
                    else:
                        yield tool_chunk["args"]
                # If the AI message does not contain tool calls, we want to yield the content
                else:
                    yield chunk.data[0]["content"]


def run_thread_events(
    assistant_id: str,
    thread_id: str,
    initial_input: Dict[str, Any] | None = None,
    resume_payload: Dict[str, Any] | None = None,
) -> Iterator[Tuple[EventKind, Any]]:
    kwargs = {"thread_id": thread_id,
              "assistant_id": assistant_id, "stream_mode": "updates"}
    if resume_payload is not None:
        # RESUME PATH
        kwargs["command"] = Command(resume=resume_payload)
    else:
        # FIRST CALL PATH
        kwargs["input"] = initial_input or {}

    try:
        for chunk in client.runs.stream(**kwargs):
            if chunk.event != "updates":
                yield ("other", {"event": chunk.event, "data": chunk.data})
                continue

            data = chunk.data or {}

            if "__interrupt__" in data:
                items = data["__interrupt__"]
                if isinstance(items, list) and items:
                    # {'value': {...}, 'id': '...'}
                    yield ("interrupt", items[0])
                else:
                    yield ("interrupt", items)
                continue

            # surface AI text
            for node_name, node_payload in data.items():
                if isinstance(node_payload, dict):
                    messages = node_payload.get("messages") or []
                    for m in messages:
                        if m.get("type") == "ai":
                            content = m.get("content", "")
                            yield ("ai_chunk", content)

        yield ("done", None)
    except Exception as e:
        import traceback
        traceback.print_exc()
        yield ("other", {"error": str(e)})


async def main():
    """
    Convenience function to cleanup all threads for a user. You can use this to manage your Langgraph Server environment while you're testing and developing.
    """

    user_id = "valdrin"
    delete_all_threads(user_id)


if __name__ == "__main__":
    import asyncio
    import nest_asyncio
    nest_asyncio.apply()

    asyncio.run(main())
