from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.observability import (
    CorrelationIdMiddleware,
    get_logger,
    setup_logging,
    setup_metrics,
)

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Notification Service",
    description="Сервис уведомлений проекта DevForge",
    version="1.0.0",
)

app.add_middleware(CorrelationIdMiddleware)
setup_metrics(app)


@app.get("/")
def root():
    logger.info("health_check")
    return {
        "message": "Notification Service API",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/notifications/users/{user_id}", response_model=List[schemas.Notification])
def GetAllNotifications(user_id: int, db: Session = Depends(get_db)):
    """Get a list of all user notifications."""
    logger.info("get_all_notifications", user_id=user_id)
    return db.query(models.Notification).filter(models.Notification.user_id == user_id).all()


@app.get("/notifications/{notification_id}", response_model=schemas.Notification)
def GetNotification(notification_id: int, db: Session = Depends(get_db)):
    """Get a notification by Id."""
    notification = db.get(models.Notification, notification_id)
    if not notification:
        logger.warning("notification_not_found", notification_id=notification_id)
        raise HTTPException(status_code=404, detail="Task not found")
    return notification


@app.get("/notifications/{user_id}/unread", response_model=List[schemas.Notification])
def GetUnreadNotifications(user_id: int, db: Session = Depends(get_db)):
    notifications = (
        db.query(models.Notification)
        .filter(models.Notification.user_id == user_id)
        .filter(models.Notification.is_read.is_(False))
        .all()
    )
    return notifications


@app.put("/notifications/{user_id}/read-all")
def ReadAllNotifications(user_id: int, db: Session = Depends(get_db)):
    """Read all notifications."""
    notifications = (
        db.query(models.Notification)
        .filter(models.Notification.user_id == user_id)
        .filter(models.Notification.is_read.is_(False))
        .all()
    )
    for notification in notifications:
        notification.is_read = True

    db.commit()
    return {"message": "Notifications have been read"}


@app.delete("/notifications/{notification_id}")
def DeleteNotification(notification_id: int, db: Session = Depends(get_db)):
    """Delete a notification by Id."""
    notification = db.get(models.Notification, notification_id)
    if not notification:
        logger.warning("notification_not_found", notification_id=notification_id)
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(notification)
    db.commit()

    logger.info("notification_deleted", notification_id=notification_id)
    return {"message": "Task deleted successfully"}
