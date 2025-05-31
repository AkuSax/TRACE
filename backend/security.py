import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# --- Configuration ---
# To generate a good secret key, run this in your terminal:
# openssl rand -hex 32
SECRET_KEY = os.environ.get('SECRET_KEY', '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password Hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic model for the token data
class TokenData(BaseModel):
    email: Optional[str] = None

# --- Password Functions ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)

# --- JWT Functions ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Dependency to Get Current User ---
# This function will be more fleshed out once we have a way to query users
# For now, it sets up the dependency structure.
def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Decodes the JWT token to get the current user.
    This function will be used as a dependency to protect endpoints.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    # In a real app, you would fetch the user from the database here
    # to ensure the user still exists and is active.
    # For now, we return the token data.
    return token_data