from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session, get_current_user
from app.schemas import RecruitmentOfficeCreateSchema, RecruitmentOfficeSchema, ModeWorkOfficeCreateSchema, ModeWorkOfficeSchema
from app.crud import recruitment_offices_crud
from datetime import time
from app.models import User

router = APIRouter(prefix="/recruitment_offices", tags=["Призывные пункты"])

@router.post("/", response_model=RecruitmentOfficeSchema, summary="Создать призывной пункт")
async def create_recruitment_office(
        ro: RecruitmentOfficeCreateSchema,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user)):
    return await recruitment_offices_crud.create_recruitment_office(session=db, recruitment_office=ro)

@router.get("/", response_model=list[RecruitmentOfficeSchema], summary="Получить все пункты призыва")
async def read_recruitment_offices(db: AsyncSession = Depends(get_session)):
    recruitment_offices = await recruitment_offices_crud.get_branches(session=db)
    return recruitment_offices

@router.get("/{recruitment_office_id}", response_model=RecruitmentOfficeSchema, summary="Получить призывной пункт по ID")
async def get_recruitment_office_by_id(recruitment_office_id: int, db: AsyncSession = Depends(get_session)):
    result = await recruitment_offices_crud.get_recruitment_office_by_id(session=db, recruitment_office_id=recruitment_office_id)

    if not result:
        raise HTTPException(status_code=404, detail="Данный пункт призыва не найден!")

    return result

@router.patch("/{recruitment_office_id}", response_model=RecruitmentOfficeSchema, summary="Обновить данные призывного пункта")
async def update_recruitment_office(
        recruitment_office_id: int,
        db: AsyncSession = Depends(get_session),
        address: str = None,
        chief_name: str = None,
        current_user: User = Depends(get_current_user)
):
    exist_recruitment_office = await recruitment_offices_crud.get_recruitment_office_by_id(session=db,
                                                                                           recruitment_office_id=recruitment_office_id)
    if not exist_recruitment_office:
        raise HTTPException(status_code=404, detail="Данный призывной пункт не найден!")

    if address:
        exist_recruitment_office.address = address

    if chief_name:
        exist_recruitment_office.chief_name = chief_name

    await db.commit()
    await db.refresh(exist_recruitment_office)

    return exist_recruitment_office

@router.delete("/{recruitment_office_id}", status_code=204, summary="Удалить призывной пункт")
async def delete_recruitment_office(recruitment_office_id: int, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    existing_recruitment_office = await recruitment_offices_crud.get_recruitment_office_by_id(session=db, recruitment_office_id=recruitment_office_id)
    if not existing_recruitment_office:
        raise HTTPException(status_code=404, detail="Данный род войск не найден!")

    await recruitment_offices_crud.delete_recruitment_office(session=db, recruitment_office_id=recruitment_office_id)

@router.post("/work_hours_office/{recruitment_office_id}", response_model=ModeWorkOfficeSchema, summary="Добавить режим работы офиса")
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

@router.get("/work_hours_office/{recruitment_office_id}", response_model=list[ModeWorkOfficeSchema], summary="Режим работы призывного пункта")
async def get_modes_work(recruitment_office_id: int, db: AsyncSession = Depends(get_session)):
    existing_recruitment_office = await recruitment_offices_crud.get_recruitment_office_by_id(session=db,
                                                                                              recruitment_office_id=recruitment_office_id)
    if not existing_recruitment_office:
        raise HTTPException(status_code=404, detail="Данный род войск не найден!")

    modes_work = await recruitment_offices_crud.get_modes_work(session=db, recruitment_office_id=recruitment_office_id)

    return modes_work

@router.delete("/work_hours_office/{work_hours_office}", status_code=204, summary="Удалить режим работы")
async def delete_mode_work(mode_work_id: int,
                           db: AsyncSession = Depends(get_session),
                           current_user: User = Depends(get_current_user)):
    existing_mode_work = await recruitment_offices_crud.get_mode_work_by_id(session=db, mode_work_id=mode_work_id)
    if not existing_mode_work:
        raise HTTPException(status_code=404, detail="Режим работы не найден.")

    await db.delete(existing_mode_work)
    await db.commit()
