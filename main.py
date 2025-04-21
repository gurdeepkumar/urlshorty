from fastapi import FastAPI, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse
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
    UserResponse,
    DeleteUserRequest,
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

# Check if model/table exists in DB
init_db()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usr/login")


# *** UrlShorty Features ***
# Server and DB check
@app.get("/", tags=["Features"])
def server_check(session: Session = Depends(get_session)):
    try:
        session.exec(select(URL))
        return {"status": "Server running and Database connection successful"}
    except:
        raise HTTPException(
            status_code=500, detail=f"Server running. But, Database connection failed"
        )


# List all urls
@app.get("/url/list/", tags=["Features"])
def List_url(session: Session = Depends(get_session)):
    rows = session.exec(select(URL)).all()
    rows_json = jsonable_encoder(rows)
    return rows_json


# Create a short url
@app.post("/url/shorten/", tags=["Features"])
def shorten_url(request: CreateRequest, session: Session = Depends(get_session)):
    original_url = normalize_url(request.original_url)
    short_code = request.short_code

    if not short_code.isalpha():
        raise HTTPException(status_code=403, detail="Only use alphabtes for short code")

    statement = select(URL).where(URL.short_code == short_code)

    if session.exec(statement).first():
        raise HTTPException(status_code=403, detail="Short code is already used")

    url = URL(original_url=original_url, short_code=short_code)
    session.add(url)
    session.commit()
    session.refresh(url)

    return {"short_url": f"https://urlshorty.gurdeepkumar.com/url/{url.short_code}"}


# Get the orignal URL
@app.get("/url/{short_code}", tags=["Features"])
def redirect_to_url(short_code: str, session: Session = Depends(get_session)):
    url = session.exec(select(URL).where(URL.short_code == short_code)).first()
    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(url.original_url, status_code=307)


# Delete a URL with short code
@app.delete("/url/", tags=["Features"])
def delete_url(request: DeleteRequest, session: Session = Depends(get_session)):
    short_code = request.short_code
    statement = select(URL).where(URL.short_code == short_code)
    url = session.exec(statement).first()

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    session.delete(url)
    session.commit()
    return {"message": "URL deleted successfully"}


# Update a URL with short code
@app.patch("/url/", tags=["Features"])
def update_url(request: UpdateRequest, session: Session = Depends(get_session)):
    short_code = request.short_code
    updated_url = normalize_url(request.updated_url)
    statement = select(URL).where(URL.short_code == short_code)
    url = session.exec(statement).first()

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    url.original_url = updated_url
    session.add(url)
    session.commit()
    session.refresh(url)

    return {"message": "URL updated successfully", "data": url}


# *** User authentication and authorization ***
# Register User
@app.post("/usr/register", tags=["Authentication"])
def register(user: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.username == user.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pw = auth.get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_pw)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username}


# Login user and return access token
@app.post("/usr/login", tags=["Authentication"])
def login(data: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == data.username)).first()
    if not user or not auth.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = auth.create_access_token({"sub": user.username})
    refresh_token = auth.create_refresh_token({"sub": user.username})

    # Optional: Save refresh_token in DB for tracking
    auth.save_refresh_token(user.username, refresh_token, session)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# Return currently logged user
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

    return UserResponse(username=user.username)


@app.post("/usr/refresh", tags=["Authentication"])
def refresh_token_endpoint(refresh_token: str):
    try:
        tokens = auth.refresh_token(refresh_token)
        return tokens
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/usr/logout", tags=["Authentication"])
def logout(refresh_token: str, session: Session = Depends(get_session)):
    # Delete refresh token from DB
    auth.delete_refresh_token(refresh_token, session)
    return {"message": "Logged out successfully"}


@app.delete("/usr/delete", tags=["Authentication"])
def delete_user(data: DeleteUserRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == data.username)).first()

    if not user or not auth.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    session.delete(user)
    session.commit()
    return {"message": f"User '{data.username}' and related data deleted successfully."}
