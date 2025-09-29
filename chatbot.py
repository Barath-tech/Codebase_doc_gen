import os
import time
import uuid
from datetime import datetime
import weaviate
from weaviate.auth import AuthApiKey
from weaviate.classes.config import Property, DataType
from weaviate.collections.classes.filters import Filter

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ---------------- Gemini Client ----------------
class GeminiClient:
    def __init__(self, model: str = "gemini-2.5-pro"):
        """Initialize Gemini Pro client"""
        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        self.client = genai.Client(api_key=api_key)
        self.model = model

    def call_llm(self, messages: list, temperature: float = 0.7) -> str:
        """Make LLM API call with error handling."""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=messages,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    top_p=0.9,
                    top_k=40,
                ),
            )
            return response.text.strip() if response.text else "No response text returned."
        except Exception as e:
            return f"Error generating response: {str(e)}"


# ---------------- Weaviate Setup ----------------
load_dotenv()
WEAVIATE_URL="https://oxgsm0k8r3a6uxwi5tnitw.c0.asia-southeast1.gcp.weaviate.cloud"
WEAVIATE_API_KEY = "bEtxSVNhT3pQMHFMZHFvc185WCtsVWlqeDA3ejJjZjlVdWpnOEJPS0M1a0JBVk12OHVqRkxaVTd5aVE0PV92MjAw"

if not WEAVIATE_URL:
    raise ValueError("Please set WEAVIATE_URL in .env file")

# Connect to Weaviate Cloud
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,
    auth_credentials=AuthApiKey(api_key=WEAVIATE_API_KEY),
)

print("Connected to Weaviate:", client.is_ready())

llm_client = GeminiClient()


# ---------------- Schema ----------------
def setup_schema():
    """Create Message collection schema if it doesn't exist"""
    try:
        if "Message" not in client.collections.list_all().names:
            client.collections.create(
                name="Message",
                properties=[
                    Property(name="content", data_type=DataType.TEXT),
                    Property(name="role", data_type=DataType.TEXT),
                    Property(name="conversationId", data_type=DataType.TEXT),
                    Property(name="userId", data_type=DataType.TEXT),
                    Property(name="timestamp", data_type=DataType.INT),
                ],
            )
            print("Schema created successfully")
        else:
            print("Schema already exists")
    except Exception as e:
        print(f"Schema creation note: {str(e)}")



# ---------------- Store & Retrieve ----------------
def store_message(content, role, conversation_id, user_id):
    """Store a message in Weaviate with timestamps"""
    message_data = {
        "content": content,
        "role": role,
        "conversationId": conversation_id,
        "userId": user_id,
        "timestamp": int(time.time()),
    }

    try:
        client.collections.get("Message").data.insert(properties=message_data)
        print(f"Stored {role} message successfully")
    except Exception as e:
        print(f"Error storing message: {str(e)}")


def get_conversation_history(conversation_id):
    try:
        filters = Filter.by_property("conversationId").equal(conversation_id)
        response = client.collections.get("Message").query.fetch_objects(
            filters=filters,
            limit=100
        )
        messages = [obj.properties for obj in response.objects]
        return sorted(messages, key=lambda x: x["timestamp"])
    except Exception as e:
        print(f"Error retrieving conversation history: {str(e)}")
        return []



# ---------------- Formatting ----------------
# def format_messages_for_llm(messages):
#     formatted_msgs = [
#         types.Message(
#             role="system",
#             content="You are a helpful AI assistant. Maintain conversation context and provide concise responses."
#         )
#     ]

#     for msg in messages:
#         formatted_msgs.append(
#             types.Message(
#                 role=msg["role"],
#                 content=msg["content"]
#             )
#         )

#     return formatted_msgs
def format_messages_for_llm(messages):
    # Combine previous conversation into a single string
    conversation = "System: You are a helpful AI assistant. Maintain context.\n"
    for msg in messages:
        conversation += f"{msg['role'].capitalize()}: {msg['content']}\n"
    return conversation



# ---------------- Chat Loop ----------------
def chat_loop():
    """Main chat loop"""
    setup_schema()

    conversation_id = str(uuid.uuid4())
    user_id = f"user_{str(uuid.uuid4())[:8]}"

    print("\n=== RAG-Enhanced Chatbot ===")
    print("New conversation started! (Enter 'quit' to exit)")
    print(f"Conversation ID: {conversation_id}")
    print(f"User ID: {user_id}")
    print("=" * 30)

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() == "quit":
                break

            # Store user message
            store_message(user_input, "user", conversation_id, user_id)

            # Retrieve history
            history = get_conversation_history(conversation_id)

            # Format for LLM
            formatted_msgs = format_messages_for_llm(history)

            # Get Gemini response
            assistant_reply = llm_client.call_llm(formatted_msgs)

            # Store assistant reply
            store_message(assistant_reply, "assistant", conversation_id, user_id)

            # Show response
            print(f"\nAssistant: {assistant_reply}")

        except KeyboardInterrupt:
            print("\nInterrupted by user")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Continuing conversation...")


if __name__ == "__main__":
    try:
        chat_loop()
        print("\nConversation ended. Thank you for chatting!")
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
    finally:
        client.close()
