# schemas.py
from typing import List, Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str
    confirm_password: str


class UserLogin(UserBase):
    password: str


class UserResponse(BaseModel):
    id: Optional[int]
    email: str


class Response(BaseModel):
    code: str
    status: str
    message: str
    result: Optional[UserResponse]


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: str
    password: str


class GoogleLoginRequest(BaseModel):
    google_token: str


class PromptRequest(BaseModel):
    appIdea: str
    appFeatures: str
    appLook: str


class EditPromptRequest(BaseModel):
    editPrompt: str
    projectID: str
    # websiteID: int


class EnhancePromptRequest(BaseModel):
    enhancePrompt: str


class EditPromptRequest(BaseModel):
    editPrompt: str
    projectID: str
    # websiteID: int


class EditRedirectRequest(BaseModel):
    projectID: str
    # websiteID: int


class CodeRequest(BaseModel):
    code: str
