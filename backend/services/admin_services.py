# backend/services/admin_services.py (INTEGRATED)

import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, Depends, status

from db.mongo import db
from schemas.user import User, UserApprovalRequest, ProjectAssignment
from schemas.project import Project, ProjectCreate, ProjectUpdate, ProjectPhase # New imports
from data.constants import IMPACT_PHASES # New import

from services.user_management_utils import (
    create_admin_notification,
    log_user_activity,
    create_user_notification,
    calculate_daily_active_users,
    calculate_weekly_active_users,
    calculate_monthly_active_users,
    calculate_project_completion_rate,
    calculate_assessment_completion_rate
)
from services.workflow_management import ( # New imports
    generate_comprehensive_tasks_for_phase,
    generate_deliverables_for_phase,
    generate_milestones_for_phase,
    calculate_project_progress,
    calculate_phase_progress
)
from core.security import get_current_user

# --- NEW PROJECT SERVICE FUNCTIONS ---

async def get_project_document(project_id: str, user_id: str) -> Dict[str, Any]:
    """Retrieves a project document by ID, ensuring user ownership/access."""
    project_doc = await db.projects.find_one({"id": project_id, "owner_id": user_id})

    if not project_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you are not authorized to view it."
        )
    project_doc.pop("_id", None)
    return project_doc

async def create_new_project_service(project_data: ProjectCreate, current_user: User) -> Project:
    """Handles logic for creating a standard new project."""
    project_id = str(uuid.uuid4())
    now = datetime.utcnow()

    existing_project = await db.projects.find_one({
        "name": project_data.name,
        "organization": current_user.organization
    })
    if existing_project:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project with this name already exists in your organization.")

    # 1. Initialization and Task Generation (investigate phase)
    initial_phases = [
        ProjectPhase(
            phase_name=phase_key,
            phase_display_name=phase_info["name"],
            phase_number=phase_info["order"]
        )
        for phase_key, phase_info in IMPACT_PHASES.items()
    ]

    initial_tasks_raw = generate_comprehensive_tasks_for_phase("investigate", project_id)
    initial_deliverables_raw = generate_deliverables_for_phase("investigate", project_id)
    initial_milestones_raw = generate_milestones_for_phase("investigate", project_id, now)

    # 2. Construct Project Document
    new_project_data = project_data.model_dump(exclude_unset=True)
    new_project_data.update({
        "id": project_id,
        "owner_id": current_user.id,
        "organization": current_user.organization,
        "current_phase": "investigate",
        "start_date": now,
        "created_at": now,
        "updated_at": now,
        "last_update": now,
        "phases": [p.model_dump() for p in initial_phases],
        "phase_progress": {phase: 0.0 for phase in IMPACT_PHASES.keys()},
        "tasks": initial_tasks_raw,
        "deliverables": initial_deliverables_raw,
        "milestones": initial_milestones_raw,
        "status": "active",
        "spent_budget": 0.0,
    })

    # 3. Final Validation and Progress Calculation
    project_instance = Project(**new_project_data)
    project_instance.progress_percentage = calculate_project_progress(project_instance.model_dump())
    
    if project_instance.phases:
        project_instance.phases[0].completion_percentage = calculate_phase_progress(project_instance.model_dump(), "investigate")

    # 4. Database Insertion
    project_doc = project_instance.model_dump()
    await db.projects.insert_one(project_doc)

    return project_instance


