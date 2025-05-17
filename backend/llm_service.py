import ollama
import os
import re # For more robust response parsing

# --- Configuration ---
DEEPSEEK_MODEL_TAG = os.environ.get('DEEPSEEK_MODEL_TAG', 'deepseek-coder:6.7b-instruct')

# --- Helper function to clean LLM artifacts ---
def _clean_llm_artifacts(text: str) -> str:
    """Removes known LLM artifacts from the text, focusing on <｜...｜> style tags."""
    if not text:
        return ""

    cleaned_text = text

    # This more general pattern aims to remove any tags of the form <｜...｜>
    # It matches:
    # - Literal "<｜"
    # - Followed by any characters that are NOT a pipe, zero or more times, non-greedily ([^｜]*?)
    #   (Using [^｜] to avoid issues if the content inside the tag itself has > or < )
    # - Followed by literal "｜>"
    # Using re.escape for the literal parts of the delimiter is safest.
    tag_pattern = re.compile(re.escape("<｜") + r"[^｜]*?" + re.escape("｜>"))

    cleaned_text = tag_pattern.sub("", cleaned_text)

    # You can add other specific string replacements here if needed for other artifact types
    # For example:
    # cleaned_text = cleaned_text.replace("SOME_OTHER_UNWANTED_BOILERPLATE", "")
    return cleaned_text.strip() # Remove leading/trailing whitespace from the final result

# --- Main Service Function ---
def get_tests_from_deepseek(prompt_text: str) -> str | None:
    """
    Sends a prompt to the configured DeepSeek Coder model via Ollama
    and attempts to return the cleaned-up code generation.
    """
    print(f"Sending prompt to DeepSeek Coder (Model: {DEEPSEEK_MODEL_TAG})...")
    # For debugging the prompt sent to the LLM:
    # print(f"--- PROMPT SENT TO LLM --- \n{prompt_text}\n--- END PROMPT ---")

    try:
        response = ollama.chat(
            model=DEEPSEEK_MODEL_TAG,
            messages=[
                {
                    'role': 'user',
                    'content': prompt_text,
                }
            ]
            # options={ 'temperature': 0.3 } # Example: Lower temperature for more deterministic code
        )

        raw_response_content = response.get('message', {}).get('content', '')
        # For debugging the raw response from LLM:
        # print(f"--- RAW LLM RESPONSE --- \n{raw_response_content}\n--- END RAW RESPONSE ---")

        if not raw_response_content.strip():
            print("LLM returned an empty response.")
            return None

        # Step 1: Extract content from markdown code blocks if present
        # This regex looks for content between ``` optionally followed by a language hint and then ```
        code_block_match = re.search(r"```(?:[a-zA-Z0-9_]+)?\n(.*?)\n```", raw_response_content, re.DOTALL)

        content_to_clean = ""
        if code_block_match:
            extracted_code = code_block_match.group(1).strip()
            print("Extracted content from markdown code block.")
            content_to_clean = extracted_code
        else:
            print("No markdown code block found, using stripped raw response for cleaning.")
            content_to_clean = raw_response_content.strip()

        # Step 2: Clean known LLM artifacts from the extracted/raw content
        final_cleaned_code = _clean_llm_artifacts(content_to_clean)

        # print(f"--- CLEANED LLM RESPONSE (to be returned) --- \n{final_cleaned_code}\n--- END CLEANED RESPONSE ---")

        return final_cleaned_code if final_cleaned_code else None # Avoid returning empty string if all was cleaned

    except Exception as e:
        print(f"Error communicating with Ollama or processing DeepSeek Coder response: {e}")
        # Consider logging the full traceback here in a real app: app.logger.error(..., exc_info=True)
        return None

    # --- Simple Test Block ---
if __name__ == '__main__':
    print("Testing llm_service.py's _clean_llm_artifacts function...")
    test_text_with_artifact_1 = "def test_method(self, mocked<｜begin of sentence｜>):"
    test_text_with_artifact_2 = "Some text <｜some_other_tag｜> and more."
    test_text_no_artifact = "def clean_method(self, arg):"

    print(f"\nOriginal 1: '{test_text_with_artifact_1}'")
    print(f"Cleaned 1  : '{_clean_llm_artifacts(test_text_with_artifact_1)}'")

    print(f"\nOriginal 2: '{test_text_with_artifact_2}'")
    print(f"Cleaned 2  : '{_clean_llm_artifacts(test_text_with_artifact_2)}'")

    print(f"\nOriginal 3: '{test_text_no_artifact}'")
    print(f"Cleaned 3  : '{_clean_llm_artifacts(test_text_no_artifact)}'")


# --- Simple Test Block (can be kept for direct testing of this module) ---
if __name__ == '__main__':
    print("Testing llm_service.py...")
    test_code_snippet = "def example_func(x):\n    return x * 2"
    example_prompt = (
        f"Generate Python unittest cases for the following code. Only output the Python test code.\n\n"
        f"```python\n{test_code_snippet}\n```"
    )
    # Example of text with an artifact for testing the cleaner
    test_text_with_artifact = "def hello():\n    print(\"Hello<｜begin of sentence｜> World!\")"
    print(f"\nOriginal text with artifact: '{test_text_with_artifact}'")
    print(f"Cleaned text: '{_clean_llm_artifacts(test_text_with_artifact)}'")

    print("\nAttempting to call actual LLM (ensure Ollama is running and model is pulled):")
    generated_script = get_tests_from_deepseek(example_prompt)
    if generated_script:
        print("\n--- Generated Test Script (from LLM) ---")
        print(generated_script)
        print("--- End of Script ---")
    else:
        print("Failed to generate test script from LLM.")