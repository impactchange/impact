# --- schemas/task.py ---
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Task(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    phase: str
    category: str
    status: str = "pending"
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    priority: str = "medium"
    notes: Optional[str] = None
    dependencies: List[str] = []
    completion_criteria: Optional[str] = None
