# Pydantic BaseModel → APIga kelayotgan va ketayotgan data ni tekshiradi (validation)

from datetime import date

from pydantic import BaseModel
#DTO / VALIDATION LAYER
#Dasturchilar tilida: DTO (Data Transfer Object)

# ========================
# REGISTER INPUT
# ========================

# Register paytida frontenddan keladigan data
class UserCreate(BaseModel):
    username: str   # username majburiy (string)
    password: str   # password majburiy (string)


# ========================
# USER RESPONSE
# ========================

# API user haqida qaytaradigan data
# ❗ password qaytarmaymiz (xavfsizlik uchun)
class UserResponse(BaseModel):
    id: int          # user ID
    username: str    # username

    # SQLAlchemy modelni Pydantic modelga aylantirish uchun
    model_config = {
        "from_attributes": True
    }


# ========================
# TOKEN RESPONSE
# ========================

# Login qilgandan keyin frontendga token qaytadi
class Token(BaseModel):
    access_token: str   # JWT token
    token_type: str     # odatda "bearer"


# ========================
# TASK CREATE (INPUT)
# ========================

# Task yaratishda frontenddan keladigan data
class TaskCreate(BaseModel):
    title: str                       # task nomi (majburiy)
    description: str | None = None  # description ixtiyoriy (None bo‘lishi mumkin)
    due_date: date

# ========================
# TASK UPDATE (INPUT)
# ========================

# Taskni update qilish uchun schema
# ❗ hamma field ixtiyoriy (partial update uchun)
class TaskUpdate(BaseModel):
    title: str | None = None        # yangi title (bo‘lsa)
    description: str | None = None  # yangi description
    is_done: bool | None = None     # task bajarilganmi
    due_date: date | None = None

# ========================
# TASK RESPONSE
# ========================

# API task haqida qaytaradigan data
class TaskResponse(BaseModel):
    id: int              # task ID
    title: str           # task nomi
    description: str | None
    is_done: bool        # bajarilganmi yoki yo‘q
    owner_id: int        # qaysi userga tegishli
    due_date: date

    # SQLAlchemy model → Pydantic model konvertatsiya
    model_config = {
        "from_attributes": True
    }