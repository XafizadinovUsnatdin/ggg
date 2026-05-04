# FastAPI dependency injection va errorlar uchun
from fastapi import Depends, HTTPException, status
#Dependency / Auth Middleware
# OAuth2 orqali Authorization headerdan token olish
from fastapi.security import OAuth2PasswordBearer

# JWT tokenni decode qilish va xatolarni ushlash
from jose import jwt, JWTError

# Database session (DB bilan ishlash uchun)
from sqlalchemy.orm import Session

# DB connection beradigan funksiya
from app.database import get_db

# CRUD orqali userni DBdan topamiz
from app import crud

# Token decode qilish uchun SECRET_KEY va ALGORITHM
from app.auth import SECRET_KEY, ALGORITHM


# OAuth2 sxema:
# Frontend yuboradi:
# Authorization: Bearer TOKEN
# FastAPI shu TOKENni avtomatik olib beradi
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ========================
# CURRENT USERNI OLISH
# ========================

def get_current_user(
    token: str = Depends(oauth2_scheme),  # 🔥 tokenni headerdan oladi
    db: Session = Depends(get_db)         # 🔥 DB connection beradi
):
    try:
        # JWT tokenni decode qilamiz
        payload = jwt.decode(
            token,
            SECRET_KEY,        # tokenni tekshirish uchun secret
            algorithms=[ALGORITHM]
        )

        # token ichidan username olamiz
        # (create_access_token da "sub" sifatida yozilgandi)
        username = payload.get("sub")

        # agar username yo‘q bo‘lsa → token noto‘g‘ri
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token noto‘g‘ri"
            )

    # agar token yaroqsiz bo‘lsa (expire, buzilgan va h.k.)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token noto‘g‘ri"
        )

    # DB dan userni topamiz
    user = crud.get_user_by_username(db, username)

    # agar user DB da bo‘lmasa
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User topilmadi"
        )

    # 🔥 hammasi OK → userni endpointga qaytaramiz
    return user