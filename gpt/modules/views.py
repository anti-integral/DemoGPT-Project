from django.shortcuts import render
from decouple import config
import openai
from gpt.services.deployment_vercel import deploy_html_to_vercel
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


# Create your views here.
@api_view(http_method_names=["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def prompt():
    key = config("openai_key")
    openai.api_key = key  # Set the API key for the openai library

    prompt_text = "write a code for create a simple landing page for my website."

    parameters = {
        "engine": "text-davinci-003",
        "prompt": prompt_text,
        "max_tokens": 100,
        "temperature": 0.7,
    }

    response = openai.Completion.create(**parameters)  # Use openai.Completion

    generated_text = response["choices"][0]["text"].strip()

    deployed_url = deploy_html_to_vercel(generated_text)

    return Response({"generated_text": generated_text, "deployed_url": deployed_url})
