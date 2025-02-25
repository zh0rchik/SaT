from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Branch
from app.schemas import BranchCreateSchema

# Функция для создания нового подразделения
async def create_branch(db: AsyncSession, branch: BranchCreateSchema):
    db_branch = Branch(name=branch.name)
    db.add(db_branch)
    await db.commit()
    await db.refresh(db_branch)
    return db_branch

# Функция для получения всех подразделений
async def get_branches(db: AsyncSession, skip: int = 0, limit: int = 10, sort_by: Optional[str] = None,
                       order: str = "asc", name: Optional[str] = None):
    query = select(Branch)

    # Фильтрация по названию
    if name:
        query = query.filter(Branch.name.ilike(f"%{name}%"))

    # Сортировка
    if sort_by:
        if order == "asc":
            query = query.order_by(getattr(Branch, sort_by).asc())
        else:
            query = query.order_by(getattr(Branch, sort_by).desc())

    # Пагинация
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()

# Примерный код для CRUD операций
async def get_branch_by_id(db: AsyncSession, branch_id: int):
    result = await db.execute(select(Branch).filter(Branch.id == branch_id))
    return result.scalar_one_or_none()

async def update_branch(db: AsyncSession, branch_id: int, branch: BranchCreateSchema):
    existing_branch = await get_branch_by_id(db, branch_id)
    if not existing_branch:
        return None

    # Обновляем поля, которые не пустые
    if branch.name:
        existing_branch.name = branch.name

    await db.commit()
    await db.refresh(existing_branch)
    return existing_branch

async def delete_branch(db: AsyncSession, branch_id: int):
    # Получаем запись для удаления
    existing_branch = await get_branch_by_id(db, branch_id)
    if existing_branch:
        await db.delete(existing_branch)
        await db.commit()