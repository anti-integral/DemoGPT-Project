# main.py
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from jose import JWTError

# from sqlalchemy.orm import Session
from services.schemas import (
    UserCreate,
    UserResponse,
    Response,
    Token,
    LoginRequest,
    PromptRequest,
    EditPromptRequest,
    EnhancePromptRequest,
    EditRedirectRequest,
    DeploymentRequest,
)
from services.crud import verify_password

# from services.database import SessionLocal, engine, Base
from decouple import config
import openai
from services.deployment_vercel import deploy_html_to_vercel
from services.jwt import create_access_token, decode_token, verify_google_token
from services import mongo_connection, crud
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2AuthorizationCodeBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from prompt_service.prompt_to_code import prompt, editprompt, enhanceprompt
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import uvicorn
import os
import pymongo
from typing import List

app = FastAPI()
templates = Jinja2Templates(directory="templates")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ACCESS_TOKEN_EXPIRE_MINUTES = 120

websites = {}


@app.post("/signup")
async def signup(user_create: UserCreate):
    # Check if passwords match
    if user_create.password != user_create.confirm_password:
        error_detail = {"message": "Passwords do not match"}
        raise HTTPException(status_code=400, detail=error_detail)

    try:
        hashpassword = crud.hash_password(user_create.password)

        # Check if the email already exists in the database
        existing_user = mongo_connection.UserCollection.find_one(
            {"email": user_create.email}
        )

        if existing_user:
            # Email already exists, handle accordingly (raise exception or return response)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Email does not exist, proceed with user registration
        data = {
            "email": user_create.email,
            "password": hashpassword,
        }

        # Insert the data into the MongoDB collection
        result = mongo_connection.UserCollection.insert_one(data)

        # Retrieve the inserted document using the _id returned by insert_one
        inserted_user = mongo_connection.UserCollection.find_one(
            {"_id": result.inserted_id}
        )

        response_data = {
            "code": "200",
            "status": "success",
            "message": "User registered successfully",
            "result": {
                "user_id": str(
                    result.inserted_id
                ),  # Convert ObjectId to string for the response
                "email": inserted_user["email"],
            },
        }

        return JSONResponse(content=response_data)
    except IntegrityError as e:
        error_detail = {"message": "Email is already registered"}
        raise HTTPException(status_code=400, detail=error_detail)


@app.post("/login", response_model=Token)
async def login_for_access_token(login_request: LoginRequest):
    user = mongo_connection.UserCollection.find_one({"email": login_request.email})
    if user is None or not verify_password(
        login_request.password, user.get("password")
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "email": login_request.email},
        expires_delta=access_token_expires,
    )
    login_response_data = {
        "code": "200",
        "status": "success",
        "message": "User login successfully",
        "result": {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": str(
                user.get("_id")
            ),  # Convert ObjectId to string for the response
        },
    }
    return JSONResponse(content=login_response_data)


@app.post("/google-login", response_model=Token)
async def google_login(
    token: str = Depends(
        OAuth2AuthorizationCodeBearer(
            tokenUrl="token",
            authorizationUrl="https://www.googleapis.com/oauth2/v3/userinfo",
        ),
    ),
):
    try:
        user_data = verify_google_token(token)

        if not user_data:
            raise HTTPException(
                status_code=401,
                detail="Invalid Google token",
            )

        existing_user = mongo_connection.Googlelogin.find_one(
            {"email": user_data["email"]}
        )

        if existing_user:
            # Generate an access token for the user
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={
                    "sub": str(existing_user["_id"]),
                    "email": existing_user["email"],
                },
                expires_delta=access_token_expires,
            )
            user_id = str(existing_user["_id"])
        else:
            # User is not registered, handle accordingly (e.g., register the user)
            # You can also save additional user details from Google here
            result = mongo_connection.Googlelogin.insert_one(user_data)
            inserted_user = mongo_connection.Googlelogin.find_one(
                {"_id": result.inserted_id}
            )

            if not inserted_user:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to insert user data",
                )

            # Generate an access token for the newly registered user
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={
                    "sub": str(inserted_user["_id"]),
                    "email": inserted_user["email"],
                },
                expires_delta=access_token_expires,
            )
            user_id = str(inserted_user["_id"])

        # Prepare the response
        login_response_data = {
            "code": "200",
            "status": "success",
            "message": "User login successfully",
            "result": {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": user_id,
            },
        }

        return JSONResponse(content=login_response_data)

    except Exception as e:
        # Log the exception for debugging
        print(f"Error in google_login: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/generate")
async def generate_website(
    request: Request,
    prompts: PromptRequest,
    token: str = Depends(oauth2_scheme),
):
    app_idea = prompts.appIdea
    app_feature = prompts.appFeatures
    app_look = prompts.appLook
    decode = decode_token(token)
    user_id = decode.get("sub")
    project_id = datetime.now().strftime("%Y%m%d%H%M%S")
    generated_content = prompt(app_idea, app_feature, app_look, user_id, project_id)

    generate_response = {
        "code": "200",
        "status": "success",
        "message": "code generated successfully",
        "code": generated_content,
        "result": {"project_id": project_id},
    }

    return JSONResponse(content=generate_response)


