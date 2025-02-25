from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session, get_current_user
from app.schemas import ModeWorkOfficeCreateSchema, ModeWorkOfficeSchema
from app.crud import recruitment_offices_crud
from datetime import time
from app.models import User

router = APIRouter(prefix="/work_hours_office", tags=["Режимы работы"])

@router.post("/{recruitment_office_id}", response_model=ModeWorkOfficeSchema, summary="Добавить режим работы офиса")
async def add_mode_work(
        recruitment_office_id: int,
        mode_work: ModeWorkOfficeCreateSchema,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    mode_work = await recruitment_offices_crud.add_mode_work(session=db,
                                                             recruitment_office_id=recruitment_office_id,
                                                             mode_work=mode_work)

    if not mode_work:
        raise HTTPException(status_code=404, detail="Данный призывной пункт не найден!")
    return mode_work

@router.get("/{recruitment_office_id}", response_model=list[ModeWorkOfficeSchema], summary="Режим работы призывного пункта")
async def get_modes_work(recruitment_office_id: int, db: AsyncSession = Depends(get_session)):
    existing_recruitment_office = await recruitment_offices_crud.get_recruitment_office_by_id(session=db,
                                                                                              recruitment_office_id=recruitment_office_id)
    if not existing_recruitment_office:
        raise HTTPException(status_code=404, detail="Данный режим работы не найден не найден")

    modes_work = await recruitment_offices_crud.get_modes_work(session=db, recruitment_office_id=recruitment_office_id)

    return modes_work

@router.delete("/{work_hours_office}", status_code=204, summary="Удалить режим работы")
async def delete_mode_work(mode_work_id: int,
                           db: AsyncSession = Depends(get_session),
                           current_user: User = Depends(get_current_user)):
    existing_mode_work = await recruitment_offices_crud.get_mode_work_by_id(session=db, mode_work_id=mode_work_id)
    if not existing_mode_work:
        raise HTTPException(status_code=404, detail="Режим работы не найден.")

    await db.delete(existing_mode_work)
    await db.commit()

@router.get("/", response_model=list[ModeWorkOfficeSchema], summary="Получить все режимы работы офисов")
async def get_all_modes_work(db: AsyncSession = Depends(get_session)):
    modes_work = await recruitment_offices_crud.get_all_modes_work(session=db)
    if not modes_work:
        raise HTTPException(status_code=404, detail="Режимы работы не найдены!")
    return modes_work