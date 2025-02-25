from typing import Optional

from app.models import RecruitmentOffice, ModeWorkOffice
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import ModeWorkOfficeCreateSchema


async def create_recruitment_office(session, recruitment_office):
    db_ro = RecruitmentOffice(
        address=recruitment_office.address,
        chief_name=recruitment_office.chief_name
    )

    session.add(db_ro)
    await session.commit()
    await session.refresh(db_ro)
    return db_ro

async def get_recruit_offices(
    session: AsyncSession,
    address: Optional[str] = None,
    chief_name: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    sort_by: Optional[str] = None,
    order: str = "asc"
):
    query = select(RecruitmentOffice)

    # Фильтрация по адресу (ищет вхождения)
    if address:
        query = query.filter(RecruitmentOffice.address.ilike(f"%{address}%"))

    # Фильтрация по имени начальника (ищет вхождения)
    if chief_name:
        query = query.filter(RecruitmentOffice.chief_name.ilike(f"%{chief_name}%"))

    # Сортировка по указанному полю
    if sort_by:
        column = getattr(RecruitmentOffice, sort_by, None)
        if column is not None:
            query = query.order_by(column.asc() if order == "asc" else column.desc())

    # Пагинация
    query = query.offset(skip).limit(limit)

    result = await session.execute(query)
    return result.scalars().all()


async def get_recruitment_office_by_id(session: AsyncSession, recruitment_office_id: int):
    result = await session.execute(select(RecruitmentOffice).filter(RecruitmentOffice.id == recruitment_office_id))
    return result.scalar_one_or_none()

async def get_mode_work_by_id(session: AsyncSession, mode_work_id: int):
    result = await session.execute(select(ModeWorkOffice).filter(ModeWorkOffice.id == mode_work_id))
    return result.scalar_one_or_none()

async def delete_recruitment_office(session: AsyncSession, recruitment_office_id: int):
    existing_recruitment_office = await get_recruitment_office_by_id(session, recruitment_office_id)
    if existing_recruitment_office:
        await session.delete(existing_recruitment_office)
        await session.commit()
    return existing_recruitment_office


async def add_mode_work(session: AsyncSession,
                  recruitment_office_id: int,
                  mode_work: ModeWorkOfficeCreateSchema):
    existing_recruitment_office = await get_recruitment_office_by_id(session, recruitment_office_id)
    if existing_recruitment_office:
        db_wm = ModeWorkOffice(
            day=mode_work.day,
            work_start=mode_work.work_start,
            work_end=mode_work.work_end,
            recruitment_office_id=recruitment_office_id
        )

        session.add(db_wm)
        await session.commit()
        await session.refresh(db_wm)

        return db_wm
    else:
        return None


async def get_modes_work(session: AsyncSession, recruitment_office_id: int):
    existing_recruitment_office = await get_recruitment_office_by_id(session, recruitment_office_id)
    if existing_recruitment_office:
        result = await session.execute(
            select(ModeWorkOffice).filter(ModeWorkOffice.recruitment_office_id == recruitment_office_id))
        return result.scalars().all()
    else:
        return None

async def get_all_modes_work(session: AsyncSession):
    result = await session.execute(select(ModeWorkOffice))
    return result.scalars().all()
