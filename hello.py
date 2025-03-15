import os

import google.genai as generativeai  # This is the Google AI Studio client library
from langfuse.decorators import observe
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
# Replace these with your actual API keys
GENERATIVE_AI_API_KEY = os.getenv("GEMINI_API_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")

client = generativeai.Client(api_key=GENERATIVE_AI_API_KEY)


@observe
def gemini_api(prompt: str) -> str:
    """
    Calls the Gemini API via Google AI Studio to generate a response,
    while tracking the request and response using Langfuse.
    """
    # Log the API call event with Langfuse

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        return response.text
    except Exception as e:
        # Log any error events with Langfuse
        return f"An error occurred: {str(e)}"


def main():
    st.title("Chat with Gemini via Google AI Studio")
    st.write("This chatbot uses Google AI Studio's Gemini API and Langfuse for observability.")

    # Initialize the chat history in session_state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing chat messages (if any)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input via the new chat-style input box
    if prompt := st.chat_input("Say something to Gemini..."):
        # Store user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get Gemini response
        with st.chat_message("assistant"):
            response_text = gemini_api(prompt)
            st.markdown(response_text)

        # Store assistant response
        st.session_state.messages.append({"role": "assistant", "content": response_text})

if __name__ == "__main__":
    main()