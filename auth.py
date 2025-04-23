from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

from models import RefreshToken
from sqlmodel import Session, select

from typing import Dict

from dotenv import load_dotenv
import os

load_dotenv()

ACCESS_TOKEN_SECRET_KEY = os.getenv("ACCESS_TOKEN_SECRET_KEY")
REFRESH_TOKEN_SECRET_KEY = os.getenv("REFRESH_TOKEN_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Takes access token and return user
def get_username_from_token(token: str):
    try:
        payload = jwt.decode(token, ACCESS_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


# Return hased password
def get_password_hash(password):
    return pwd_context.hash(password)


# Return bool after verifing the str password with hased password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Receive user and create/return access token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, ACCESS_TOKEN_SECRET_KEY, algorithm=ALGORITHM)


# Receive user and create/return refresh token
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=int(REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, REFRESH_TOKEN_SECRET_KEY, algorithm=ALGORITHM)


# Save refresh token
def save_refresh_token(username: str, token: str, session: Session):
    rt = RefreshToken(username=username, token=token)
    session.add(rt)
    session.commit()


# Delete refresh token to logout user from backend
def delete_refresh_token(token: str, session: Session):
    rt = session.exec(select(RefreshToken).where(RefreshToken.token == token)).first()
    if rt:
        session.delete(rt)
        session.commit()


# Return bool for refresh token validation
def is_refresh_token_valid(token: str, session: Session) -> bool:
    return (
        session.exec(select(RefreshToken).where(RefreshToken.token == token)).first()
        is not None
    )


# Generate a new access token using a valid refresh token.
def refresh_token(refresh_token: str) -> Dict[str, str]:
    try:
        payload = jwt.decode(
            refresh_token, REFRESH_TOKEN_SECRET_KEY, algorithms=[ALGORITHM]
        )
        username = payload.get("sub")

        if not username:
            raise ValueError("Username not found in the token payload")

        new_access_token = create_access_token({"sub": username})
        return {"access_token": new_access_token}

    except jwt.ExpiredSignatureError:
        raise ValueError("Refresh token has expired")
    except jwt.JWTError as e:
        raise ValueError(f"Invalid refresh token: {str(e)}")
