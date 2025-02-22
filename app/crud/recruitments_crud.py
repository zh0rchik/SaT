from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Recruitment, Troops, RecruitmentOffice
from app.schemas import RecruitmentCreateSchema
from fastapi import HTTPException, UploadFile
from sqlalchemy.future import select
from pathlib import Path

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

async def get_recruitments(session: AsyncSession):
    result = await session.execute(select(Recruitment))
    return result.scalars().all()

async def get_recruitment_by_id(session: AsyncSession, recruitment_id: int):
    result = await session.execute(select(Recruitment).filter(Recruitment.id == recruitment_id))
    return result.scalar_one_or_none()