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
