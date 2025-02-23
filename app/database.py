from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import DATABASE_URL, ECHO_LOG
from app.models import Base

# Создаем асинхронный движок для работы с базой данных
engine = create_async_engine(DATABASE_URL, echo=ECHO_LOG)

# Создаем сессию
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Функция для получения сессии с включением PRAGMA foreign_keys
async def get_session():
    async with async_session() as session:
        yield session

# Функция для инициализации базы данных (создание всех таблиц)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

from fastapi import Depends, HTTPException, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.users_crud import get_user_by_username
from app.models import User
from app.routes.auth_routes import access_security


async def get_current_user(
        credentials: JwtAuthorizationCredentials = Security(access_security),
        db: AsyncSession = Depends(get_session),
) -> User:

    subject = credentials.subject

    # Если subject — это словарь, достаем username
    if isinstance(subject, dict) and "username" in subject:
        username = subject["username"]
    elif isinstance(subject, str):
        username = subject
    else:
        raise HTTPException(status_code=401, detail="Некорректный токен")

    user = await get_user_by_username(username, db)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    return user



