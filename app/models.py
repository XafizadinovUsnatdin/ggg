# ORM Models / Entities Column → table ustunlari
# Integer, String, Boolean → data turlari
# ForeignKey → tablelar orasidagi bog‘lanish
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
#ORM Model / Entity
# relationship → Python darajasida bog‘lanish (ORM)
from sqlalchemy.orm import relationship

# Base → barcha modellarning asosiy classi
from app.database import Base


# ========================
# USER TABLE
# ========================

class User(Base):
    # DB ichidagi table nomi
    __tablename__ = "users"

    # Primary key (unikal ID)
    id = Column(Integer, primary_key=True, index=True)

    # Username (unikal bo‘lishi kerak)
    username = Column(String, unique=True, index=True, nullable=False)

    # Parol (hash qilingan holda saqlanadi)
    hashed_password = Column(String, nullable=False)

    # User → Task bog‘lanishi
    # Bu userning nechta taski borligini ko‘rsatadi
    tasks = relationship("Task", back_populates="owner")


# ========================
# TASK TABLE
# ========================

class Task(Base):
    __tablename__ = "tasks"

    # Task ID
    id = Column(Integer, primary_key=True, index=True)

    # Task nomi (bo‘sh bo‘lishi mumkin emas)
    title = Column(String, nullable=False)

    # Task haqida qo‘shimcha ma’lumot
    description = Column(String, nullable=True)

    # Task bajarildimi yo‘qmi
    is_done = Column(Boolean, default=False)

    # Bu task qaysi userga tegishli
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Task → User bog‘lanishi
    owner = relationship("User", back_populates="tasks")



# yangi ustun due date frontend o'zgarish kiritish uchun
    due_date = Column(Date, nullable=False)