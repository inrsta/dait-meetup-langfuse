from langfuse.decorators import observe
from vertexai.generative_models import GenerativeModel

@observe(as_type="generation")
def vertex_generate_content(input_text, model_name="gemini-pro"):
    # Call Vertex AI's Gemini model
    response = GenerativeModel(model_name).generate_content(
        [input_text],
        generation_config={"max_output_tokens": 8192, "temperature": 1}
    )
    return response.candidates[0].content.parts[0].text
