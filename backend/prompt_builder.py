# backend/prompt_builder.py
def construct_llm_prompt(code_snippet: str, module_name_to_test: str, language: str ="python", test_framework: str ="unittest", user_instructions: str | None = None) -> str:
    """
    Constructs a detailed prompt for DeepSeek Coder to generate test scripts.
    """
    instruction = (
        f"You are an expert AI programming assistant specialized in software testing. "
        f"Your task is to generate high-quality, runnable unit tests for the provided {language} code. "
        f"from the module named '{module_name_to_test}'. " # Use the module name
        f"Please import and use the module '{module_name_to_test}' in your test script. " # Explicit instruction
        f"For example, if the module is '{module_name_to_test}', you should use 'import {module_name_to_test}' and then call functions like '{module_name_to_test}.my_function()'. "
        f"If the code contains a 'main()' function within '{module_name_to_test}', assume it's the primary entry point to test unless specified otherwise. "
        f"Please use the {test_framework} framework. "
        f"The generated tests should be comprehensive, covering main functionality, typical use cases (positive tests), "
        f"and important edge cases. Where applicable, also include negative tests to check handling of invalid inputs. "
        f"Ensure all necessary imports for the {test_framework} framework, the '{module_name_to_test}' module, and any standard libraries used are included. "
        f"If using mocks (e.g., from 'unittest.mock'), ensure 'MagicMock' or 'Mock' are imported if used (e.g., 'from unittest.mock import MagicMock, patch'). " # Hint for MagicMock
        f"The output should be ONLY the {language} test code itself, formatted correctly and ready to run. "
        f"Do not include any explanatory text, apologies, or introductory/concluding sentences "
        f"outside of the code block."
    )

    if user_instructions: # If the user provides specific instructions via the frontend later
        instruction += (
            f"\n\nAdditionally, please consider the following specific user requests for the tests: "
            f"{user_instructions}"
        )

    prompt = (
        f"{instruction}\n\n"
        f"Here is the source code (`{language}`) to be tested:\n"
        f"```\n"
        f"{code_snippet}\n"
        f"```\n\n"
        f"Generated {test_framework} tests for the code above:"
    )
    return prompt