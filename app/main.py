# FastAPI classini import qilyapmiz
# Bu bizga API application yaratish imkonini beradi

print("🚀 MAIN.PY ISHLADI")


from datetime import date
# FastAPI asosiy class
# Depends → dependency injection (DB, user)
# HTTPException → xatolik qaytarish
# status → HTTP status code
from fastapi import FastAPI, Depends, HTTPException, status

# Login form (username, password olish uchun)
from fastapi.security import OAuth2PasswordRequestForm

# Database session type
from sqlalchemy.orm import Session


# Database ulanish, Base (model uchun), engine (connection), get_db (session)
from app.database import Base, engine, get_db
# models → DB table
# schemas → request/response format
# crud → DB bilan ishlash logikasi
from app import models, schemas, crud

# JWT token yaratish funksiyasi
from app.auth import create_access_token

# Token orqali userni aniqlash
from app.deps import get_current_user

# Frontend bilan bog‘lanish uchun (CORS)
from fastapi.middleware.cors import CORSMiddleware



print("✅ MODELS IMPORT BO‘LDI")
# app degan FastAPI obyekt yaratilyapti
# Server shu app orqali ishlaydi
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# models.py ichidagi User va Task classlarni ko‘rib,
# database ichida users va tasks table yaratadi
# DBdagi jadvallarni yaratadi (keyin model yozganda ishlaydi)
print("⚙️ CREATE_ALL ISHLAYAPTI")
Base.metadata.create_all(bind=engine)

print("✅ TABLE YARATISH TUGADI")
# Bu GET endpoint
# Ya'ni foydalanuvchi browserdan "/" ga kirsa, shu funksiya ishlaydi


# ========================
# TEST ENDPOINT
# ========================

# GET / → test uchun endpoint
@app.get("/")
def home():
    return {"message": "FastAPI ishlayapti"}


# ========================
# REGISTER
# ========================

@app.post("/register", response_model=schemas.UserResponse)
def register(
    user: schemas.UserCreate,           # frontenddan keladigan data
    db: Session = Depends(get_db)       # DB connection avtomatik keladi
):
    # Username oldin mavjudmi tekshiramiz
    existing_user = crud.get_user_by_username(db, user.username)

    # Agar mavjud bo‘lsa error qaytaramiz
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Bu username allaqachon mavjud"
        )

    # Yangi user yaratamiz (parol hash qilinadi)
    return crud.create_user(db, user)

# ========================
# LOGIN
# ========================

@app.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  # username + password
    db: Session = Depends(get_db)
):
    # Userni tekshiramiz
    user = crud.authenticate_user(
        db,
        form_data.username,
        form_data.password
    )

    # Agar noto‘g‘ri bo‘lsa error
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username yoki password noto‘g‘ri"
        )

    # JWT token yaratamiz
    token = create_access_token(
        data={"sub": user.username}   # token ichida username saqlanadi
    )

    # Frontendga token qaytaramiz
    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ========================
# CREATE TASK
# ========================

@app.post("/tasks", response_model=schemas.TaskResponse)
def create_task(
    task: schemas.TaskCreate,                  # frontenddan kelgan task
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)  
    # 🔥 token orqali userni aniqlaymiz
):
    # Taskni DBga yozamiz
    return crud.create_task(
        db=db,
        task=task,
        user_id=current_user.id   # task qaysi userga tegishli
    )


# ========================
# GET TASKS
# ========================
@app.get("/tasks", response_model=list[schemas.TaskResponse])
def get_tasks(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_user_tasks(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )


@app.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    task = crud.update_task(
        db=db,
        task_id=task_id,
        user_id=current_user.id,
        task_update=task_update
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task topilmadi")

    return task


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    task = crud.delete_task(
        db=db,
        task_id=task_id,
        user_id=current_user.id
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task topilmadi")

    return {"message": "Task o‘chirildi"}