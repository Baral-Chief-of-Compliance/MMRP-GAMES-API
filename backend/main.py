from typing import Annotated
from uuid import uuid4
from datetime import datetime, date
from contextlib import asynccontextmanager
import random

from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select, func
import pytz


from db import create_db_and_tables, get_session, UserTetris
from email_validation import is_valid_email_strict
from models import Score


SessionDep = Annotated[Session, Depends(get_session)]


app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post('/tetris/users/')
def create_user(user: UserTetris, session: SessionDep) -> UserTetris:
    """Создание пользователя в системе"""
    if is_valid_email_strict(user.email):
        user_in_db = session.exec(select(UserTetris).where(UserTetris.email == user.email)).first()

        if not user_in_db:
            user_in_db = session.exec(select(UserTetris).where(UserTetris.name == user.name)).first()

            if not user_in_db:
                user.id = str(uuid4())
                session.add(user)
                session.commit()
                session.refresh(user)
                return user
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с таким именем уже есть"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже есть"
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email невалидный"
        )
    
@app.put('/tetris/users/{user_id}/update-score')
def update_score(user_id: str, score: Score,  session: SessionDep):
    """Обновить рекорд пользователя"""
    user_in_db = session.exec(select(UserTetris).where(UserTetris.id == user_id)).first()
    if user_in_db:
        user_in_db.updated_at = datetime.now(pytz.timezone('Europe/Moscow'))
        user_in_db.score = score.score
        session.commit()
        session.refresh(user_in_db)
        return user_in_db
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким id не найден"
        )
    
@app.get('/tetris/leaderboard/')
def get_leaderboard(session: SessionDep) -> UserTetris:
    # Таблица лидеров за все время
    users = session.exec(select(UserTetris).order_by(UserTetris.score))
    result : list = []
    if len(users) > 0 : result = [{'name': user.name, 'score': user.score} for user in users]
    return {
        'users': result
    }

@app.get('/tetris/leaderboard/today')
def get_leaderboard(session: SessionDep) -> UserTetris:
    # Таблица лидеров за сегодня
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    users = session.exec(select(UserTetris).where(
        UserTetris.updated_at >= start_of_day,
        UserTetris.updated_at <= end_of_day
    ).order_by(UserTetris.score))

    result : list = []
    if len(users) > 0 : result = [{'name': user.name, 'score': user.score} for user in users]
    return {
        'users': result
    }


@app.get('/tetris/get_random_username')
def get_random_username(session: SessionDep):
    random_number = random.randint(100000, 999999)
    return {
        'username': f'users{random_number}'
    }