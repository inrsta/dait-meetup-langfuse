import random

import langfuse  # Observability tool for language models
import streamlit as st
from langfuse.decorators import langfuse_context, observe

from config import gemini_client


@observe(as_type="generation")
def gemini_api(prompt: str, model: str = "gemini-1.5-flash", **kwargs) -> str:
    langfuse_context.update_current_observation(
        input=prompt, model=model, metadata=kwargs
    )

    user_ids = ["user-1", "user-2", "user-3"]
    selected_user_id = random.choice(user_ids)

    try:
        response = gemini_client.models.generate_content(
            model=model, contents=prompt, **kwargs
        )
        langfuse_context.update_current_trace(user_id=selected_user_id)
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
