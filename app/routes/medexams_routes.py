from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import Recruitment, MedExam
from app.schemas import MedExamSchema, MedExamCreateSchema
from app.crud import medexams_crud, recruitments_crud
from sqlalchemy import select
from app.routes.recruitments_router import update_recruitment

router = APIRouter(prefix="/medexams", tags=["Медицинские комиссии"])

from app.models import User
from app.database import get_session, get_current_user

@router.post("/", response_model=MedExamSchema, summary="Создать мед. комиссию")
async def create_medexam(
        medexam: MedExamCreateSchema,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user)):
    check_recruitment= await db.execute(select(Recruitment).filter_by(id=medexam.recruitment_id))
    recruitment = check_recruitment.scalar_one_or_none()
    if not recruitment:
        raise HTTPException(status_code=404, detail="Призывник не найден!")

    return await medexams_crud.create_medexam(session=db, medexam=medexam)


@router.get("/", response_model=list[MedExamSchema], summary="Получить мед. комиссии призывника")
async def get_medexams_of_recruits(
        recruit_id: int,
        db: AsyncSession = Depends(get_session)):
    check_recruitment = await db.execute(select(Recruitment).filter_by(id=recruit_id))
    recruitment = check_recruitment.scalar_one_or_none()

    if not recruitment:
        raise HTTPException(status_code=404, detail="Призывник не найден!")

    # Получаем все медкомиссии
    result = await db.execute(select(MedExam).filter_by(recruitment_id=recruit_id))
    medexams = result.scalars().all()

    return medexams

# @router.delete("/{medexams_id}", status_code=204, summary="Удалить мед. комиссию")
# async def delete_recruit(medexam_id: int, db: AsyncSession = Depends(get_session),
#                          current_user: User = Depends(get_current_user)):
#     existing_medexam= await medexams_crud.get_medexam_by_id(session=db, medexam_id=medexam_id)
#     if not existing_medexam:
#         raise HTTPException(status_code=404, detail="Призывник не найден.")
#
#     await db.delete(existing_medexam)
#     await db.commit()