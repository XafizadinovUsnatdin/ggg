# vaqt bilan ishlash uchun (token expire vaqtini hisoblash)
from datetime import datetime, timedelta, timezone

# JWT token yaratish va kodlash uchun kutubxona
from jose import jwt

# passwordni xavfsiz hash qilish uchun
from passlib.context import CryptContext


# ========================
# CONFIG (XAVFSIZLIK)
# ========================

# SECRET_KEY — tokenni shifrlash uchun maxfiy kalit
# ❗ productionda .env faylga chiqariladi
SECRET_KEY = "super-secret-key"

# JWT algoritmi (HS256 — eng keng ishlatiladigan)
ALGORITHM = "HS256"

# Token qancha vaqt amal qiladi (30 minut)
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ========================
# PASSWORD HASH CONFIG
# ========================

# bcrypt algoritmi orqali password hash qilamiz
pwd_context = CryptContext(
    schemes=["bcrypt"],     # bcrypt ishlatiladiuuy
    deprecated="auto"
)


# ========================
# PASSWORD HASH QILISH
# ========================

def hash_password(password: str):
    """
    Oddiy passwordni hash qilib beradi
    """
    # masalan: "1234" → "$2b$12$abcxyz..."
    return pwd_context.hash(password)


# ========================
# PASSWORD TEKSHIRISH
# ========================

def verify_password(plain_password: str, hashed_password: str):
    """
    Login paytida passwordni tekshiradi
    """
    # plain_password = foydalanuvchi kiritgan
    # hashed_password = DB da saqlangan

    # True yoki False qaytaradi
    return pwd_context.verify(plain_password, hashed_password)


# ========================
# JWT TOKEN YARATISH
# ========================

def create_access_token(data: dict):
    """
    JWT token yaratadi
    """

    # data dictni copy qilamiz (originalni o‘zgartirmaslik uchun)
    to_encode = data.copy()

    # token expire vaqtini hisoblaymiz
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # payload ichiga expire vaqt qo‘shamiz
    to_encode.update({"exp": expire})

    # JWT token yaratamiz:
    # payload + SECRET_KEY + ALGORITHM
    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    # tayyor tokenni qaytaramiz
    return token