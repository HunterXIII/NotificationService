from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Notification(BaseModel):
    """
        Full model, used for responses
        Contains all field
    """
    id: int
    user_id: int
    title: str
    content: Optional[str] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True 

    