# main.py
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from services.schemas import (
    UserCreate,
    UserResponse,
    Response,
    Token,
    LoginRequest,
    PromptRequest,
    EditPromptRequest,
)
from services.crud import verify_password

# from services.database import SessionLocal, engine, Base
from decouple import config
import openai
from deployment_vercel import deploy_html_to_vercel
from services.jwt import create_access_token, decode_token
from services import mongo_connection, crud
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from prompt_service.prompt_to_code import prompt, editprompt
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import os

UserCreate
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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/generate", response_class=HTMLResponse)
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

    generated_content = prompt(app_idea, app_feature, app_look)

    templates_dir = "templates"
    os.makedirs(templates_dir, exist_ok=True)

    # Save the generated content to the "generated_website.html" file
    with open(
        os.path.join(templates_dir, "generated_website.html"), "w", encoding="utf-8"
    ) as file:
        file.write(generated_content)

    return templates.TemplateResponse(
        "generated_website.html",
        {"request": request, "content": generated_content},
    )


@app.post("/edit", response_class=HTMLResponse)
async def edit_generate_website(
    request: Request, data: EditPromptRequest, token: str = Depends(oauth2_scheme)
):
    prompt_input = data.editprompt
    decode = decode_token(token)
    user_id = decode.get("sub")
    # website_id = data.websiteID

    generated_content = editprompt(prompt_input)

    templates_dir = "templates"
    os.makedirs(templates_dir, exist_ok=True)

    # Save the generated content to the "generated_website.html" file
    with open(
        os.path.join(templates_dir, "generated_website.html"), "w", encoding="utf-8"
    ) as file:
        file.write(generated_content)

    # website_id = len(websites) + 1
    # websites[website_id] = {"content": generated_content}

    return templates.TemplateResponse(
        "generated_website.html",
        {
            "request": request,
            "content": generated_content,
        },
    )


if (__name__) == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8036, reload=True)
