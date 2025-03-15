from langfuse import Langfuse
import streamlit as st
from langfuse.decorators import langfuse_context, observe

from config import openai_client

langfuse = Langfuse()


@observe(as_type="generation")
def openai_api(
    prompt: str,
    model: str = "gpt-4o-mini",
    instructions: str = "You are a coding assistant that talks like a pirate.",
    **kwargs,
) -> str:
    # Update the current observation context with input and metadata.
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


def save_feedback(index):
    # Retrieve the feedback value stored in session state.
    # (Assume the thumbs widget returns "up" for positive and "down" for negative.)
    feedback_value = st.session_state.get(f"feedback_{index}")
    # Update the corresponding message with the new feedback.
    st.session_state.openai_messages[index]["feedback"] = feedback_value

    # Convert feedback to a score: here we assume "up" means 1 (helpful) and "down" means 0.
    score_value = 1 if feedback_value == "up" else 0
    message = st.session_state.openai_messages[index]

    # Send the score to Langfuse.
    langfuse.score(
        id=f"score_{index}",  # unique identifier (can be used for idempotency)
        trace_id=message.get("trace_id"),
        observation_id=message.get("generation_id"),  # may be None if not available
        name="helpfulness",
        value=score_value,
        data_type="BOOLEAN",
        comment="User feedback",
    )


def openai_chat_page():
    st.title("Chat with OpenAI")
    st.write("Interact with our assistant.")

    # Initialize session state for chat messages.
    if "openai_messages" not in st.session_state:
        st.session_state.openai_messages = []

    # Display the chat history along with any feedback widgets.
    for i, message in enumerate(st.session_state.openai_messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                # Ensure a feedback value exists in session state.
                st.session_state.setdefault(f"feedback_{i}", message.get("feedback"))
                st.feedback(
                    "thumbs",
                    key=f"feedback_{i}",
                    disabled=message.get("feedback") is not None,
                    on_change=save_feedback,
                    args=[i],
                )

    # Chat input: when a user sends a message.
    if prompt := st.chat_input("Say something to OpenAI..."):
        # Append and display the user's message.
        st.session_state.openai_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get the assistant's response.
        response_text = openai_api(prompt)
        # Capture the current trace id from Langfuse.
        trace_id = langfuse_context.get_current_trace_id()
        # Optionally, if available, you could extract a generation id from the response.
        generation_id = None  # Replace with a real id if applicable.

        # Create the assistant message with feedback metadata.
        assistant_message = {
            "role": "assistant",
            "content": response_text,
            "trace_id": trace_id,
            "generation_id": generation_id,
            # "feedback" key will be added once the user interacts.
        }
        st.session_state.openai_messages.append(assistant_message)
        with st.chat_message("assistant"):
            st.markdown(response_text)
            st.feedback(
                "thumbs",
                key=f"feedback_{len(st.session_state.openai_messages) - 1}",
                on_change=save_feedback,
                args=[len(st.session_state.openai_messages) - 1],
            )
