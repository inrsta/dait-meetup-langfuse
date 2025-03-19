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
) -> dict:
    # Debug: Log input details.
    print("DEBUG: Starting openai_api")
    print(f"DEBUG: Input prompt: {prompt}")
    print(f"DEBUG: Model: {model}")
    print(f"DEBUG: Additional kwargs: {kwargs}")

    # Update the current observation context with input and metadata.
    langfuse_context.update_current_observation(
        input=prompt, model=model, metadata=kwargs
    )
    # Capture the trace ID immediately.
    trace_id = langfuse_context.get_current_trace_id()
    print(f"DEBUG: Captured Trace ID: {trace_id}")

    try:
        response = openai_client.responses.create(
            model=model, instructions=instructions, input=prompt, **kwargs
        )
        print(f"DEBUG: Received response from openai_client: {response}")

        if hasattr(response, "usage"):
            usage_details = {
                "input": getattr(response.usage, "input_tokens", None),
                "output": getattr(response.usage, "output_tokens", None),
            }
            print(f"DEBUG: Response usage details: {usage_details}")
            langfuse_context.update_current_observation(usage_details=usage_details)
        # Return both the response text and the trace ID.
        result = {"output_text": response.output_text, "trace_id": trace_id}
        print(f"DEBUG: openai_api result: {result}")
        return result
    except Exception as e:
        print(f"DEBUG: Exception in openai_api: {e}")
        return {"output_text": f"An error occurred: {str(e)}", "trace_id": trace_id}


def save_feedback(index):
    print(f"DEBUG: Saving feedback for message index {index}")
    # Retrieve the feedback value stored in session state.
    feedback_value = st.session_state.get(f"feedback_{index}")
    print(f"DEBUG: Feedback value for message index {index}: {feedback_value}")

    # Update the corresponding message with the new feedback.
    st.session_state.openai_messages[index]["feedback"] = feedback_value

    # Convert feedback to a score: here "up" means 1 (helpful) and "down" means 0.
    score_value = 1 if (feedback_value == "up" or feedback_value == 1) else 0
    message = st.session_state.openai_messages[index]
    print(f"DEBUG: Message being scored: {message}")

    # Debug: Log details before sending score.
    trace_id = message.get("trace_id")
    print(
        f"DEBUG: Sending score for message index {index} with trace_id: {trace_id}, score_value: {score_value}"
    )
    try:
        # Use only the trace_id (like the hardcoded version that works)
        langfuse.score(
            id=f"score-{trace_id}",
            trace_id=trace_id,
            # trace_name="openai_api2",
            name="helpfulness",
            value=int(score_value),
            data_type="BOOLEAN",
            comment="Feedback",
        )

    except Exception as e:
        print(f"DEBUG: Exception when sending score: {e}")


def openai_chat_page():
    st.title("Chat with OpenAI")
    st.write("Interact with our assistant.")

    # Debug: Log the starting state.
    print("DEBUG: Starting openai_chat_page")
    if "openai_messages" not in st.session_state:
        st.session_state.openai_messages = []
        print("DEBUG: Initialized st.session_state.openai_messages as empty list")
    else:
        print(f"DEBUG: Existing openai_messages: {st.session_state.openai_messages}")

    # Display the chat history along with any feedback widgets.
    for i, message in enumerate(st.session_state.openai_messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
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
        print(f"DEBUG: Received chat input: {prompt}")
        # Append and display the user's message.
        st.session_state.openai_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        print(
            f"DEBUG: Appended user message. Current openai_messages: {st.session_state.openai_messages}"
        )

        # Get the assistant's response along with the trace ID.
        result = openai_api(prompt)
        print(f"DEBUG: openai_api returned: {result}")
        response_text = result["output_text"]
        trace_id = result["trace_id"]
        # Optionally, if available, you could extract a generation id from the response.
        # In this case, we'll omit it.
        assistant_message = {
            "role": "assistant",
            "content": response_text,
            "trace_id": trace_id,
        }
        st.session_state.openai_messages.append(assistant_message)
        print(f"DEBUG: Added assistant message: {assistant_message}")
        with st.chat_message("assistant"):
            st.markdown(response_text)
            st.feedback(
                "thumbs",
                key=f"feedback_{len(st.session_state.openai_messages) - 1}",
                on_change=save_feedback,
                args=[len(st.session_state.openai_messages) - 1],
            )
