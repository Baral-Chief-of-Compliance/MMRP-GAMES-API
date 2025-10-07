import os
from datetime import datetime

import pytz
from sqlmodel import Field, SQLModel, create_engine, Session
from dotenv import load_dotenv


load_dotenv()

DB_PATH = os.getenv('DB_PATH')

connect_args = {"check_same_thread": False}
engine = create_engine(DB_PATH, connect_args=connect_args)


class UserTetris(SQLModel, table=True):
    """Модель пользователя для учета статистики в тетрис"""
    id: str | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    email: str = Field(unique=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(pytz.timezone('Europe/Moscow')))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(pytz.timezone('Europe/Moscow')))
    score: int


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session