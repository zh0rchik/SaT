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


async def get_branches(session: AsyncSession):
    result = await session.execute(select(RecruitmentOffice))
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