from datetime import timedelta
from typing import Optional

from fastapi import APIRouter
from fastapi_jwt import JwtAccessBearer
from pydantic import EmailStr

from app.schemas import UserSchema, UserCreateSchema, LoginResponseSchema, UserInformationSchema, UserUpdateSchema
from app.crud.users_crud import create_user, verify_password
from app.database import get_session

from fastapi import Depends, HTTPException, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.users_crud import get_user_by_username
from app.models import User
import app.crud.users_crud as user_crud

router = APIRouter(prefix="/auth", tags=["Аутентификация"])

access_security = JwtAccessBearer(
    secret_key="uOXJadCVO4hfbAt",
    access_expires_delta=timedelta(hours=1)
)

async def get_token(user: User):
    return access_security.create_access_token(subject={"username": user.username})


@router.post("/register", response_model=UserSchema)
async def register(user_data: UserCreateSchema, db: AsyncSession = Depends(get_session)):
    existing_user = await get_user_by_username(user_data.username, db)
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    return await create_user(user_data, db)


@router.post("/login", response_model=LoginResponseSchema)
async def login(user: UserCreateSchema, db: AsyncSession = Depends(get_session)):
    print(f"[DEBUG] Полученные данные от клиента: {user}")

    # Получаем пользователя из базы данных
    db_user = await get_user_by_username(user.username, db)
    if not db_user:
        print("[ERROR] Пользователь не найден")
        raise HTTPException(status_code=401, detail="Неверные учетные данные")

    # Проверка пароля
    if not verify_password(user.password, db_user.password):
        print("[ERROR] Неверный пароль")
        raise HTTPException(status_code=401, detail="Неверные учетные данные")

    # Генерация токена
    token = await get_token(db_user)
    print(f"[DEBUG] Создан токен: {token}")

    # Формируем ответ
    response = {
        "id": db_user.id,
        "username": db_user.username,
        "access_token": token
    }
    print(f"[DEBUG] Ответ клиенту: {response}")

    return response


async def current_user_update(
        credentials: JwtAuthorizationCredentials = Security(access_security),
        db: AsyncSession = Depends(get_session),
) -> User:
    # Извлекаем username из токена (subject)
    subject = credentials.subject

    if isinstance(subject, dict) and "username" in subject:
        username = subject["username"]
    elif isinstance(subject, str):
        username = subject
    else:
        raise HTTPException(status_code=401, detail="Некорректный токен")

    # Получаем пользователя по username
    user = await get_user_by_username(username, db)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    return user


@router.patch("/profile/update", response_model=UserUpdateSchema, summary="Обновить данные пользователя")
async def update_user_info(
        username: Optional[str],
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        father_name: Optional[str] = None,
        email: Optional[EmailStr] = None,
        password: Optional[str] = None,
        page_size: Optional[int] = None,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(current_user_update)
):
    # Проверяем, что текущий пользователь существует
    user = await get_user_by_username(username, db)  # Предположим, что у вас есть такая функция
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Обновляем поля, если они были переданы
    if username and username != current_user.username:
        raise HTTPException(status_code=403, detail="Невозможно изменить имя пользователя")

    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if father_name:
        user.father_name = father_name
    if email:
        user.email = email
    if password:
        user.password = user_crud.hash_password(password)  # Хешируем новый пароль
    if page_size:
        user.page_size = page_size

    # Сохраняем изменения в базе данных
    await db.commit()
    await db.refresh(user)

    return user

@router.get("/profile", response_model=UserInformationSchema, summary="Получить информацию о текущем пользователе")
async def get_user_info(
    current_user: User = Depends(current_user_update)  # Проверка авторизации через токен
):
    # Возвращаем информацию о текущем пользователе
    return UserInformationSchema(
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        father_name=current_user.father_name,
        email=current_user.email,
        page_size=current_user.page_size
    )