import random

import streamlit as st
from langfuse.decorators import langfuse_context, observe

from config import openai_client


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

    user_ids = ["user-1", "user-2", "user-3"]
    selected_user_id = random.choice(user_ids)

    try:
        response = openai_client.responses.create(
            model=model, instructions=instructions, input=prompt, **kwargs
        )
        langfuse_context.update_current_trace(user_id=selected_user_id)
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
