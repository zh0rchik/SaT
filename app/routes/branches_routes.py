from fastapi import APIRouter, Depends, HTTPException
from fastapi import FastAPI, Depends, HTTPException
from app.database import init_db, get_session
from app.schemas import BranchCreateSchema, BranchSchema
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import branches_crud

router = APIRouter(prefix="/branches", tags=["Роды войск"])

# API для создания нового подразделения
@router.post("/", status_code=201, response_model=BranchSchema, summary="Создать род войск")
async def create_branch(branch: BranchCreateSchema, db: AsyncSession = Depends(get_session)):
    return await branches_crud.create_branch(db=db, branch=branch)

# API для получения списка подразделений
@router.get("/", response_model=list[BranchSchema], summary="Получить все рода войск")
async def read_branches(db: AsyncSession = Depends(get_session)):
    branches = await branches_crud.get_branches(db=db)
    return branches

#API для получения сущности по индетификатору
@router.get("/{branch_id}", response_model=BranchSchema, summary="Получить род войска по id")
async def get_branch_by_id(branch_id: int, db: AsyncSession = Depends(get_session)):
    branch = await branches_crud.get_branch_by_id(db=db, branch_id=branch_id)

    if not branch:
        raise HTTPException(status_code=404, detail="Такого рода войск нет")

    return branch


# API для обновления существующего подразделения
@router.patch("/{branch_id}", response_model=BranchSchema, summary="Обновить род войск")
async def update_branch(
        branch_id: int,
        name: str = None,
        db: AsyncSession = Depends(get_session)):
    # Получаем существующее подразделение
    existing_branch = await branches_crud.get_branch_by_id(db=db, branch_id=branch_id)
    if not existing_branch:
        raise HTTPException(status_code=404, detail="Данного рода войск не найдено!")

    # Обновляем только те поля, которые были переданы
    if name:  # Если передано новое значение для name
        existing_branch.name = name

    # Сохраняем изменения в базе данных
    await db.commit()
    await db.refresh(existing_branch)

    return existing_branch

# API для удаления подразделения
@router.delete("/{branch_id}", status_code=204,summary="Удалить род войск")
async def delete_branch(branch_id: int, db: AsyncSession = Depends(get_session)):
    # Получаем существующее подразделение
    existing_branch = await branches_crud.get_branch_by_id(db=db, branch_id=branch_id)
    if not existing_branch:
        raise HTTPException(status_code=404, detail="Данного рода войска не найдено!")

    await branches_crud.delete_branch(db=db, branch_id=branch_id)
