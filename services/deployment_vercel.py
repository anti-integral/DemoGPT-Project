import requests
from decouple import config
import json

vercel_token = config("vercel_token")
vercel_project_id = config("vercel_project_id")


def deploy_html_to_vercel(frontend_code):
    vercel_deploy_endpoint = "https://api.vercel.com/v12/now/deployments"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {vercel_token}",
    }

    deployment_payload = {
        "name": "demo-gpt-project",
        "projectId": vercel_project_id,  # Include projectId in the payload
        "files": [
            {
                "file": "index.html",
                "data": frontend_code,
            },
        ],
    }

    response = requests.post(
        vercel_deploy_endpoint, headers=headers, json=deployment_payload
    )

    if response.status_code == 200:
        deployed_url = response.json().get("url")
        return deployed_url
    else:
        return {"error": response.text}


html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Deployed HTML</title>
</head>
<body>
    <h1>Hello, Vercel!</h1>
</body>
</html>
"""
# print(deploy_html_to_vercel(frontend_code=html_content))


def create_new_project():
    api_endpoint = "https://api.vercel.com/v6/projects"
    config = {
        "method": "post",
        "url": api_endpoint,
        "headers": {
            "Authorization": "Bearer " + vercel_token,
            "Content-Type": "application/json",
        },
        "data": json.dumps(
            {
                "name": "test1",
            }
        ),
    }

    try:
        response = requests.request(**config)
        response.raise_for_status()
        data = response.json()
        print(f"New project created with ID: {data['id']}")
    except requests.exceptions.RequestException as error:
        print(error)


# create_new_project()
