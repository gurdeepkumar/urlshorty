from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    username: str


class DeleteUserRequest(BaseModel):
    username: str
    password: str


class CreateRequest(BaseModel):
    original_url: str
    short_code: str


class DeleteRequest(BaseModel):
    short_code: str


class UpdateRequest(BaseModel):
    short_code: str
    updated_url: str
