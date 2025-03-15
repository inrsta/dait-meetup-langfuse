import os
import streamlit as st
from dotenv import load_dotenv
from langfuse.decorators import observe, langfuse_context

# Import the necessary client libraries
import google.genai as generativeai  # For Gemini API
from openai import OpenAI  # For OpenAI API (new interface)
import anthropic  # For Anthropics' API (Claude)

# Load environment variables
load_dotenv()

# API keys and configuration
GENERATIVE_AI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")  # New key for Anthropics
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")

# Set up API clients
gemini_client = generativeai.Client(api_key=GENERATIVE_AI_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)
anthropic_client = anthropic.Client(
    api_key=ANTHROPIC_API_KEY
)  # Instantiate Anthropics client


@observe(as_type="generation")
def gemini_api(prompt: str, model: str = "gemini-1.5-flash", **kwargs) -> str:
    langfuse_context.update_current_observation(
        input=prompt, model=model, metadata=kwargs
    )
    try:
        response = gemini_client.models.generate_content(
            model=model, contents=prompt, **kwargs
        )
        if hasattr(response, "usage"):
            langfuse_context.update_current_observation(
                usage_details={
                    "input": getattr(response.usage, "input_tokens", None),
                    "output": getattr(response.usage, "output_tokens", None),
                }
            )
        return response.text
    except Exception as e:
        return f"An error occurred: {str(e)}"


def gemini_page():
    st.title("Chat with Gemini via Google AI Studio")
    st.write(
        "This chatbot uses Google AI Studio's Gemini API and Langfuse for observability."
    )

    if "gemini_messages" not in st.session_state:
        st.session_state.gemini_messages = []

    for message in st.session_state.gemini_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Say something to Gemini..."):
        st.session_state.gemini_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_text = gemini_api(prompt)
            st.markdown(response_text)

        st.session_state.gemini_messages.append(
            {"role": "assistant", "content": response_text}
        )


@observe(as_type="generation")
def openai_api(
    prompt: str,
    model: str = "gpt-4.5-preview",
    instructions: str = "You are a coding assistant that talks like a pirate.",
    **kwargs,
) -> str:
    langfuse_context.update_current_observation(
        input=prompt, model=model, metadata=kwargs
    )
    try:
        response = openai_client.responses.create(
            model=model, instructions=instructions, input=prompt, **kwargs
        )
        if hasattr(response, "usage"):
            langfuse_context.update_current_observation(
                usage_details={
                    "input": getattr(response.usage, "input_tokens", None),
                    "output": getattr(response.usage, "output_tokens", None),
                }
            )
        return response.output_text
    except Exception as e:
        return f"An error occurred: {str(e)}"


def openai_page():
    st.title("Chat with OpenAI's GPT Model")
    st.write(
        "This chatbot uses OpenAI's GPT API (via the new Responses interface) and Langfuse for observability."
    )

    if "openai_messages" not in st.session_state:
        st.session_state.openai_messages = []

    for message in st.session_state.openai_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Say something to OpenAI..."):
        st.session_state.openai_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        response_text = openai_api(prompt)

        with st.chat_message("assistant"):
            st.markdown(response_text)

        st.session_state.openai_messages.append(
            {"role": "assistant", "content": response_text}
        )


@observe(as_type="generation")
def anthropic_api(
    prompt: str, model: str = "claude-3-5-sonnet-latest", **kwargs
) -> str:
    """
    Calls the Anthropics API (Claude) to generate a response,
    while tracking the request and response using Langfuse.

    Note: We use the official method 'messages.create()' to obtain the response.
    If Claude were a stand-up comedian, it might joke that it doesn't do 'completion'
    anymore—it just delivers punchlines via 'message.content'!
    """
    langfuse_context.update_current_observation(
        input=prompt, model=model, metadata=kwargs
    )
    try:
        response = anthropic_client.messages.create(
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
            model=model,
            **kwargs,
        )
        return response.content[0].text
    except Exception as e:
        return f"An error occurred: {str(e)}"


def anthropic_page():
    st.title("Chat with Anthropics' Claude Model")
    st.write(
        "This chatbot uses Anthropics' API (Claude) and Langfuse for observability."
    )

    if "anthropic_messages" not in st.session_state:
        st.session_state.anthropic_messages = []

    for message in st.session_state.anthropic_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Say something to Anthropic..."):
        st.session_state.anthropic_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        response_text = anthropic_api(prompt)

        with st.chat_message("assistant"):
            st.markdown(response_text)

        st.session_state.anthropic_messages.append(
            {"role": "assistant", "content": response_text}
        )


def main():
    st.sidebar.title("Chat Options")
    chat_option = st.sidebar.radio(
        "Choose a chat", ("Gemini Chat", "OpenAI Chat", "Anthropic Chat")
    )

    if chat_option == "Gemini Chat":
        gemini_page()
    elif chat_option == "OpenAI Chat":
        openai_page()
    elif chat_option == "Anthropic Chat":
        anthropic_page()


if __name__ == "__main__":
    main()
