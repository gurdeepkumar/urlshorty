from sqlmodel import SQLModel, Field
from typing import Optional
import datetime


class URL(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    original_url: str
    short_code: str = Field(index=True, unique=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
