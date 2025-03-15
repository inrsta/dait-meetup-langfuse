# Langfuse Demo

This repository demonstrates how to build a multi-model chatbot application using Langfuse for observability. It integrates three chat models:
- Gemini via Google AI Studio
- OpenAI’s GPT models
- Anthropic’s Claude

## Overview

The demo uses [Streamlit](https://streamlit.io/) for the UI, connecting to each API via dedicated pages:
- `gemini_page.py` for Gemini
- `openai_page.py` for OpenAI
- `anthropic_page.py` for Anthropics (Claude)

Each page sends requests to the respective API while tracking requests and responses with Langfuse.

## Installation

1. Ensure you have [uv](https://docs.astral.sh/uv/getting-started/installation/) installed.
2. Install dependencies by running:
   ```bash
   uv sync
   ```
3. Activate the virtual environment:
   - **MacOS**:
     ```bash
     source .venv/bin/activate
     ```
   - **Windows**:
     ```bash
     .venv\Scripts\activate
     ```

## Environment Variables

Before running the application, set the following environment variables:

```bash
GEMINI_API_KEY
LANGFUSE_SECRET_KEY
LANGFUSE_PUBLIC_KEY
LANGFUSE_HOST
OPENAI_API_KEY
ANTHROPIC_API_KEY
```

These credentials are used to access the relevant APIs.

## Running the Application

Launch the demo with Streamlit:
```bash
streamlit run main.py
```

Use the sidebar in the application to choose between Gemini Chat, OpenAI Chat, or Anthropic Chat.

## Project Structure

- `main.py`: The entry point to launch the Streamlit app.
- `config.py`: API client configuration and environment variable loading.
- `gemini_page.py`, `openai_page.py`, `anthropic_page.py`: Pages for interacting with respective APIs.
- `pyproject.toml`: Project configuration and dependencies.

## Additional Information

- The app uses Langfuse to track requests and responses, ensuring observability over language models.
- For further customization or issues, check the individual pages for specific API integrations.

Happy chatting!