from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
import os
from datetime import date

from app.schemas import RecruitmentCreateSchema, RecruitmentSchema
from app.crud import recruitments_crud, recruitment_offices_crud, \
    troop_crud
from app.routes import troops_routes, recruitment_offices_router, medexams_routes
from app.database import get_session
from app.models import Recruitment

router = APIRouter(prefix="/recruitments", tags=["Призывники"])

# Папка для загрузки файлов
UPLOAD_DIR = "static/uploads/avatars"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Создать призывника
@router.post("/", response_model=RecruitmentSchema, summary="Добавить призывника")
async def create_recruitment(
        recruitment: RecruitmentCreateSchema,
        db: AsyncSession = Depends(get_session)
):
    # Создаем призывника через CRUD-функцию
    new_recruitment = await recruitments_crud.create_recruitment(
        db=db,
        recruitment=recruitment,
    )
    return new_recruitment

# Обновить фото
@router.post("/upload_avatar/{recruitment_id}", summary="Загрузить фотографию призывника")
async def upload_avatar(
        recruitment_id: int,
        photo: UploadFile = File(...),
        db: AsyncSession = Depends(get_session)
):
    try:
        # Генерируем уникальное имя файла
        file_extension = photo.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        local_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Сохраняем файл на диск
        contents = await photo.read()
        with open(local_path, "wb") as f:
            f.write(contents)

        # Получаем призывника по id
        result = await db.execute(select(Recruitment).filter_by(id=recruitment_id))
        recruitment = result.scalar_one_or_none()
        if not recruitment:
            raise HTTPException(status_code=404, detail="Призывник не найден")

        # Обновляем путь к аватарке
        recruitment.photo = f"/static/uploads/avatars/{unique_filename}"
        db.add(recruitment)
        await db.commit()
        await db.refresh(recruitment)

        return {"message": "Фотография обновлена", "photo_url": recruitment.photo}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при загрузке файла")

# Отобразить всех призывников
@router.get("/", response_model=list[RecruitmentSchema], summary="Получить всех призывников")
async def read_recruitments(db: AsyncSession = Depends(get_session)):
    recruitments = await recruitments_crud.get_recruitments(session=db)
    return recruitments

@router.get("/{recruitments_id}", response_model=RecruitmentSchema, summary="Получить призывника по ID")
async def get_recruitment_by_id(recruitment_id: int, db: AsyncSession = Depends(get_session)):
    result = await recruitments_crud.get_recruitment_by_id(session=db, recruitment_id=recruitment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Призывник не найден!")

    return result

@router.patch("/{recruitment_id}", response_model=RecruitmentSchema, summary="Обновить данные призывника")
async def update_recruitment(
        recruitment_id: int,
        db: AsyncSession = Depends(get_session),
        name: str = None,
        address: str = None,
        date_of_birth: date = None,
        marital_status: bool = None,
        troop_id: int = None,
        recruitment_office_id = None
):
    recruit = await recruitments_crud.get_recruitment_by_id(session=db, recruitment_id=recruitment_id)
    if not recruit:
        raise HTTPException(status_code=404, detail="Данный призывник не найден!")

    if recruitment_office_id:
        ro = await recruitment_offices_router.get_recruitment_office_by_id(db=db, recruitment_office_id=recruitment_office_id)
        recruit.recruitment_office_id = ro.id

    if troop_id:
        troop = await troops_routes.get_troop_by_id(db=db, troop_id=troop_id)
        medexams_recruit = await medexams_routes.get_medexams_of_recruits(recruit_id=recruitment_id, db=db)

        if medexams_recruit:
            last_medexam = medexams_recruit[-1]
            if last_medexam.result == "годен к строевой службе":
                recruit.troop_id = troop.id
            else:
                raise HTTPException(status_code=404, detail="Призывнику необходимо пройти мед. комиссию")
        else:
            raise HTTPException(status_code=404, detail="У призывника нет записей о мед. комиссиях")

    if name:
        recruit.name = name

    if address:
        recruit.address = address

    if date_of_birth:
        recruit.date_of_birth = date_of_birth

    if marital_status:
        recruit.marital_status = marital_status

    await db.commit()
    await db.refresh(recruit)

    return recruit

@router.delete("/{recruitment_id}", status_code=204, summary="Удалить призывника")
async def delete_recruit(recruit_id: int, db: AsyncSession = Depends(get_session)):
    existing_recruit = await recruitments_crud.get_recruitment_by_id(session=db, recruitment_id=recruit_id)
    if not existing_recruit:
        raise HTTPException(status_code=404, detail="Призывник не найден.")

    await db.delete(existing_recruit)
    await db.commit()
