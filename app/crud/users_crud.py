# app/crud/users_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User
from app.schemas import UserCreateSchema
from sqlalchemy.exc import NoResultFound
from passlib.context import CryptContext

# Инициализируем Password Context для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Хеширование пароля
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Проверка пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Получение пользователя по имени
async def get_user_by_username(username: str, db: AsyncSession):
    query = select(User).filter(User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    return user  # Возвращаем None, если пользователь не найден


# Создание нового пользователя
async def create_user(user: UserCreateSchema, db: AsyncSession):
    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
