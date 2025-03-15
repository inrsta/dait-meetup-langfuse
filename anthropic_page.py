import streamlit as st
import langfuse  # Observability tool for language models
from langfuse.decorators import observe, langfuse_context
from config import anthropic_client

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
        # Join text if response.content is a list of TextBlock objects.
        if isinstance(response.content, list):
            return "\n".join(block.text for block in response.content)
        return response.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

def anthropic_page():
    st.title("Chat with Anthropics' Claude Model")
    st.write("This chatbot uses Anthropics' API (Claude) and Langfuse for observability.")

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
