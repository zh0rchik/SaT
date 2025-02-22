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

async def get_troops(session: AsyncSession):
    result = await session.execute(select(Troops))
    return result.scalars().all()

async def get_troop_by_id(session:AsyncSession, troop_id: int):
    result = await session.execute(select(Troops).filter(Troops.id == troop_id))
    return result.scalar_one_or_none()


async def delete_troop(session: AsyncSession, troop_id: id):
    existing_troop = await get_troop_by_id(session, troop_id)
    if existing_troop:
        await session.delete(existing_troop)
        await session.commit()