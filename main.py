import streamlit as st
from gemini_page import gemini_page
from openai_page import openai_page
from anthropic_page import anthropic_page

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
