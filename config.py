import os
from dotenv import load_dotenv
import google.genai as generativeai  # For Gemini API
from openai import OpenAI           # For OpenAI API (new interface)
import anthropic                   # For Anthropics' API (Claude)

load_dotenv()

# API keys and configuration
GENERATIVE_AI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Set up API clients
gemini_client = generativeai.Client(api_key=GENERATIVE_AI_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)
anthropic_client = anthropic.Client(api_key=ANTHROPIC_API_KEY)
