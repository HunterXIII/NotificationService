from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List
from app import schemas, models
from app.database import SessionLocal, engine, get_db
from sqlalchemy.orm import Session

app = FastAPI(
    title="Notification Service",
    description="Сервис уведомлений проекта DevForge",
    version="1.0.0"
)


@app.get("/")
def root():
    
    return {
        "message": "Notification Service API",
        "status": "running",
        "docs": "/docs"
    }

# Routes
@app.get("/notifications/users/{user_id}", response_model=List[schemas.Notification])
def GetAllNotifications(user_id: int, db: Session = Depends(get_db)):
    """
        Get a list of all user notifications
    """
    return db.query(models.Notification).filter(models.Notification.user_id == user_id)

@app.get("/notifications/{notification_id}", response_model=schemas.Notification)
def GetNotification(notification_id: int, db: Session = Depends(get_db)):
    """
        Get a notification by Id
    """
    notification = db.get(models.Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Task not found")
    return notification

@app.get("/notifications/{user_id}/unread", response_model=List[schemas.Notification])
def GetUnreadNotifications(user_id: int, db: Session = Depends(get_db)):
    notifications = db.query(models.Notification)\
        .filter(models.Notification.user_id == user_id)\
        .filter(models.Notification.is_read == False)\
        .all()
    return notifications

@app.put("/notifications/{user_id}/read-all")
def ReadAllNotifications(user_id: int, db: Session = Depends(get_db)):
    """
        Read all notifications
    """
    notifications = db.query(models.Notification)\
        .filter(models.Notification.user_id == user_id)\
        .filter(models.Notification.is_read == False)\
        .all()
    for notification in notifications:
        notification.is_read = True

    db.commit()
    return {"message": "Notifications have been read"}

@app.delete("/notifications/{notification_id}")
def DeleteNotification(notification_id: int, db: Session = Depends(get_db)):
    """
        Delete a notification by Id
    """
    notification = db.get(models.Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(notification)
    db.commit()
    
    return {"message": "Task deleted successfully"}
