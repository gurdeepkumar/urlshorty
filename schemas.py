from pydantic import BaseModel


# User Schemas
class UserCreate(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LogoutRequest(BaseModel):
    refresh_token: str


class RefreshRequest(BaseModel):
    refresh_token: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    username: str


class DeleteUserRequest(BaseModel):
    username: str
    password: str


# Url Shorty Schemas
class CreateRequest(BaseModel):
    original_url: str
    short_code: str


class DeleteRequest(BaseModel):
    short_code: str


class UpdateRequest(BaseModel):
    short_code: str
    updated_url: str
