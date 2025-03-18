import enum
from math import trunc

from pydantic import root_validator
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Enum

# Создаем базовый класс для всех моделей
Base = declarative_base()

class Troops(Base):
    __tablename__ = "troops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="CASCADE"), nullable=False)

    # Дочерняя связь к ...
    branch = relationship("Branch", back_populates="troops")
    # Родительская связь к ...
    recruitment = relationship("Recruitment", back_populates="troops")

class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    # Родительская связь
    troops = relationship("Troops", back_populates="branch", cascade="all, delete")

class MedExam(Base):
    __tablename__ = "med_exams"

    id = Column(Integer, primary_key=True, index=True)
    date_of_exam = Column(Date, nullable=False)
    recruitment_id = Column(Integer, ForeignKey("recruitments.id", ondelete="CASCADE"), nullable=False)
    result = Column(String, nullable=False)

    # Дочерняя связь к ...
    recruitment = relationship("Recruitment", back_populates="med_exam")

class ModeWorkOffice(Base):
    __tablename__ = "mode_work_offices"

    id = Column(Integer, primary_key=True)
    day = Column(String, nullable=False)
    work_start = Column(Time, nullable=False)
    work_end = Column(Time, nullable=False)
    recruitment_office_id = Column(Integer, ForeignKey("recruitment_offices.id", ondelete="CASCADE"))

    # Дочерняя связь к ...
    recruitment_office = relationship("RecruitmentOffice", back_populates="mode_work_office")

class RecruitmentOffice(Base):
    __tablename__ = "recruitment_offices"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True, nullable=False)
    chief_name = Column(String, index=True, nullable=False)

    # Родительская связь к ...
    recruitment = relationship("Recruitment", back_populates="recruitment_office")
    mode_work_office = relationship("ModeWorkOffice", back_populates="recruitment_office",
                                     cascade="all, delete")

class Recruitment(Base):
    __tablename__ = "recruitments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    address = Column(String, index=True, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    marital_status = Column(Boolean, nullable=False)
    troop_id = Column(Integer, ForeignKey("troops.id", ondelete="CASCADE"), nullable=True)
    photo = Column(String, nullable=True, default="/static/uploads/avatar.jpg")
    recruitment_office_id = Column(Integer, ForeignKey("recruitment_offices.id", ondelete="CASCADE"))

    # Родительская связь к ...
    med_exam = relationship("MedExam", back_populates="recruitment", cascade="all, delete")
    # Дочерняя связь к ...
    troops = relationship("Troops", back_populates="recruitment")
    recruitment_office = relationship("RecruitmentOffice", back_populates="recruitment")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False)
    password = Column(String, index=True, nullable=False)

    last_name = Column(String, nullable=True)  # Фамилия (по умолчанию пустая)
    first_name = Column(String, nullable=True)  # Имя (по умолчанию пустое)
    father_name = Column(String, nullable=True)  # Отчество (по умолчанию пустое)
    email = Column(String, unique=True, index=True, nullable=True)  # Email (по умолчанию пустой)