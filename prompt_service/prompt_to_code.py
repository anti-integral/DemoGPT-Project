import openai
from decouple import config


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
    print(generated_text)

    return generated_text
