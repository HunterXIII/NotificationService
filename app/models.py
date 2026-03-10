from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Notification(Base):

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=True)
    is_read =  Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    class Config:
        orm_mode = True 