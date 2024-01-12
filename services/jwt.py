# jwt.py

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, Depends, status
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# from google.auth.transport import requests
# from google.oauth2 import id_token
from decouple import config
import secrets
import string
from requests.exceptions import HTTPError as RequestsHTTPError
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.auth.exceptions import TransportError
import google.auth.transport.requests
import requests

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(characters) for _ in range(length))
    return password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Access token not valid",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception


def verify_google_token(token):
    userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Create a request object using the GoogleAuthRequest class
        request = GoogleAuthRequest()

        # Make the request using the session.request method
        with requests.session() as session:
            response = session.request("GET", userinfo_url, headers=headers)
            response.raise_for_status()
            user_info = response.json()

        random_password = generate_random_password()

        user_data = {
            "email": user_info.get("email", ""),
            "google_user_id": user_info.get("sub", ""),
            "name": user_info.get("name", ""),
            "password": random_password,
        }

        return user_data

    except TransportError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error connecting to Google API: {str(e)}",
        )

    except Exception as e:
        print(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during token verification",
        )
