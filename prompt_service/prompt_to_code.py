import openai
from decouple import config
import difflib


def prompt(prompt_input):
    key = config("openai_key")
    openai.api_key = key  # Set the API key for the openai library

    # prompt_text = "write a code for create a simple landing page for my website."

    parameters = {
        "engine": "text-davinci-003",
        "prompt": prompt_input,
        "max_tokens": 500,
        "temperature": 0.7,
    }

    response = openai.Completion.create(**parameters)  # Use openai.Completion

    generated_text = response["choices"][0]["text"].strip()
    # print(generated_text)

    return generated_text


def apply_edits(existing_content, edited_content):
    """
    Apply edits to the existing content based on the differences between
    the existing content and the edited content.
    """
    differ = difflib.Differ()
    diff = list(
        differ.compare(existing_content.splitlines(), edited_content.splitlines())
    )

    # Track the current position in the existing content
    current_position = 0

    # Iterate through the differences and apply edits
    for line in diff:
        if line.startswith(" "):
            # Unchanged line, move the current position
            current_position += len(line) + 1
        elif line.startswith("-"):
            # Line removed in the edited content, remove from existing content
            start = current_position
            end = current_position + len(line) + 1
            existing_content = existing_content[:start] + existing_content[end:]
        elif line.startswith("+"):
            # Line added in the edited content, insert into existing content
            start = current_position
            existing_content = (
                existing_content[:start] + line[2:] + existing_content[start:]
            )
        elif line.startswith("?"):
            print("hello")
            # Ignore information about the difference
    return existing_content
