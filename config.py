import os

class Settings:
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("POSTGRES_NAME")
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
    RABBITMQ_USER = os.getenv("RABBITMQ_USER")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
    
    GOOGLE_KEY = os.getenv("GOOGLE_KEY")

settings = Settings()