import openai
import json
from decouple import config
import os


def save_conversation_to_file(conversation, filename="conversation_history.json"):
    with open(filename, "w") as file:
        json.dump(conversation, file)


def load_conversation_from_file(filename="conversation_history.json"):
    try:
        with open(filename, "r") as file:
            conversation = json.load(file)
    except FileNotFoundError:
        conversation = []
    return conversation


def prompt(
    app_idea, app_feature, app_look, conversation_file="conversation_history.json"
):
    user_message = f"generate the code of my website. Title of my website is {app_idea} and features of my website is {app_feature} add all code of my website in single html "
    key = config("openai_key")
    openai.api_key = key  # Set the API key for the openai library

    # Load the existing conversation history
    conversation = load_conversation_from_file(conversation_file)

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
    save_conversation_to_file(conversation, conversation_file)
    templates_dir = "templates"
    os.makedirs(templates_dir, exist_ok=True)

    # with open(
    #     os.path.join(templates_dir, "generated_website.html"), "w", encoding="utf-8"
    # ) as file:
    #     file.write(assistant_message)

    return assistant_message


def editprompt(
    app_idea, app_feature, app_look, conversation_file="conversation_history.json"
):
    user_message = f"generate the code of my website. Title of my website is {app_idea} and features of my website is {app_feature} add all code of my website in single html "
    key = config("openai_key")
    openai.api_key = key  # Set the API key for the openai library

    # Load the existing conversation history
    conversation = load_conversation_from_file(conversation_file)

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
    save_conversation_to_file(conversation, conversation_file)
    templates_dir = "templates"
    os.makedirs(templates_dir, exist_ok=True)

    # with open(
    #     os.path.join(templates_dir, "generated_website.html"), "w", encoding="utf-8"
    # ) as file:
    #     file.write(assistant_message)

    return assistant_message


# Example usage:
# user_message = "Can you add a game to the home page for my visitors to play update this functionality and provide me fully updated code for my website with css and js i need full code"
# prompt(user_message)
