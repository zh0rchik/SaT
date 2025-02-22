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
