import openai
import json
import os


# def save_conversation_to_file(conversation, filename="conversation_history.json"):
#     with open(filename, "w") as file:
#         json.dump(conversation, file)


# def load_conversation_from_file(filename="conversation_history.json"):
#     try:
#         with open(filename, "r") as file:
#             conversation = json.load(file)
#     except FileNotFoundError:
#         conversation = []
#     return conversation


# def prompt(user_message, conversation_file="conversation_history.json"):
#     key = config("openai_key")
#     openai.api_key = key  # Set the API key for the openai library

#     # Load the existing conversation history
#     conversation = load_conversation_from_file(conversation_file)

#     # Append the user's message to the conversation
#     conversation.append({"role": "user", "content": user_message})

#     # Call OpenAI API with the entire conversation history
#     response = openai.ChatCompletion.create(model="gpt-4", messages=conversation)

#     # Extract the assistant's message from the response
#     assistant_message = response["choices"][0]["message"]["content"]
#     print(assistant_message)

#     # Append the assistant's message to the conversation
#     conversation.append({"role": "assistant", "content": assistant_message})

#     # Save the updated conversation history to the file
#     save_conversation_to_file(conversation, conversation_file)
#     templates_dir = "templates"
#     os.makedirs(templates_dir, exist_ok=True)

#     with open(
#         os.path.join(templates_dir, "generated_website.html"), "w", encoding="utf-8"
#     ) as file:
#         file.write(assistant_message)
#     return assistant_message


# Example usage:
# user_message = "Can you add a game to the home page for my visitors to play update this functionality and provide me fully updated code for my website with css and js i need full code"
# prompt(user_message)
from fastapi.responses import StreamingResponse
from decouple import config

key = config("openai_key")

SYSTEM_PROMPT = """
You are an expert Tailwind developer
You take screenshots of a reference web page design from the user, and then build single page apps 
using Tailwind, HTML and JS.
You might also be given a screenshot of a web page that you have already built, and asked to
update it to look more like the reference image.

- Make sure the app is also mobile responsive and looks good on smaller screens.
- Make sure the app looks exactly like the screenshot.
- Pay close attention to background color, text color, font size, font family, 
padding, margin, border, etc. Match the colors and sizes exactly.
- Use the exact text from the screenshot.
- Do not add comments in the code such as "<!-- Add other navigation links as needed -->" and "<!-- ... other news items ... -->" in place of writing the full code. WRITE THE FULL CODE.
- Repeat elements as needed to match the screenshot. For example, if there are 15 items, the code should have 15 items. DO NOT LEAVE comments like "<!-- Repeat for each news item -->" or bad things will happen.
- For images, use placeholder images from https://placehold.co and include a detailed description of the image in the alt text so that an image generation AI can generate the image later.

In terms of libraries,

- Use this script to include Tailwind: <script src="https://cdn.tailwindcss.com"></script>
- You can use Google Fonts
- Font Awesome for icons: <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css"></link>

Return only the full code in <html></html> tags.
"""

USER_PROMPT = "Generate code for a web page that looks exactly like this."

import base64
import json


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def build_messages():
    image_path = "/home/sanjeev/Desktop/projects/python projects/GPT/demogpt_backend/demogpt-backend/Screenshot from 2023-12-12 12-13-10.png"
    base64_image = encode_image(image_path)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "high",
                    },
                },
                {"type": "text", "text": USER_PROMPT},
            ],
        },
    ]


def image_to_code(base64_image):
    try:
        messages = build_messages()
        openai.api_key = key

        response_generator = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            temperature=0,
            stream=True,
            max_tokens=4096,
            messages=messages,
        )
        # print(response_generator.json())
        for response in response_generator:
            print(response.choices[0])

            # Extract the generated HTML from the first message
            generated_html = response["choices"][0]["message"]["content"]
            print(generated_html)
        # print(response)
        # generated_html = response["choices"][0]["text"]
        # print(generated_html)
        return generated_html
    except Exception as error:
        print(error)


# Your base64-encoded string

base64_image = "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"
image_to_code(base64_image)
