from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer

from sqlmodel import Session, select
from models import URL, User
from database import get_session, init_db

from utils import normalize_url

from schemas import (
    UserCreate,
    CreateRequest,
    DeleteRequest,
    UpdateRequest,
    LoginRequest,
    LogoutRequest,
    UserResponse,
    DeleteUserRequest,
    RefreshRequest,
)

import auth

# FastAPI Tags
tags_metadata = [
    {
        "name": "Authentication",
    },
    {
        "name": "Features",
    },
]

# FastAPI instance
app = FastAPI(openapi_tags=tags_metadata)
app.title = "URL Shorty"

# For serving templates
templates = Jinja2Templates(directory="templates")

# Check if model/table exists in DB
init_db()

# Dependency for user auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usr/login")


# Index Page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# *** User authentication and authorization ***
# Register User
@app.post("/usr/register", tags=["Authentication"])
def register(user: UserCreate, session: Session = Depends(get_session)):
    # Username and password len and characters check
    if not user.username.isalpha():
        raise HTTPException(status_code=400, detail="Username must be only alphabets")
    elif len(user.username) <= 5:
        raise HTTPException(
            status_code=400, detail="Username must be 6 or more characters"
        )
    elif len(user.password) <= 7:
        raise HTTPException(
            status_code=400, detail="Password must be minimum 8 characters"
        )

    existing = session.exec(select(User).where(User.username == user.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pw = auth.get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_pw)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username}


# Login user and return access token and refresh token
@app.post("/usr/login", tags=["Authentication"])
def login(data: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == data.username)).first()
    if not user or not auth.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    refresh_token = auth.create_refresh_token({"sub": user.username})
    access_token = auth.create_access_token({"sub": user.username})

    auth.save_refresh_token(user.username, refresh_token, session)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# Takes access token and return user for it
@app.get("/usr/me", tags=["Authentication"])
def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> UserResponse:
    username = auth.get_username_from_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(username=user.username, id=user.id)


# Takes refresh token and return new access token
@app.post("/usr/refresh", tags=["Authentication"])
def refresh_token_endpoint(data: RefreshRequest):
    try:
        tokens = auth.refresh_token(data.refresh_token)
        return tokens
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


# Delete refresh token from db
@app.post("/usr/logout", tags=["Authentication"])
def logout(data: LogoutRequest, session: Session = Depends(get_session)):
    auth.delete_refresh_token(data.refresh_token, session)
    return {"message": "Logged out successfully"}


# Delete user and related urls
@app.delete("/usr/delete", tags=["Authentication"])
def delete_user(data: DeleteUserRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == data.username)).first()

    if not user:
        raise HTTPException(status_code=401, detail="User doesn't exist.")

    if not auth.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    session.delete(user)
    session.commit()
    return {"message": f"User '{data.username}' and related data deleted successfully."}


# Server and DB check
@app.get("/health/", tags=["Features"])
def server_check(
    session: Session = Depends(get_session),
):
    try:
        session.exec(select(1))
        return {
            "status": "Server running and Database connection successful",
        }
    except:
        raise HTTPException(status_code=500, detail=f"Database error.")


# *** UrlShorty Features ***
# List all urls
@app.get("/url/list/", tags=["Features"])
def List_url(
    user: UserResponse = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    rows = session.exec(select(URL).where(URL.user_id == user.id)).all()
    rows_json = jsonable_encoder(rows)
    return rows_json


# Create a short url
@app.post("/url/shorten/", tags=["Features"])
def shorten_url(
    request: CreateRequest,
    session: Session = Depends(get_session),
    user: UserResponse = Depends(get_current_user),
):
    original_url = normalize_url(request.original_url)
    short_code = request.short_code

    if not short_code.isalpha():
        raise HTTPException(status_code=403, detail="Only use alphabtes for short code")

    statement = (
        select(URL).where(URL.user_id == user.id).where(URL.short_code == short_code)
    )

    if session.exec(statement).first():
        raise HTTPException(
            status_code=403, detail="Short code is already used by this user."
        )

    url = URL(original_url=original_url, short_code=short_code, user_id=user.id)
    session.add(url)
    session.commit()
    session.refresh(url)

    return url.__dict__
    # return {"short_url": f"https://urlshorty.gurdeepkumar.com/url/{url.short_code}"}


# Get the orignal URL
@app.get("/url/{short_code}", tags=["Features"])
def redirect_to_url(
    short_code: str,
    user: UserResponse = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    url = session.exec(
        select(URL).where(URL.user_id == user.id).where(URL.short_code == short_code)
    ).first()
    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return url.__dict__
    # return RedirectResponse(url.original_url, status_code=307)


# Delete a URL with short code
@app.delete("/url/", tags=["Features"])
def delete_url(
    request: DeleteRequest,
    user: UserResponse = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    short_code = request.short_code
    statement = (
        select(URL).where(URL.user_id == user.id).where(URL.short_code == short_code)
    )
    url = session.exec(statement).first()

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    session.delete(url)
    session.commit()
    return {"message": "URL deleted successfully"}


# Update a URL with short code
@app.patch("/url/", tags=["Features"])
def update_url(
    request: UpdateRequest,
    user: UserResponse = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    short_code = request.short_code
    updated_url = normalize_url(request.updated_url)
    statement = (
        select(URL).where(URL.user_id == user.id).where(URL.short_code == short_code)
    )
    url = session.exec(statement).first()

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    url.original_url = updated_url
    session.add(url)
    session.commit()
    session.refresh(url)

    return {"message": "URL updated successfully", "data": url}
