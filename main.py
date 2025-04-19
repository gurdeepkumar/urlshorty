from fastapi import FastAPI, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse

from sqlmodel import Session, select
from models import URL
from database import get_session, init_db

from pydantic import BaseModel
from utils import normalize_url


# Type checking
class CreateRequest(BaseModel):
    original_url: str
    short_code: str


class DeleteRequest(BaseModel):
    short_code: str


class UpdateRequest(BaseModel):
    short_code: str
    updated_url: str


tags_metadata = [
    {
        "name": "Features",
    },
]

# Fast API instance
app = FastAPI(openapi_tags=tags_metadata)
app.title = "URL Shorty"

# Check if model/table exists in DB
init_db()


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
@app.get("/list/", tags=["Features"])
def List_url(session: Session = Depends(get_session)):
    rows = session.exec(select(URL)).all()
    rows_json = jsonable_encoder(rows)
    return rows_json


# Create a short url
@app.post("/shorten/", tags=["Features"])
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

    return {"short_url": f"https://urlshorty.gurdeepkumar.com/{url.short_code}"}


# Get the orignal URL
@app.get("/{short_code}", tags=["Features"])
def redirect_to_url(short_code: str, session: Session = Depends(get_session)):
    url = session.exec(select(URL).where(URL.short_code == short_code)).first()
    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(url.original_url, status_code=307)


# Delete a URL with short code
@app.delete("/", tags=["Features"])
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
@app.patch("/", tags=["Features"])
def update_url(request: UpdateRequest, session: Session = Depends(get_session)):
    short_code = request.short_code
    updated_url = request.updated_url
    statement = select(URL).where(URL.short_code == short_code)
    url = session.exec(statement).first()

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    url.original_url = updated_url
    session.add(url)
    session.commit()
    session.refresh(url)

    return {"message": "URL updated successfully", "data": url}
