from enum import Enum

from pydantic import BaseModel
from datetime import date
from datetime import time
from typing import Optional
from fastapi import UploadFile

class BranchCreateSchema(BaseModel):
    name: str

class BranchSchema(BranchCreateSchema):
    id: int

    class Config:
        from_attributes = True

class TroopsCreateSchema(BaseModel):
    name: str
    branch_id: int

class TroopsSchema(TroopsCreateSchema):
    id: int

    class Config:
        from_attributes = True

class ExamResult(str, Enum):
    FIT = "годен к строевой службе"
    ALTERNATIVE_SERVICE = "годен к альтернативной службе"
    FIT_LIMITED = "ограничено годен"
    UNFIT = "не годен"

class MedExamCreateSchema(BaseModel):
    date_of_exam: date
    recruitment_id: int
    result: ExamResult

class MedExamSchema(MedExamCreateSchema):
    id: int

    class Config:
        from_attributes = True

class RecruitmentOfficeCreateSchema(BaseModel):
    address: str
    chief_name: str
    # work_time_start: time
    # work_time_end: time

    class Config:
        from_attributes = True

class RecruitmentOfficeSchema(RecruitmentOfficeCreateSchema):
    id: int

class DayOfWeek(str, Enum):  # Используем enum из стандартной библиотеки
    MONDAY = "Пн"
    TUESDAY = "Вт"
    WEDNESDAY = "Ср"
    THURSDAY = "Чт"
    FRIDAY = "Пт"

class ModeWorkOfficeCreateSchema(BaseModel):
    day: DayOfWeek
    work_start: time
    work_end: time


class ModeWorkOfficeSchema(ModeWorkOfficeCreateSchema):
    id: int
    recruitment_office_id: int

class RecruitmentCreateSchema(BaseModel):
    name: str
    date_of_birth: date
    address: str
    marital_status: bool = False
    recruitment_office_id: int

DEFAULT_AVATAR = "/static/uploads/avatar.jpg"
class RecruitmentSchema(RecruitmentCreateSchema):
    id: int
    photo: Optional[str] = DEFAULT_AVATAR
    troop_id: Optional[int]

    class Config:
        from_attributes = True