async def update_project_details(project_id: str, update_dict: Dict[str, Any], user_id: str) -> Project:
    """Handles updating non-nested project fields and recalculating overall progress."""
    await get_project_document(project_id, user_id) # Validates ownership

    if "estimated_end_date" in update_dict and update_dict["estimated_end_date"]:
        if isinstance(update_dict["estimated_end_date"], str):
            try:
                update_dict["estimated_end_date"] = datetime.fromisoformat(update_dict["estimated_end_date"])
            except ValueError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format for estimated_end_date")

    update_dict["updated_at"] = datetime.utcnow()
    update_dict["last_update"] = datetime.utcnow()

    # 1. Update Database
    result = await db.projects.update_one(
        {"id": project_id, "owner_id": user_id},
        {"$set": update_dict}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or no changes made")

    # 2. Re-fetch and return
    updated_project_doc = await db.projects.find_one({"id": project_id})
    if not updated_project_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Updated project not found after update operation.")

    updated_project_doc.pop("_id", None)
    return Project(**updated_project_doc)


async def create_project_from_assessment_service(project_data_from_assessment: Any, current_user: User, assessment_data: Dict[str, Any]) -> Project:
    """Handles logic for creating a project based on an existing assessment."""
    
    project_id = str(uuid.uuid4())
    now = datetime.utcnow()

    recommended_project_config = assessment_data.get("recommended_project", {})
    suggested_duration_weeks = recommended_project_config.get("suggested_duration_weeks", 16)
    target_completion = project_data_from_assessment.target_completion_date or (now + timedelta(weeks=suggested_duration_weeks))

    # 1. Initialize Phases
    initial_phases = [
        ProjectPhase(
            phase_name=phase_key,
            phase_display_name=phase_info["name"],
            phase_number=phase_info["order"]
        )
        for phase_key, phase_info in IMPACT_PHASES.items()
    ]
    
    # 2. Generate Content for ALL Phases
    all_tasks_raw = []
    all_deliverables_raw = []
    all_milestones_raw = []

    for phase_name_short in IMPACT_PHASES.keys():
        phase_tasks = generate_comprehensive_tasks_for_phase(phase_name_short, project_id)
        phase_deliverables = generate_deliverables_for_phase(phase_name_short, project_id)
        phase_milestones = generate_milestones_for_phase(phase_name_short, project_id, now)

        all_tasks_raw.extend(phase_tasks)
        all_deliverables_raw.extend(phase_deliverables)
        all_milestones_raw.extend(phase_milestones)

    # 3. Construct Project Document
    new_project_data = {
        "id": project_id,
        "name": project_data_from_assessment.project_name,
        "description": project_data_from_assessment.description,
        "organization": current_user.organization,
        "owner_id": current_user.id,
        "current_phase": "investigate",
        "status": "active",
        "start_date": now,
        "target_completion_date": target_completion,
        "budget": project_data_from_assessment.budget,
        "assessment_id": project_data_from_assessment.assessment_id,
        "newton_insights": assessment_data.get("newton_analysis", {}),
        "created_at": now,
        "updated_at": now,
        "last_update": now,
        "phases": [p.model_dump() for p in initial_phases],
        "phase_progress": {phase: 0.0 for phase in IMPACT_PHASES.keys()},
        "tasks": all_tasks_raw,
        "deliverables": all_deliverables_raw,
        "milestones": all_milestones_raw,
        "spent_budget": 0.0,
    }

    # 4. Final Validation and Progress Calculation
    project_instance = Project(**new_project_data)
    project_instance.progress_percentage = calculate_project_progress(project_instance.model_dump())
    
    for phase_name_short in IMPACT_PHASES.keys():
        progress = calculate_phase_progress(project_instance.model_dump(), phase_name_short)
        project_instance.phase_progress[phase_name_short] = progress

    # 5. Database Insertion
    project_doc = project_instance.model_dump(by_alias=False)
    await db.projects.insert_one(project_doc)

    return project_instance

# --- ORIGINAL ADMIN FUNCTIONS (BELOW) ---

async def get_admin_user(current_user: User = Depends(get_current_user)):
    """Dependency to check if current user is admin"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def get_admin_dashboard_metrics() -> Dict[str, Any]:
    """Get admin dashboard statistics"""
    try:
        total_users = await db.users.count_documents({})
        pending_approvals = await db.users.count_documents({"status": "pending_approval"})
        approved_users = await db.users.count_documents({"status": "approved"})
        rejected_users = await db.users.count_documents({"status": "rejected"})
        active_projects = await db.projects.count_documents({"status": "active"})
        total_projects = await db.projects.count_documents({})
        total_assessments = await db.assessments.count_documents({})
        recent_activities = []
        activities_cursor = db.user_activities.find({}).sort("timestamp", -1).limit(10)
        async for activity in activities_cursor:
            activity["_id"] = str(activity["_id"])
            recent_activities.append(activity)
        pending_notifications = []
        notifications_cursor = db.admin_notifications.find({"resolved": False}).sort("created_at", -1).limit(5)
        async for notification in notifications_cursor:
            notification["_id"] = str(notification["_id"])
            pending_notifications.append(notification)
        platform_usage = {
            "daily_active_users": await calculate_daily_active_users(),
            "weekly_active_users": await calculate_weekly_active_users(),
            "monthly_active_users": await calculate_monthly_active_users(),
            "project_completion_rate": await calculate_project_completion_rate(),
            "assessment_completion_rate": await calculate_assessment_completion_rate()
        }
        dashboard_stats = {
            "user_statistics": {
                "total_users": total_users,
                "pending_approvals": pending_approvals,
                "approved_users": approved_users,
                "rejected_users": rejected_users
            },
            "project_statistics": {
                "active_projects": active_projects,
                "total_projects": total_projects,
                "completion_rate": platform_usage["project_completion_rate"]
            },
            "assessment_statistics": {
                "total_assessments": total_assessments,
                "completion_rate": platform_usage["assessment_completion_rate"]
            },
            "platform_usage": platform_usage,
            "recent_activities": recent_activities,
            "pending_notifications": pending_notifications,
            "generated_at": datetime.utcnow()
        }
        return dashboard_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get admin dashboard: {str(e)}")

async def get_all_users_data(status: Optional[str] = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """Get all users with optional filtering"""
    try:
        query = {}
        if status:
            query["status"] = status
        users_cursor = db.users.find(query).skip(offset).limit(limit).sort("created_at", -1)
        users = []
        async for user in users_cursor:
            user["_id"] = str(user["_id"])
            user.pop("hashed_password", None)
            users.append(user)
        total_count = await db.users.count_documents(query)
        return {
            "users": users, "total_count": total_count, "offset": offset, "limit": limit,
            "has_more": offset + limit < total_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")

async def approve_or_reject_user_registration(approval_request: UserApprovalRequest, admin_user: User) -> Dict[str, Any]:
    """Approve or reject user registration"""
    try:
        user = await db.users.find_one({"id": approval_request.user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        update_data = {
            "status": "approved" if approval_request.action == "approve" else "rejected",
            "approved_at": datetime.utcnow(),
            "approved_by": admin_user.id,
            "is_active": approval_request.action == "approve"
        }
        if approval_request.action == "reject" and approval_request.rejection_reason:
            update_data["rejection_reason"] = approval_request.rejection_reason
        result = await db.users.update_one({"id": approval_request.user_id}, {"$set": update_data})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User not found or already processed")
        await log_user_activity(
            admin_user.id,
            f"user_{approval_request.action}",
            f"Admin {admin_user.full_name} {approval_request.action}d user {user['full_name']} ({user['email']})",
            affected_users=[approval_request.user_id]
        )
        await db.admin_notifications.update_one(
            {"data.user_id": approval_request.user_id, "type": "user_registration"},
            {"$set": {"resolved": True, "resolved_at": datetime.utcnow(), "resolved_by": admin_user.id}}
        )
        return {
            "message": f"User {approval_request.action}d successfully", "user_id": approval_request.user_id,
            "action": approval_request.action, "processed_by": admin_user.full_name,
            "processed_at": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process user approval: {str(e)}")

async def assign_user_to_project_logic(project_id: str, assignment: ProjectAssignment, admin_user: User) -> Dict[str, Any]:
    """Assign user to project with specific role"""
    try:
        project = await db.projects.find_one({"id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        user = await db.users.find_one({"id": assignment.user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        current_assignments = project.get("assigned_users", [])
        existing_assignment = next((a for a in current_assignments if a["user_id"] == assignment.user_id), None)
        if existing_assignment:
            existing_assignment.update({
                "role": assignment.role, "permissions": assignment.permissions,
                "assigned_at": datetime.utcnow(), "assigned_by": admin_user.id
            })
        else:
            new_assignment = {
                "user_id": assignment.user_id, "user_name": user["full_name"], "user_email": user["email"],
                "role": assignment.role, "permissions": assignment.permissions,
                "assigned_at": datetime.utcnow(), "assigned_by": admin_user.id
            }
            current_assignments.append(new_assignment)
        result = await db.projects.update_one(
            {"id": project_id},
            {"$set": {"assigned_users": current_assignments, "updated_at": datetime.utcnow()}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Project not found")
        await log_user_activity(
            admin_user.id, "project_assignment",
            f"Admin {admin_user.full_name} assigned {user['full_name']} to project {project.get('project_name', project.get('name'))} as {assignment.role}",
            project_id=project_id, affected_users=[assignment.user_id]
        )
        await create_user_notification(
            assignment.user_id, "project_assignment",
            f"You have been assigned to project: {project.get('project_name', project.get('name'))}",
            {"project_id": project_id, "role": assignment.role}
        )
        return {
            "message": "User assigned to project successfully", "project_id": project_id,
            "user_id": assignment.user_id, "role": assignment.role,
            "assigned_by": admin_user.full_name, "assigned_at": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assign user to project: {str(e)}")

async def get_project_assignments_data(project_id: str) -> Dict[str, Any]:
    """Get all user assignments for a project"""
    try:
        project = await db.projects.find_one({"id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        assignments = project.get("assigned_users", [])
        enriched_assignments = []
        for assignment in assignments:
            user = await db.users.find_one({"id": assignment["user_id"]})
            if user:
                enriched_assignment = {**assignment, "user_current_status": user.get("status", "unknown"), "user_last_active": user.get("last_active")}
                enriched_assignments.append(enriched_assignment)
        return {
            "project_id": project_id, "project_name": project.get("project_name", ""),
            "assignments": enriched_assignments, "total_assignments": len(enriched_assignments)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project assignments: {str(e)}")

async def get_assigned_projects_for_user(current_user: User) -> Dict[str, Any]:
    """Get projects assigned to current user"""
    try:
        projects_cursor = db.projects.find({"assigned_users.user_id": current_user.id}).sort("created_at", -1)
        assigned_projects = []
        async for project in projects_cursor:
            project["_id"] = str(project["_id"])
            user_assignment = next((a for a in project.get("assigned_users", []) if a["user_id"] == current_user.id), None)
            if user_assignment:
                project["user_role"] = user_assignment["role"]
                project["user_permissions"] = user_assignment.get("permissions", [])
                project["assigned_at"] = user_assignment.get("assigned_at")
                assigned_projects.append(project)
        return {"assigned_projects": assigned_projects, "total_count": len(assigned_projects)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get assigned projects: {str(e)}")

async def get_project_activities_data(project_id: str, limit: int = 20, offset: int = 0, current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """Get project activities for collaboration"""
    try:
        project = await db.projects.find_one({"id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        is_owner = project.get("user_id") == current_user.id
        is_assigned = any(a["user_id"] == current_user.id for a in project.get("assigned_users", []))
        if not is_owner and not is_assigned and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied")
        activities_cursor = db.user_activities.find({"project_id": project_id}).sort("timestamp", -1).skip(offset).limit(limit)
        activities = []
        async for activity in activities_cursor:
            activity["_id"] = str(activity["_id"])
            user = await db.users.find_one({"id": activity["user_id"]})
            if user:
                activity["user_name"] = user["full_name"]
                activity["user_email"] = user["email"]
            activities.append(activity)
        total_count = await db.user_activities.count_documents({"project_id": project_id})
        return {
            "project_id": project_id, "activities": activities, "total_count": total_count,
            "offset": offset, "limit": limit, "has_more": offset + limit < total_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project activities: {str(e)}")