# @app.post("/renderoutput", response_class=HTMLResponse)
# async def generate_website(
#     request: Request,
#     token: str = Depends(oauth2_scheme),
# ):
#     decode = decode_token(token)

#     return templates.TemplateResponse("generated_website.html", {"request": request})


@app.post("/edit")
async def edit_generate_website(
    request: Request, data: EditPromptRequest, token: str = Depends(oauth2_scheme)
):
    prompt_input = data.editPrompt
    project_id = data.projectID
    decode = decode_token(token)
    user_id = decode.get("sub")
    # website_id = data.websiteID

    generated_content = editprompt(prompt_input, user_id, project_id)

    generate_edited_response = {
        "code": "200",
        "status": "success",
        "code": generated_content,
        "message": "edit code generated successfully",
        "result": {"project_id": project_id},
    }

    return JSONResponse(content=generate_edited_response)


@app.post("/enhance")
async def enhance_app_idea(
    request: Request, data: EnhancePromptRequest, token: str = Depends(oauth2_scheme)
):
    enhance_prompt_input = data.enhancePrompt
    decode = decode_token(token)

    generated_content = enhanceprompt(enhance_prompt_input)

    enhance_response = {
        "code": "200",
        "status": "success",
        "message": "User enhance successfully",
        "result": {"enhace_data": generated_content},
    }
    return JSONResponse(content=enhance_response)


@app.post("/image-upload")
async def edit_generate_website(
    request: Request, data: EditPromptRequest, token: str = Depends(oauth2_scheme)
):
    image_base64 = data.image
    project_id = data.projectID
    decode = decode_token(token)
    user_id = decode.get("sub")

    generated_content = editprompt(image_base64, user_id, project_id)

    generate_edited_response = {
        "code": "200",
        "status": "success",
        "code": generated_content,
        "message": "edit code generated successfully",
        "result": {"project_id": project_id},
    }

    return JSONResponse(content=generate_edited_response)


@app.post("/redirect-edit")
async def edit_redirect_website(
    request: Request, data: EditRedirectRequest, token: str = Depends(oauth2_scheme)
):
    project_id = data.projectID
    decode = decode_token(token)
    user_id = decode.get("sub")

    # generated_content = editprompt(image_base64, user_id, project_id)
    query = {
        "user_id": user_id,
        "project_id": project_id,
    }
    chat_history_document = mongo_connection.userchathistory.find_one(query)
    conversation = chat_history_document.get("conversation", [])
    for item in conversation:
        if item.get("role") == "assistant":
            # Print or store the content field
            assistant_content = item.get("content")
    # print(assistant_content)
    redirect_edited_response = {
        "code": "200",
        "status": "success",
        "code": assistant_content,
        "message": "edit redirect successfully",
        "result": {"project_id": project_id},
    }

    return JSONResponse(content=redirect_edited_response)


@app.get("/getuserdata", response_class=HTMLResponse)
async def collect_user_details(request: Request, token: str = Depends(oauth2_scheme)):
    decode = decode_token(token)
    user_id = decode.get("sub")
    query = {"user_id": user_id}

    # Find all documents matching the query
    user_objects = mongo_connection.userchathistory.find(query)

    # Check if user_objects is a cursor
    if not isinstance(user_objects, pymongo.cursor.Cursor):
        # Handle the case where the result is not a cursor (e.g., empty result)
        return JSONResponse(
            content={"code": "404", "status": "error", "message": "No data found"}
        )

    # Extract relevant information from each document
    collect_data: List[dict] = []
    for user_object in user_objects:
        collect_data.append(
            {
                "appIdea": user_object.get("app_idea", ""),
                "appFeatures": user_object.get("app_feature", ""),
                "appLook": user_object.get("app_look", ""),
                "projectId": user_object.get("project_id", ""),
            }
        )

    collected_response = {
        "code": "200",
        "status": "success",
        "message": "User enhance successfully",
        "result": {"collect_data": collect_data},
    }

    return JSONResponse(content=collected_response)


@app.post("/deployment")
async def deploy_website(
    request: Request,
    data: DeploymentRequest,
    token: str = Depends(oauth2_scheme),
):
    project_id = data.projectID
    decode = decode_token(token)
    user_id = decode.get("sub")
    find_query = {
        "user_id": user_id,
        "project_id": project_id,
    }
    chat_history_document = mongo_connection.userchathistory.find_one(find_query)
    conversation = chat_history_document.get("conversation", [])
    for item in conversation:
        if item.get("role") == "assistant":
            # Print or store the content field
            frontend_code = item.get("content")
    deployment_name = "sample"
    response = deploy_html_to_vercel(frontend_code, deployment_name)

    query = {
        "user_id": user_id,
        "project_id": project_id,
        "deployment_id": response["deployment_id"],
        "deploy_url": response["deploy_url"],
    }

    # Find all documents matching the query
    user_objects = mongo_connection.Deployments.insert_one(query)

    collected_response = {
        "code": "200",
        "status": "success",
        "message": "deploy successfully",
    }

    return JSONResponse(collected_response)
