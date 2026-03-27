from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from config import settings
# Загружаем переменные окружения из .env
load_dotenv()

<<<<<<< HEAD
# Формируем строку подключения
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = "localhost"  
DB_PORT = "5433"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print(DATABASE_URL)
=======
# # Формируем строку подключения
# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_NAME = os.getenv("DB_NAME")
# DB_HOST = "localhost"  
# DB_PORT = "5433"

DATABASE_URL = (
    f"postgresql://{settings.DB_USER}:"
    f"{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:5432/"
    f"{settings.DB_NAME}"
)
# print(DATABASE_URL)
>>>>>>> 6447015590a82018ba540fdf7a59fd28da7fae33
# Создаём engine (двигатель) - фабрика соединений
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)  # echo=True для отладки SQL-запросов

# Создаём SessionLocal - фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Зависимость для получения сессии БД в эндпоинтах
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()