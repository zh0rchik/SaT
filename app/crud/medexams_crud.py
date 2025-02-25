from typing import Optional

from sqlalchemy import text

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import MedExam
from app.schemas import MedExamCreateSchema

async def create_medexam(session: AsyncSession, medexam: MedExamCreateSchema):
    db_medexam = MedExam(
        date_of_exam = medexam.date_of_exam,
        recruitment_id = medexam.recruitment_id,
        result = medexam.result
    )
    session.add(db_medexam)

    if db_medexam.result != "годен к строевой службе":
        query = """
                UPDATE recruitments
                SET troop_id = NULL
                WHERE id = :recruitment_id
            """
        # с передачей параметра
        await session.execute(text(query), {'recruitment_id': db_medexam.recruitment_id})
    await session.commit()
    await session.refresh(db_medexam)
    return db_medexam

async def get_medexam_by_id(session: AsyncSession, medexam_id: int):
    result = await session.execute(select(MedExam).filter(MedExam.id == medexam_id))
    return result.scalar_one_or_none()


from sqlalchemy import select
from sqlalchemy.orm import Query
from sqlalchemy.future import select
from datetime import date
from sqlalchemy import or_

async def get_all(session: AsyncSession, skip: int = 0, limit: int = 10, sort_by: Optional[str] = None,
                  order: str = "asc", recruitment_id: Optional[int] = None,
                  date_from: Optional[date] = None, date_to: Optional[date] = None,
                  result: Optional[str] = None):
    query = select(MedExam)

    if recruitment_id:
        query = query.filter(MedExam.recruitment_id == recruitment_id)


    if date_from:
        query = query.filter(MedExam.date_of_exam >= date_from)
    if date_to:
        query = query.filter(MedExam.date_of_exam <= date_to)

    if result:
        query = query.filter(MedExam.result.ilike(f"%{result}%"))

    if sort_by:
        column = getattr(MedExam, sort_by, None)
        if column is not None:
            query = query.order_by(column.asc() if order == "asc" else column.desc())

    # паг
    query = query.offset(skip).limit(limit)

    result = await session.execute(query)
    return result.scalars().all()
