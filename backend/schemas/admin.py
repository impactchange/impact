# --- admin_schema.py ---
from pydantic import BaseModel

class AdminDashboardStats(BaseModel):
    total_users: int
    pending_approvals: int
    active_projects: int
    total_assessments: int
    platform_usage: dict