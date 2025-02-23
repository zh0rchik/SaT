from fastapi import APIRouter, HTTPException, Depends
from fastapi_jwt import JwtAccessBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.schemas import UserSchema, UserCreateSchema
from app.crud.users_crud import get_user_by_username, create_user, verify_password
from app.database import get_session

router = APIRouter(prefix="/auth", tags=["Аутентификация"])

access_security = JwtAccessBearer(secret_key="uOXJadCVO4hfbAt")

async def get_token(user: User):
    return access_security.create_access_token(subject={"username": user.username})


@router.post("/register", response_model=UserSchema)
async def register(user_data: UserCreateSchema, db: AsyncSession = Depends(get_session)):
    existing_user = await get_user_by_username(user_data.username, db)
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    return await create_user(user_data, db)

@router.post("/login")
async def login(user: UserCreateSchema, db: AsyncSession = Depends(get_session)):
    db_user = await get_user_by_username(user.username, db)
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")

    token = await get_token(db_user)

    return {
        "id": db_user.id,
        "username": db_user.username,
        "access_token": token
    }
