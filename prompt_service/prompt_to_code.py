import openai
import json
from decouple import config
import os
from services import mongo_connection


def save_conversation_to_db(conversation, filename="conversation_history.json"):
    with open(filename, "w") as file:
        json.dump(conversation, file)


def load_conversation_db(filename="conversation_history.json"):
    try:
        with open(filename, "r") as file:
            conversation = json.load(file)
    except FileNotFoundError:
        conversation = []
    return conversation


def prompt(
    app_idea,
    app_feature,
    app_look,
    user_id,
    conversation_file="conversation_history.json",
):
    user_message = f"generate the code of my website. idea of my website is {app_idea} and features of my website is {app_feature} and look of my website is {app_look} add all code of my website in single html"
    key = config("openai_key")
    openai.api_key = key  # Set the API key for the openai library

    # Load the existing conversation history
    conversation = load_conversation_db(conversation_file)

    # Append the user's message to the conversation
    conversation.append({"role": "user", "content": user_message})

    # Call OpenAI API with the entire conversation history
    response = openai.ChatCompletion.create(model="gpt-4", messages=conversation)

    # Extract the assistant's message from the response
    assistant_message = response["choices"][0]["message"]["content"]
    print(assistant_message)

    # Append the assistant's message to the conversation
    conversation.append({"role": "assistant", "content": assistant_message})

    # Save the updated conversation history to the file
    save_conversation_to_db(conversation, conversation_file)
    templates_dir = "templates"
    os.makedirs(templates_dir, exist_ok=True)

    # with open(
    #     os.path.join(templates_dir, "generated_website.html"), "w", encoding="utf-8"
    # ) as file:
    #     file.write(assistant_message)

    return assistant_message


def editprompt(prompt_input, conversation_file="conversation_history.json"):
    key = config("openai_key")
    openai.api_key = key  # Set the API key for the openai library

    # Load the existing conversation history
    conversation = load_conversation_db(conversation_file)
    prompt__edit_input = f"{prompt_input} provide me fully updated code with all updates in a single file"
    # Append the user's message to the conversation
    conversation.append({"role": "user", "content": prompt__edit_input})

    # Call OpenAI API with the entire conversation history
    response = openai.ChatCompletion.create(model="gpt-4", messages=conversation)

    # Extract the assistant's message from the response
    assistant_message = response["choices"][0]["message"]["content"]
    print(assistant_message)

    # Append the assistant's message to the conversation
    conversation.append({"role": "assistant", "content": assistant_message})

    # Save the updated conversation history to the file
    save_conversation_to_db(conversation, conversation_file)
    templates_dir = "templates"
    os.makedirs(templates_dir, exist_ok=True)

    # with open(
    #     os.path.join(templates_dir, "generated_website.html"), "w", encoding="utf-8"
    # ) as file:
    #     file.write(assistant_message)

    return assistant_message


def enhanceprompt(enhance_prompt):
    key = config("openai_key")
    openai.api_key = key  # Set the API key for the openai library
    prompt__edit_input = (
        f"{enhance_prompt} : enhance this prompt for better understanding"
    )

    conversation_input = [{"role": "user", "content": prompt__edit_input}]

    # Call OpenAI API
    response = openai.ChatCompletion.create(model="gpt-4", messages=conversation_input)

    assistant_message = response["choices"][0]["message"]["content"]
    print(assistant_message)

    return assistant_message


# Example usage:
# user_message = "Can you add a game to the home page for my visitors to play update this functionality and provide me fully updated code for my website with css and js i need full code"
# prompt(user_message)
