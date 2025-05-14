import ollama # Assuming local Ollama setup for DeepSeek Coder
# import requests # If using a direct API
import os

# Load from environment variables or a config file
DEEPSEEK_MODEL_TAG = os.environ.get('DEEPSEEK_MODEL_TAG', 'deepseek-coder:6.7b-instruct')

def get_tests_from_deepseek(prompt):
    """
    Sends the prompt to the configured DeepSeek Coder model and returns the response.
    """
    try:
        # Using Ollama client
        response = ollama.chat(
            model=DEEPSEEK_MODEL_TAG,
            messages=[{'role': 'user', 'content': prompt}]
        )
        generated_text = response['message']['content']

        # Basic cleaning: extract code if it's in a markdown block
        # LLMs often wrap code in ```python ... ``` or similar
        if "```" in generated_text:
            parts = generated_text.split("```")
            if len(parts) >= 2: # Found at least one code block
                code_block = parts[1]
                # Remove potential language hint from the first line of the block
                if '\n' in code_block:
                    first_line_end = code_block.find('\n')
                    return code_block[first_line_end+1:].strip() if first_line_end != -1 else code_block.strip()
                return code_block.strip()
        return generated_text.strip() # Fallback if no clear markdown block

    except Exception as e:
        print(f"Error communicating with LLM (Ollama): {e}")
        # In a real application, you might want to raise a custom error
        # or return a more structured error response.
        return None # Or raise e