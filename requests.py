import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.models import Base, Branch, Troops, MedExam, Recruitment, RecruitmentOffice
from app.config import DATABASE_URL

# Создаем асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=False)
# Движок — это основной объект для взаимодействия с базой данных.
# Он отвечает за установление соединений с базой данных и выполнение
# SQL-запросов.

# create_async_engine используется для создания асинхронного движка SQLAlchemy,
# который работает с асинхронными соединениями, используя библиотеки, такого ка
# aiosqlite (для SQLite).

# Создаем фабрику сессий
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
# В SQLAlchemy фабрика сессий — это объект, который помогает создавать
# новые сессии для работы с базой данных. Сессия (session) — это как "контейнер",
# который управляет всеми операциями с базой данных в рамках одного запроса.

# async_sessionmaker — это асинхронная версия обычного sessionmaker.
# Он создаёт асинхронную сессию, которая работает с базой данных в неблокирующем режиме.
# Это важно для асинхронных приложений, таких как FastAPI,
# потому что оно позволяет выполнять несколько операций с базой данных параллельно.

# Функция для получения сессии
async def get_session():
    async with async_session() as session:
        yield session  # возвращаем сессию

# В обычной (синхронной) программе, если вы выполняете запрос к базе данных или
# ждёте ответа от веб-сервера, программа "замерзает" и ничего не может делать,
# пока не получит ответ.

# В асинхронной программе, когда начинается долгий процесс (например, запрос к серверу),
# программа не останавливается. Она может выполнять другие операции (например, другой запрос),
# пока не получит результат первого. Это экономит время, так как можно
# работать сразу с несколькими задачами.

# Функция для добавления записи
async def add_record(record: Base):
    async for session in get_session():  # Открываем сессию через get_session
        session.add(record)  # Добавляем в сессию
        await session.commit()  # Коммитим изменения

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

# Запуск асинхронной функции
if __name__ == "__main__":
    #asyncio — это библиотека в Python для работы с асинхронным кодом.
    # Она позволяет выполнять несколько задач одновременно без блокировки программы.
    asyncio.run(init_db())
    asyncio.run(add_record(Branch(name="ВДВ")))
    asyncio.run(add_record(Branch(name="Сухопутные войска")))
    asyncio.run(add_record(Branch(name="РВСН")))
    asyncio.run(add_record(Branch(name="Военно-морской флот")))

    asyncio.run(add_record(Troops(name="Парашютно-десантные", branch_id=1)))
    asyncio.run(add_record(Troops(name="Десантно-штурмовые", branch_id=1)))
    asyncio.run(add_record(Troops(name="Танковые", branch_id=2)))
    asyncio.run(add_record(Troops(name="Мотострелковые", branch_id=2)))
    asyncio.run(add_record(Troops(name="ПВО", branch_id=2)))
    asyncio.run(add_record(Troops(name="Ракетный батальон", branch_id=3)))
    asyncio.run(add_record(Troops(name="Подводные", branch_id=4)))

    asyncio.run(add_record(RecruitmentOffice(address="г. Ульяновск, ул. Винновская роща, д.1",
                                             chief_name="Соколов Владимир Николаевич")))