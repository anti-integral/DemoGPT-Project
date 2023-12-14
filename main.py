from fastapi import FastAPI
import random
import openai
from decouple import config

app = FastAPI()


@app.get("/")
def prompt():
    key = config("openai_key")
    openai.api_key = key
    prompt_text = "write a code for create a simple landing page for my website."
    # Set the parameters for the OpenAI API call
    parameters = {
        "engine": "text-davinci-003",  # You can use a different engine if needed
        "prompt": prompt_text,
        "max_tokens": 100,  # Adjust as needed
        "temperature": 0.7,  # Adjust as needed (higher values for more randomness)
    }

    # Make the OpenAI API call
    response = openai.Completion.create(**parameters)

    # Get and return the generated text from the response
    generated_text = response["choices"][0]["text"].strip()
    return generated_text
