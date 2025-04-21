from sqlmodel import SQLModel, create_engine, Session, inspect
from dotenv import load_dotenv
import os

load_dotenv()

hostname = os.getenv("HOST")
database = os.getenv("DB")
username = os.getenv("USR")
password = os.getenv("PWD")
port_id = os.getenv("PORT")

DATABASE_URL = (
    f"postgresql+psycopg2://{username}:{password}@{hostname}:{port_id}/{database}"
)

engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


def init_db():
    inspector = inspect(engine)
    if (
        not inspector.has_table("url")
        or not inspector.has_table("user")
        or not inspector.has_table("refreshtoken")
    ):
        SQLModel.metadata.create_all(engine)
