import requests
from decouple import config

vercel_token = config("vercel_token")
vercel_project_id = config("vercel_project_id")


def deploy_html_to_vercel(frontend_code):
    vercel_deploy_endpoint = (
        f"https://api.vercel.com/v12/now/deployments?projectId={vercel_project_id}"
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {vercel_token}",
    }

    deployment_payload = {
        "name": "demo-gpt-project",
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
