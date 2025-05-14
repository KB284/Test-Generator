def construct_llm_prompt(code_snippet, language="python", test_framework="unittest", user_instructions=None):
    """
    Constructs a detailed and effective prompt for DeepSeek Coder
    to generate test scripts.
    """
    # Base instruction tailored for test generation
    instruction = (
        f"You are an expert AI programming assistant specialized in software testing. "
        f"Your task is to generate high-quality unit tests for the provided {language} code. "
        f"Please use the {test_framework} framework. "
        f"The generated tests should be comprehensive, covering main functionality, typical use cases, "
        f"and important edge cases. "
        f"The output should be ONLY the test code itself, formatted correctly for {language} "
        f"and ready to run. Do not include any explanatory text, apologies, or introductory/concluding sentences "
        f"outside of the code block."
    )

    if user_instructions:
        instruction += f"\n\nSpecific user requests to consider: {user_instructions}"

    prompt = f"{instruction}\n\nHere is the source code:\n```{language}\n{code_snippet}\n```\n\nGenerated {test_framework} tests:"
    return prompt