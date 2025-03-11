from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import Recruitment, MedExam
from app.schemas import MedExamSchema, MedExamCreateSchema
from app.crud import medexams_crud, recruitments_crud
from sqlalchemy import select
from app.routes.recruitments_router import update_recruitment
from datetime import date

router = APIRouter(prefix="/medexams", tags=["Медицинские комиссии"])

from app.models import User
from app.database import get_session, get_current_user

@router.post("/", response_model=MedExamSchema, status_code=201, summary="Создать мед. комиссию")
async def create_medexam(
        medexam: MedExamCreateSchema,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user)):
    check_recruitment= await db.execute(select(Recruitment).filter_by(id=medexam.recruitment_id))
    recruitment = check_recruitment.scalar_one_or_none()
    if not recruitment:
        raise HTTPException(status_code=404, detail="Призывник не найден!")

    return await medexams_crud.create_medexam(session=db, medexam=medexam)


@router.get("/{recruitment_id}", response_model=list[MedExamSchema], summary="Получить мед. комиссии призывника")
async def get_medexams_of_recruits(
        recruitment_id: int,
        db: AsyncSession = Depends(get_session)):
    check_recruitment = await db.execute(select(Recruitment).filter_by(id=recruitment_id))
    recruitment = check_recruitment.scalar_one_or_none()

    if not recruitment:
        raise HTTPException(status_code=404, detail="Призывник не найден!")

    # Получаем все медкомиссии
    result = await db.execute(select(MedExam).filter_by(recruitment_id=recruitment_id))
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

@router.get("/", response_model=list[MedExamSchema], summary="Получить все мед. комиссии")
async def read_medexams(
        db: AsyncSession = Depends(get_session),
        skip: int = Query(0),                                   # Сколько записей пропустить - пагинация
        limit: int = Query(10),                                 # Сколько вернуть - пагинация
        sort_by: Optional[str] = Query(None),                   # Поле для сортировки
        order: str = Query("asc", regex="^(asc|desc)$"),         # Порядок сортировки
        recruitment_id: Optional[int] = Query(None),             # Фильтрация по рекруту
        date_from: Optional[date] = Query(None),                 # Фильтрация по дате начала
        date_to: Optional[date] = Query(None),                   # Фильтрация по дате конца
        result: Optional[str] = Query(None)                      # Фильтрация по результату
        ):

    # Передаем параметры в CRUD
    medexams = await medexams_crud.get_all(
        session=db, skip=skip, limit=limit, sort_by=sort_by, order=order,
        recruitment_id=recruitment_id, date_from=date_from, date_to=date_to, result=result
    )
    return medexams
