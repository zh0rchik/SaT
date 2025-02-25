from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Recruitment, Troops, RecruitmentOffice
from app.schemas import RecruitmentCreateSchema
from fastapi import HTTPException, UploadFile
from sqlalchemy.future import select
from pathlib import Path
from datetime import date

# Папка для загрузки фото
UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # Создаем папку, если она не существует

async def create_recruitment(db: AsyncSession, recruitment: RecruitmentCreateSchema) -> Recruitment:
    # Проверка на существование вида войск
    # check_troop = await db.execute(select(Troops).filter_by(id=recruitment.troop_id))
    # troop = check_troop.scalar_one_or_none()
    # if not troop:
    #     raise HTTPException(status_code=404, detail="Такого вида войск не существует")
    #
    # Проверка на существование призывного пункта
    check_recruitment_office = await db.execute(
        select(RecruitmentOffice).filter_by(id=recruitment.recruitment_office_id))
    recruitment_office = check_recruitment_office.scalar_one_or_none()
    if not recruitment_office:
        raise HTTPException(status_code=404, detail="Такой призывной пункт не найден!")

    new_recruitment = Recruitment(
        name=recruitment.name,
        date_of_birth=recruitment.date_of_birth,
        address = recruitment.address,
        marital_status=recruitment.marital_status,
        #troop_id=recruitment.troop_id,
        recruitment_office_id=recruitment.recruitment_office_id,
    )

    db.add(new_recruitment)
    await db.commit()
    await db.refresh(new_recruitment)
    return new_recruitment

async def get_recruitments(session: AsyncSession, name: Optional[str] = None, address: Optional[str] = None,
                           marital_status: Optional[bool] = None, recruitment_office_id: Optional[int] = None,
                           date_of_birth: Optional[date] = None, troop_id: Optional[int] = None, skip: int = 0,
                           limit: int = 10, sort_by: Optional[str] = None, order: str = "asc"):
    query = select(Recruitment)

    # Фильтрация по имени
    if name:
        query = query.filter(Recruitment.name.ilike(f"%{name}%"))

    # Фильтрация по адресу
    if address:
        query = query.filter(Recruitment.address.ilike(f"%{address}%"))

    # Фильтрация по дате рождения (точное совпадение)
    if date_of_birth:
        query = query.filter(Recruitment.date_of_birth == date_of_birth)

    # Фильтрация по marital_status
    if marital_status is not None:
        query = query.filter(Recruitment.marital_status == marital_status)

    # Фильтрация по recruitment_office_id
    if recruitment_office_id:
        query = query.filter(Recruitment.recruitment_office_id == recruitment_office_id)

    # Фильтрация по troop_id
    if troop_id:
        query = query.filter(Recruitment.troop_id == troop_id)

    # Сортировка по полю sort_by
    if sort_by:
        column = getattr(Recruitment, sort_by, None)
        if column is not None:
            query = query.order_by(column.asc() if order == "asc" else column.desc())

    # Пагинация
    query = query.offset(skip).limit(limit)

    result = await session.execute(query)
    return result.scalars().all()


async def get_recruitment_by_id(session: AsyncSession, recruitment_id: int):
    result = await session.execute(select(Recruitment).filter(Recruitment.id == recruitment_id))
    return result.scalar_one_or_none()