import openai
import json
from decouple import config
import os
from services import mongo_connection
from datetime import datetime
from services.filter_result import filter_code
from prompt_service.prompt_generator import (
    build_messages,
    edit_web_build_messages,
    image_build_messages,
)

key = config("openai_key")


def save_conversation_to_db(
    user_id, project_id, conversation, app_idea=None, app_feature=None, app_look=None
):
    chat_history_document = {
        "user_id": user_id,
        "app_idea": app_idea,
        "app_feature": app_feature,
        "app_look": app_look,
        "project_id": project_id,
        "conversation": conversation,
        "timestamp": datetime.now(),
    }
    result = mongo_connection.userchathistory.insert_one(chat_history_document)


# ------------------------------------------prompt--------------------------------------------------------


def prompt(
    app_idea,
    app_feature,
    app_look,
    user_id,
    project_id,
):
    # user_message = f"generate the code of my website. idea of my website is {app_idea} and features of my website is {app_feature} and look of my website is {app_look} add all code of my website in single html"
    user_message = f"idea of my website is {app_idea} and features of my website is {app_feature} and look of my website is {app_look}"
    prompt_messages = build_messages(user_message)
    openai.api_key = key  # Set the API key for the openai library
    response = openai.ChatCompletion.create(model="gpt-4", messages=prompt_messages)

    # Append the user's message to the conversation
    input_conversation = {"role": "user", "content": user_message}

    # Call OpenAI API with the entire conversation history

    # Extract the assistant's message from the response
    assistant_message = response["choices"][0]["message"]["content"]

    generated_code = filter_code(assistant_message)
    if generated_code:
        # Append the assistant's message to the conversation
        assistant_conversation = {"role": "assistant", "content": generated_code}
    else:
        assistant_conversation = {"role": "assistant", "content": assistant_message}

    conversation = [input_conversation, assistant_conversation]
    save_conversation_to_db(
        user_id,
        project_id,
        conversation,
        app_idea,
        app_feature,
        app_look,
    )

    # templates_dir = "templates"
    # os.makedirs(templates_dir, exist_ok=True)

    return generated_code


# ------------------------------------------editprompt--------------------------------------------------------


def editprompt(prompt_input, user_id, project_id):
    openai.api_key = key  # Set the API key for the openai library
    # prompt_edit_input = f"{prompt_input} provide me fully updated code with all updates in a single file"
    prompt_edit_input = f"this is updates of my web page {prompt_input} Return only the full code in <html></html> tags"
    prompt_edit_message = edit_web_build_messages(prompt_edit_input)
    query = {
        "user_id": user_id,
        "project_id": project_id,
    }
    chat_history_document = mongo_connection.userchathistory.find_one(query)

    if chat_history_document:
        conversation_list = chat_history_document.get("conversation", [])
    else:
        print("Document not found for the given user_id and project_id.")

    # conversation_list.append({"role": "user", "content": prompt_edit_input})
    conversation_list.extend(prompt_edit_message)
    # Call OpenAI API with the entire conversation history
    response = openai.ChatCompletion.create(model="gpt-4", messages=conversation_list)

    assistant_message = response["choices"][0]["message"]["content"]
    generated_code = filter_code(assistant_message)

    if generated_code:
        # Append the assistant's message to the conversation
        assistant_conversation = {"role": "assistant", "content": generated_code}
    else:
        assistant_conversation = {"role": "assistant", "content": assistant_message}

    input_conversation = {"role": "user", "content": prompt_edit_input}
    new_conversation_data = [input_conversation, assistant_conversation]
    update_operation = {"$set": {"conversation": new_conversation_data}}
    update_result = mongo_connection.userchathistory.update_one(query, update_operation)

    if update_result.modified_count > 0:
        print("Conversation updated successfully.")
    else:
        print("No document found for the given user_id and project_id.")

    # generated_code = filter_code(assistant_message)

    return generated_code


# ---------------------------------------------------------image prompt to code-----------------------


def image_to_code(base64_image, user_id, project_id):
    # try:
    messages = image_build_messages(base64_image)
    openai.api_key = key
    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        max_tokens=4096,
        messages=messages,
    )
    # Append the user's message to the conversation
    input_conversation = {"role": "user", "content": base64_image}

    # Call OpenAI API with the entire conversation history

    # Extract the assistant's message from the response
    assistant_message = response["choices"][0]["message"]["content"]

    generated_code = filter_code(assistant_message)
    if generated_code:
        # Append the assistant's message to the conversation
        assistant_conversation = {"role": "assistant", "content": generated_code}
    else:
        assistant_conversation = {"role": "assistant", "content": assistant_message}

    conversation = [input_conversation, assistant_conversation]
    save_conversation_to_db(
        user_id,
        project_id,
        conversation,
        app_idea=None,
        app_feature=None,
        app_look=None,
    )

    # templates_dir = "templates"
    # os.makedirs(templates_dir, exist_ok=True)

    return generated_code


# ------------------------------------------------enhanceprompt-----------------------------------------
def enhanceprompt(enhance_prompt):
    openai.api_key = key  # Set the API key for the openai library
    prompt__edit_input = (
        f"{enhance_prompt} : enhance this prompt for better understanding"
    )

    conversation_input = [{"role": "user", "content": prompt__edit_input}]

    # Call OpenAI API
    response = openai.ChatCompletion.create(model="gpt-4", messages=conversation_input)

    assistant_message = response["choices"][0]["message"]["content"]
    return assistant_message


# Example usage:
# user_message = "Can you add a game to the home page for my visitors to play update this functionality and provide me fully updated code for my website with css and js i need full code"
# prompt(user_message)
