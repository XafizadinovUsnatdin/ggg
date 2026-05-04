# SQLAlchemy bilan DB ulanish uchun kerak
from sqlalchemy import create_engine
# Session va Base yaratish uchun
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL ="postgresql+psycopg://postgres:usnat@localhost:5432/fastapi_db"


'''
# Engine = DB bilan real connection
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  
    # SQLite uchun kerak (thread muammo bo‘lmasligi uchun)
)
'''


engine = create_engine(DATABASE_URL)


# Session — DB bilan gaplashish uchun object
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)





# Base — barcha model classlar shu orqali yaratiladi
Base = declarative_base()


# Har bir request uchun DB ulanish beradi
def get_db():
    db = SessionLocal()   # DB connection ochildi
    try:
        yield db          # endpointga beriladi
    finally:
        db.close()        # request tugagach yopiladi