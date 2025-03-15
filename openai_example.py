import os
import openai  # OpenAI Python client library
from langfuse.decorators import observe
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
# Replace these with your actual API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")

openai.api_key = OPENAI_API_KEY

@observe
def openai_api(prompt: str) -> str:
    """
    Calls the OpenAI Chat Completion API to generate a response,
    while tracking the request and response using Langfuse.
    """
    try:
        # OpenAI's ChatCompletion expects a list of messages. Here we only send the user prompt.
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        # Extract the assistant's reply from the response object.
        return response.choices[0].message.content
    except Exception as e:
        # Log any error events with Langfuse and return the error message.
        return f"An error occurred: {str(e)}"

def main():
    st.title("Chat with OpenAI's GPT-3.5 Turbo")
    st.write("This chatbot uses OpenAI's GPT-3.5 Turbo API and Langfuse for observability.")

    # Initialize the chat history in session_state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing chat messages (if any)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input via the new chat-style input box
    if prompt := st.chat_input("Say something to OpenAI..."):
        # Store user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get OpenAI's response
        with st.chat_message("assistant"):
            response_text = openai_api(prompt)
            st.markdown(response_text)

        # Store assistant response
        st.session_state.messages.append({"role": "assistant", "content": response_text})

if __name__ == "__main__":
    main()
