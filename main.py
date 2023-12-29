# main.py
from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from sqlalchemy.orm import Session
from schemas import (
    UserCreate,
    UserResponse,
    Response,
    Token,
    LoginRequest,
    PromptRequest,
)
from crud import create_user, get_user, get_user_by_email, verify_password
from database import SessionLocal, engine, Base
from decouple import config
import openai
from deployment_vercel import deploy_html_to_vercel
from jwt import create_access_token
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from prompt_service.prompt_to_code import prompt
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn

# from starlette.templating import Jinja2Templates
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

# Database setup
Base.metadata.create_all(bind=engine)
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/signup/", response_model=Response)
async def signup(user_create: UserCreate, db: Session = Depends(get_db)):
    # Check if passwords match
    if user_create.password != user_create.confirm_password:
        error_detail = {"message": "Passwords do not match"}
        raise HTTPException(status_code=400, detail=error_detail)

    # Create user (adjust the logic accordingly)
    try:
        # Create user (adjust the logic accordingly)
        db_user = create_user(
            db,
            email=user_create.email,
            password=user_create.password,
            # confirm_password=user_create.confirm_password,
        )

        return {
            "code": "200",
            "status": "Ok",
            "message": "User registered successfully",
            "result": UserResponse(
                id=db_user.id, email=db_user.email  # Provide the user ID
            ),
        }
    except IntegrityError as e:
        error_detail = {"message": "Email is already registered"}
        raise HTTPException(status_code=400, detail=error_detail)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/token", response_model=Token)
async def login_for_access_token(login_request: LoginRequest):
    db = SessionLocal()
    user = get_user_by_email(db, email=login_request.email)
    if user is None or not verify_password(login_request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": login_request.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/generate", response_class=HTMLResponse)
async def generate_website(request: Request, prompts: PromptRequest):
    prompt_input = prompts.prompt
    generated_content = prompt(prompt_input)

    templates_dir = "templates"
    os.makedirs(templates_dir, exist_ok=True)

    # Save the generated content to the "generated_website.html" file
    with open(
        os.path.join(templates_dir, "generated_website.html"), "w", encoding="utf-8"
    ) as file:
        file.write(generated_content)
    redirect_path = os.path.join(templates_dir, "generated_website.html")
    return templates.TemplateResponse("generated_website.html", {"request": request})
    # try:
    #     return RedirectResponse(url=f"/{templates_dir}/generated_website.html")
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))

    # generated_url = request.url_for("generated_website")

    # return {"generated_url": generated_url}


@app.post("/edit", response_class=HTMLResponse)
async def edit_website(prompts: str = Form(...)):
    edited_content = prompt(prompts)
    return templates.TemplateResponse(
        "edited_website.html",
    )


# # @app.post("/prompt")
# def prompt():
#     key = config("openai_key")
#     openai.api_key = key  # Set the API key for the openai library

#     prompt_text = "write a code for create a simple landing page for my website."

#     parameters = {
#         "engine": "text-davinci-003",
#         "prompt": prompt_text,
#         "max_tokens": 500,
#         "temperature": 0.7,
#     }

#     response = openai.Completion.create(**parameters)  # Use openai.Completion

#     generated_text = response["choices"][0]["text"].strip()

#     return Response({"generated_text": generated_text})

if (__name__) == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8036, reload=True)
