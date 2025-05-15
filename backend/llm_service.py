import ollama
import os
import re # For more robust response parsing

# --- Configuration ---
# You can set the DEEPSEEK_MODEL_TAG as an environment variable
# or default to a common tag.
# Make sure you have pulled this model with Ollama (e.g., `ollama pull deepseek-coder:6.7b-instruct`)
DEEPSEEK_MODEL_TAG = os.environ.get('DEEPSEEK_MODEL_TAG', 'deepseek-coder:6.7b-instruct') # A common instruct-tuned model

# --- Main Service Function ---
def get_tests_from_deepseek(prompt_text: str) -> str | None:
    """
    Sends a prompt to the configured DeepSeek Coder model via Ollama
    and attempts to return the cleaned-up code generation.

    Args:
        prompt_text: The full prompt to send to the LLM.

    Returns:
        A string containing the generated test script, or None if an error occurs
        or if the response is empty.
    """
    print(f"Sending prompt to DeepSeek Coder (Model: {DEEPSEEK_MODEL_TAG})...")
    # For debugging, print the prompt:
    # print(f"--- PROMPT --- \n{prompt_text}\n--- END PROMPT ---")

    try:
        response = ollama.chat(
            model=DEEPSEEK_MODEL_TAG,
            messages=[
                {
                    'role': 'user',
                    'content': prompt_text,
                }
            ],
            # You might want to experiment with options like temperature for creativity,
            # but default is often fine for code generation.
            # options={
            #     'temperature': 0.5,
            # }
        )

        raw_response_content = response.get('message', {}).get('content', '')
        # print(f"--- RAW LLM RESPONSE --- \n{raw_response_content}\n--- END RAW RESPONSE ---")

        if not raw_response_content.strip():
            print("LLM returned an empty response.")
            return None

        # Attempt to extract code from markdown code blocks
        # This regex looks for content between ``` optionally followed by a language hint and then ```
        # It's non-greedy for the content inside (.*?)
        code_block_match = re.search(r"```(?:[a-zA-Z0-9_]+)?\n(.*?)\n```", raw_response_content, re.DOTALL)

        if code_block_match:
            extracted_code = code_block_match.group(1).strip()
            print("Extracted code block from LLM response.")
            return extracted_code
        else:
            # If no markdown block is found, return the whole response, stripped.
            # This might happen if the LLM doesn't use markdown, or if the prompt
            # successfully instructs it to only output code.
            print("No markdown code block found, returning stripped raw response.")
            return raw_response_content.strip()

    except Exception as e:
        # In a production app, you'd want more sophisticated logging and error handling.
        print(f"Error communicating with Ollama or processing DeepSeek Coder response: {e}")
        return None

# --- Placeholder for API-based interaction (if you switch later) ---
# DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
# DEEPSEEK_API_URL = "YOUR_DEEPSEEK_API_ENDPOINT_HERE"

# def get_tests_from_deepseek_api(prompt_text: str) -> str | None:
#     """
#     Placeholder function for interacting with a hosted DeepSeek API.
#     """
#     if not DEEPSEEK_API_KEY:
#         print("Error: DEEPSEEK_API_KEY not configured.")
#         return None
#
#     headers = {
#         "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "model": "model_name_for_api", # Specific model name for the API
#         "messages": [{"role": "user", "content": prompt_text}],
#         # Add other API-specific parameters here
#     }
#
#     try:
#         # import requests # Would need 'requests' library: pip install requests
#         # response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
#         # response.raise_for_status() # Raise an exception for bad status codes
#         # api_response_data = response.json()
#         # generated_text = api_response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
#         # return generated_text.strip() # Add similar code extraction as above
#         print("API interaction not yet implemented.")
#         return "API response placeholder"
#     except Exception as e:
#         print(f"Error with DeepSeek API: {e}")
#         return None

# --- Simple Test Block ---
if __name__ == '__main__':
    print("Testing llm_service.py...")

    # Ensure Ollama is running and the model is pulled:
    # `ollama pull deepseek-coder:6.7b-instruct` (or your chosen DEEPSEEK_MODEL_TAG)

    # Example prompt (you'll build more sophisticated ones in prompt_builder.py)
    test_code_snippet = """
def add(x, y):
    return x + y

def subtract(x, y):
    return x - y
"""
    # A simple prompt, assuming prompt_builder.py will create more detailed ones
    example_prompt = (
        f"Generate Python unittest cases for the following code. "
        f"Ensure you cover addition and subtraction with positive and negative numbers. "
        f"Only output the Python test code.\n\n"
        f"```python\n{test_code_snippet}\n```"
    )

    generated_script = get_tests_from_deepseek(example_prompt)

    if generated_script:
        print("\n--- Generated Test Script ---")
        print(generated_script)
        print("--- End of Script ---")
    else:
        print("Failed to generate test script.")
