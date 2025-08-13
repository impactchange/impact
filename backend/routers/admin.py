# backend/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List, Dict, Any
from schemas.user import User, UserApprovalRequest, ProjectAssignment
from services.admin_services import (
    get_admin_user, 
    get_admin_dashboard_metrics,
    get_all_users_data,
    approve_or_reject_user_registration,
    assign_user_to_project_logic,
    get_project_assignments_data,
    get_assigned_projects_for_user,
    get_project_activities_data
)
from core.security import get_current_user

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/dashboard")
async def get_admin_dashboard(admin_user: User = Depends(get_admin_user)):
    """Get admin dashboard statistics"""
    return await get_admin_dashboard_metrics()

@router.get("/users")
async def get_all_users(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    admin_user: User = Depends(get_admin_user)
):
    """Get all users with optional filtering"""
    return await get_all_users_data(status, limit, offset)

@router.post("/users/approve")
async def approve_user_registration(
    approval_request: UserApprovalRequest,
    admin_user: User = Depends(get_admin_user)
):
    """Approve or reject user registration"""
    return await approve_or_reject_user_registration(approval_request, admin_user)

@router.post("/projects/{project_id}/assign")
async def assign_user_to_project(
    project_id: str,
    assignment: ProjectAssignment,
    admin_user: User = Depends(get_admin_user)
):
    """Assign user to project with specific role"""
    return await assign_user_to_project_logic(project_id, assignment, admin_user)

@router.get("/projects/{project_id}/assignments")
async def get_project_assignments(
    project_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """Get all user assignments for a project"""
    return await get_project_assignments_data(project_id)

@router.get("/projects/assigned")
async def get_assigned_projects(current_user: User = Depends(get_current_user)):
    """Get projects assigned to current user"""
    return await get_assigned_projects_for_user(current_user)

@router.get("/projects/{project_id}/activities")
async def get_project_activities(
    project_id: str,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """Get project activities for collaboration"""
    return await get_project_activities_data(project_id, limit, offset, current_user)
