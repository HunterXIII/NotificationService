import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from config import settings 
import worker  # Импортируем сам модуль, чтобы пропатчить его переменную

# 1. Настройка тестовой БД (SQLite в файле)
TEST_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Создаем таблицы в тестовой базе перед началом тестов
    Base.metadata.create_all(bind=engine)
    
    # Тот самый патч: подменяем SessionLocal в файле worker.py на нашу тестовую
    with patch("worker.SessionLocal", TestingSessionLocal):
        yield
    
    # После завершения всех тестов удаляем тестовую базу (опционально)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session", autouse=True)
def mock_settings():
    """Переопределяем настройки для всех тестов."""
    with patch.object(settings, 'RABBITMQ_USER', 'devforge'), \
         patch.object(settings, 'RABBITMQ_PASSWORD', 'devforge'), \
         patch.object(settings, 'RABBITMQ_HOST', '127.0.0.1'):
        yield