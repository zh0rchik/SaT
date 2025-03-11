from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session, get_current_user
from app.schemas import TroopsSchema, TroopsCreateSchema
from app.crud import troop_crud
from app.routes import branches_routes

from app.models import User

router = APIRouter(prefix="/troops", tags=["Виды войск"])

# API для создания новой вида войск
@router.post("/", status_code=201, response_model=TroopsSchema, summary=["Создать вид войск"])
async def create_troop(troop: TroopsCreateSchema,
                       db: AsyncSession = Depends(get_session),
                       current_user: User = Depends(get_current_user)):
    return await troop_crud.create_troop(session=db, troop=troop)

# API для отображения всех видов войск
@router.get("/", response_model=list[TroopsSchema], summary="Получить все виды войск")
async def read_troops(
        db: AsyncSession = Depends(get_session),
        skip: int = Query(0),                                   # Сколько записей пропустить - пагинация
        limit: int = Query(10),                                 # Сколько вернуть - пагинация
        sort_by: Optional[str] = Query(None),                   # Поле для сортировки
        order: str = Query("asc", regex="^(asc|desc)$"),         # Порядок сортировки
        name: Optional[str] = Query(None),                       # Фильтрация по имени
        branch_id: Optional[int] = Query(None)                   # Фильтрация по branch_id
        ):
    troops = await troop_crud.get_troops(
        session=db, skip=skip, limit=limit, sort_by=sort_by, order=order, name=name, branch_id=branch_id
    )
    return troops

# API для получения записи по ID
@router.get("/{troop_id}", response_model=TroopsSchema, summary=["Получить вид войск по id"])
async def get_troop_by_id(troop_id: int, db: AsyncSession = Depends(get_session)):
    result = await troop_crud.get_troop_by_id(session=db, troop_id=troop_id)

    if not result:
        raise HTTPException(status_code=404, detail="Данный род войск не найден!")

    return result

# API для обновления существого вида войск
@router.patch("/{troop_id}", response_model=TroopsSchema, summary="Обновить вид войск")
async def update_troop(
        troop_id: int,
        name: str = None,
        branch_id: int = None,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user)):
    exist_troop = await troop_crud.get_troop_by_id(session=db, troop_id=troop_id)

    if not exist_troop:
        raise HTTPException(status_code=404, detail="Данного вида войск не найдено!")

    if name:
        exist_troop.name = name

    if branch_id:
        branch = await branches_routes.get_branch_by_id(db=db, branch_id=branch_id)
        exist_troop.branch_id = branch.id

    # Сохраняем изменения в БД
    await db.commit()
    await db.refresh(exist_troop)

    return exist_troop

@router.delete("/{troop_id}", status_code=204, summary="Удалить вид войск")
async def delete_troop(troop_id: int,
                       db: AsyncSession = Depends(get_session),
                       current_user: User = Depends(get_current_user)):
    existing_troop = await troop_crud.get_troop_by_id(session=db, troop_id=troop_id)
    if not existing_troop:
        raise HTTPException(status_code=404, detail="Данный род войск не найден!")

    await troop_crud.delete_troop(session=db, troop_id=troop_id)