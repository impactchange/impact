# --- activity_schema.py ---
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserActivity(BaseModel):
    user_id: str
    project_id: Optional[str] = None
    action: str
    details: str
    timestamp: datetime
    affected_users: List[str] = []