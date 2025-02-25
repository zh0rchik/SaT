from typing import Optional

from app.schemas import TroopsCreateSchema
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Troops, Branch
from sqlalchemy import select
from fastapi import HTTPException

# Функция для создания нового вида войск
async def create_troop(session: AsyncSession, troop: TroopsCreateSchema):
    try:
        # Проверка существования branch_id
        result = await session.execute(select(Branch).filter_by(id=troop.branch_id))
        branch = result.scalar_one_or_none()

        if not branch:
            raise HTTPException(status_code=404, detail="Такого рода войск не существует")

        # Создание и добавление новой записи в таблицу troops
        new_troop = Troops(name=troop.name, branch_id=troop.branch_id)
        session.add(new_troop)
        await session.commit()
        await session.refresh(new_troop)
        return new_troop

    except Exception as e:
        # Обработка других исключений
        await session.rollback()
        raise HTTPException(status_code=404, detail="Error: " + str(e))

async def get_troops(session: AsyncSession, skip: int = 0, limit: int = 10, sort_by: Optional[str] = None,
                     order: str = "asc", name: Optional[str] = None, branch_id: Optional[int] = None):
    query = select(Troops)

    # Фильтрация по имени (если передан параметр name)
    if name:
        query = query.filter(Troops.name.ilike(f"%{name}%"))

    # Фильтрация по branch_id (если передан параметр branch_id)
    if branch_id:
        query = query.filter(Troops.branch_id == branch_id)

    # Сортировка по полю sort_by (если передан параметр sort_by)
    if sort_by:
        column = getattr(Troops, sort_by, None)
        if column is not None:
            query = query.order_by(column.asc() if order == "asc" else column.desc())

    # Пагинация
    query = query.offset(skip).limit(limit)

    result = await session.execute(query)
    return result.scalars().all()

async def get_troop_by_id(session:AsyncSession, troop_id: int):
    result = await session.execute(select(Troops).filter(Troops.id == troop_id))
    return result.scalar_one_or_none()


async def delete_troop(session: AsyncSession, troop_id: id):
    existing_troop = await get_troop_by_id(session, troop_id)
    if existing_troop:
        await session.delete(existing_troop)
        await session.commit()