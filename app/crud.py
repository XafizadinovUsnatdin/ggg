
from datetime import date

# SQLAlchemy Session — DB bilan ishlash uchun object
# Har bir query (SELECT, INSERT, UPDATE) shu orqali bajariladi
from sqlalchemy.orm import Session

# models → database table (User, Task)
# schemas → frontenddan keladigan data format (UserCreate, TaskCreate)
from app import models, schemas

# auth → passwordni hash qilish va tekshirish funksiyalari
from app.auth import hash_password, verify_password


# ========================
# USERNI QIDIRISH
# ========================

def get_user_by_username(db: Session, username: str):
    """
    DB dan username bo‘yicha userni topadi
    """

    # SELECT * FROM users WHERE username = 'ali' LIMIT 1
    return db.query(models.User).filter(
        models.User.username == username
    ).first()   # birinchi topilgan userni qaytaradi


# ========================
# USER YARATISH (REGISTER)
# ========================

def create_user(db: Session, user: schemas.UserCreate):
    """
    Yangi user yaratadi
    """

    # ❗ XAVFSIZLIK:
    # passwordni oddiy holda saqlamaymiz
    # hash qilib DB ga yozamiz
    hashed = hash_password(user.password)

    # Python object yaratamiz (hali DB ga yozilmadi)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed
    )

    # DB ga qo‘shamiz (queue ga tushadi)
    db.add(db_user)

    # 🔥 ENG MUHIM:
    # commit → haqiqiy DB ga yozadi
    db.commit()

    # DB dan yangi qiymatlarni (masalan id) qayta olib keladi
    db.refresh(db_user)

    # Yaratilgan userni qaytaramiz
    return db_user


# ========================
# LOGIN (AUTHENTICATION)
# ========================

def authenticate_user(db: Session, username: str, password: str):
    """
    Login paytida userni tekshiradi
    """

    # DB dan userni topamiz
    user = get_user_by_username(db, username)

    # Agar user topilmasa
    if not user:
        return None   # login fail

    # Passwordni tekshiramiz:
    # plain password vs hashed password
    if not verify_password(password, user.hashed_password):
        return None   # login fail

    # Hammasi to‘g‘ri → user qaytadi
    return user


# ========================
# TASK YARATISH
# ========================

def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    """
    Yangi task yaratadi
    """

    # Task object yaratamiz
    db_task = models.Task(
        title=task.title,              # task nomi
        description=task.description,  # description
        due_date=task.due_date,
        owner_id=user_id               # qaysi userga tegishli
    )

    # DB ga qo‘shamiz
    db.add(db_task)

    # DB ga yozamiz
    db.commit()

    # yangi qiymatlarni olib kelamiz (id va h.k.)
    db.refresh(db_task)

    # Yaratilgan taskni qaytaramiz
    return db_task


# ========================
# USER TASKLARINI OLISH
# ========================

def get_user_tasks(db: Session, user_id: int):
    """
    Faqat shu userga tegishli tasklarni qaytaradi
    """

    # SELECT * FROM tasks WHERE owner_id = 1
    return db.query(models.Task).filter(
        models.Task.owner_id == user_id
    ).all()   # barcha tasklarni list ko‘rinishda qaytaradi

def get_user_tasks(
    db: Session,
    user_id: int,
    start_date: date | None = None,
    end_date: date | None = None
):
    query = db.query(models.Task).filter(
        models.Task.owner_id == user_id
    )

    if start_date:
        query = query.filter(models.Task.due_date >= start_date)

    if end_date:
        query = query.filter(models.Task.due_date <= end_date)

    return query.order_by(models.Task.due_date.asc()).all()


def get_task(db: Session, task_id: int, user_id: int):
    return db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == user_id
    ).first()


def update_task(
    db: Session,
    task_id: int,
    user_id: int,
    task_update: schemas.TaskUpdate
):
    task = get_task(db, task_id, user_id)

    if not task:
        return None

    if task_update.title is not None:
        task.title = task_update.title

    if task_update.description is not None:
        task.description = task_update.description

    if task_update.is_done is not None:
        task.is_done = task_update.is_done

    if task_update.due_date is not None:
        task.due_date = task_update.due_date

    db.commit()
    db.refresh(task)

    return task


def delete_task(db: Session, task_id: int, user_id: int):
    task = get_task(db, task_id, user_id)

    if not task:
        return None

    db.delete(task)
    db.commit()

    return task