# backend/schemas/user.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid # Needed for UUID generation in UserRegistration logic if not in service
# ... (rest of the schema definitions, including UserRegistration, UserApprovalRequest, UserLogin, User, ProjectAssignment)

class UserRegistration(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    organization: str
    role: str

class UserApprovalRequest(BaseModel):
    user_id: str
    action: str  # approve, reject
    rejection_reason: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: str
    email: str
    full_name: str
    organization: str
    role: str
    created_at: datetime
    # Adding is_admin and is_active as they are used in admin_services and auth flows
    is_admin: bool = False
    is_active: bool = False
    status: str = "pending_approval" # Add status field for user approval
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    username: Optional[str] = None # Add username as it is part of UserRegistration and used in auth/admin
    hashed_password: Optional[str] = None # Add hashed_password for internal use in db queries


class ProjectAssignment(BaseModel):
    project_id: str
    user_id: str
    role: str  # owner, collaborator, viewer
    permissions: List[str] = []