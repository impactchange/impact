# backend/services/admin_services.py
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import HTTPException, Depends # Keep Depends for the dependency injection in get_admin_user
from db.mongo import db
from schemas.user import User, UserApprovalRequest
from schemas.project import ProjectAssignment
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
from core.security import get_current_user # Assuming get_current_user is in core/security.py

async def get_admin_user(current_user: User = Depends(get_current_user)):
    """Dependency to check if current user is admin"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def get_admin_dashboard_metrics() -> Dict[str, Any]:
    """Get admin dashboard statistics"""
    try:
        # Get user statistics
        total_users = await db.users.count_documents({})
        pending_approvals = await db.users.count_documents({"status": "pending_approval"})
        approved_users = await db.users.count_documents({"status": "approved"})
        rejected_users = await db.users.count_documents({"status": "rejected"})

        # Get project statistics
        active_projects = await db.projects.count_documents({"status": "active"})
        total_projects = await db.projects.count_documents({})

        # Get assessment statistics
        total_assessments = await db.assessments.count_documents({})

        # Get recent activities
        recent_activities = []
        activities_cursor = db.user_activities.find({}).sort("timestamp", -1).limit(10)
        async for activity in activities_cursor:
            activity["_id"] = str(activity["_id"])
            recent_activities.append(activity)

        # Get pending notifications
        pending_notifications = []
        notifications_cursor = db.admin_notifications.find({"resolved": False}).sort("created_at", -1).limit(5)
        async for notification in notifications_cursor:
            notification["_id"] = str(notification["_id"])
            pending_notifications.append(notification)

        # Platform usage statistics
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
        print(f"Admin Dashboard Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get admin dashboard: {str(e)}")

async def get_all_users_data(status: Optional[str] = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """Get all users with optional filtering"""
    try:
        # Build query
        query = {}
        if status:
            query["status"] = status

        # Get users with pagination
        users_cursor = db.users.find(query).skip(offset).limit(limit).sort("created_at", -1)
        users = []

        async for user in users_cursor:
            user["_id"] = str(user["_id"])
            # Remove sensitive data
            user.pop("hashed_password", None)
            users.append(user)

        # Get total count
        total_count = await db.users.count_documents(query)

        return {
            "users": users,
            "total_count": total_count,
            "offset": offset,
            "limit": limit,
            "has_more": offset + limit < total_count
        }

    except Exception as e:
        print(f"Get Users Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")

async def approve_or_reject_user_registration(approval_request: UserApprovalRequest, admin_user: User) -> Dict[str, Any]:
    """Approve or reject user registration"""
    try:
        # Get user
        user = await db.users.find_one({"id": approval_request.user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update user status
        update_data = {
            "status": "approved" if approval_request.action == "approve" else "rejected",
            "approved_at": datetime.utcnow(),
            "approved_by": admin_user.id,
            "is_active": approval_request.action == "approve"
        }

        if approval_request.action == "reject" and approval_request.rejection_reason:
            update_data["rejection_reason"] = approval_request.rejection_reason

        result = await db.users.update_one(
            {"id": approval_request.user_id},
            {"$set": update_data}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User not found or already processed")

        # Log admin activity
        await log_user_activity(
            admin_user.id,
            f"user_{approval_request.action}",
            f"Admin {admin_user.full_name} {approval_request.action}d user {user['full_name']} ({user['email']})",
            affected_users=[approval_request.user_id]
        )

        # Mark notification as resolved
        await db.admin_notifications.update_one(
            {"data.user_id": approval_request.user_id, "type": "user_registration"},
            {"$set": {"resolved": True, "resolved_at": datetime.utcnow(), "resolved_by": admin_user.id}}
        )

        return {
            "message": f"User {approval_request.action}d successfully",
            "user_id": approval_request.user_id,
            "action": approval_request.action,
            "processed_by": admin_user.full_name,
            "processed_at": datetime.utcnow()
        }

    except Exception as e:
        print(f"User Approval Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process user approval: {str(e)}")

async def assign_user_to_project_logic(project_id: str, assignment: ProjectAssignment, admin_user: User) -> Dict[str, Any]:
    """Assign user to project with specific role"""
    try:
        # Get project
        project = await db.projects.find_one({"id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get user
        user = await db.users.find_one({"id": assignment.user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if user is already assigned
        current_assignments = project.get("assigned_users", [])
        existing_assignment = next((a for a in current_assignments if a["user_id"] == assignment.user_id), None)

        if existing_assignment:
            # Update existing assignment
            existing_assignment.update({
                "role": assignment.role,
                "permissions": assignment.permissions,
                "assigned_at": datetime.utcnow(),
                "assigned_by": admin_user.id
            })
        else:
            # Add new assignment
            new_assignment = {
                "user_id": assignment.user_id,
                "user_name": user["full_name"],
                "user_email": user["email"],
                "role": assignment.role,
                "permissions": assignment.permissions,
                "assigned_at": datetime.utcnow(),
                "assigned_by": admin_user.id
            }
            current_assignments.append(new_assignment)

        # Update project
        result = await db.projects.update_one(
            {"id": project_id},
            {"$set": {"assigned_users": current_assignments, "updated_at": datetime.utcnow()}}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Project not found")

        # Log admin activity
        await log_user_activity(
            admin_user.id,
            "project_assignment",
            f"Admin {admin_user.full_name} assigned {user['full_name']} to project {project['project_name']} as {assignment.role}",
            project_id=project_id,
            affected_users=[assignment.user_id]
        )

        # Create notification for assigned user
        await create_user_notification(
            assignment.user_id,
            "project_assignment",
            f"You have been assigned to project: {project['project_name']}",
            {"project_id": project_id, "role": assignment.role}
        )

        return {
            "message": "User assigned to project successfully",
            "project_id": project_id,
            "user_id": assignment.user_id,
            "role": assignment.role,
            "assigned_by": admin_user.full_name,
            "assigned_at": datetime.utcnow()
        }

    except Exception as e:
        print(f"Project Assignment Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to assign user to project: {str(e)}")

async def get_project_assignments_data(project_id: str) -> Dict[str, Any]:
    """Get all user assignments for a project"""
    try:
        # Get project
        project = await db.projects.find_one({"id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        assignments = project.get("assigned_users", [])

        # Enrich assignments with current user data
        enriched_assignments = []
        for assignment in assignments:
            user = await db.users.find_one({"id": assignment["user_id"]})
            if user:
                enriched_assignment = {
                    **assignment,
                    "user_current_status": user.get("status", "unknown"),
                    "user_last_active": user.get("last_active", None)
                }
                enriched_assignments.append(enriched_assignment)

        return {
            "project_id": project_id,
            "project_name": project.get("project_name", ""),
            "assignments": enriched_assignments,
            "total_assignments": len(enriched_assignments)
        }

    except Exception as e:
        print(f"Get Project Assignments Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get project assignments: {str(e)}")

async def get_assigned_projects_for_user(current_user: User) -> Dict[str, Any]:
    """Get projects assigned to current user"""
    try:
        # Find projects where user is assigned
        projects_cursor = db.projects.find({
            "assigned_users.user_id": current_user.id
        }).sort("created_at", -1)

        assigned_projects = []
        async for project in projects_cursor:
            project["_id"] = str(project["_id"])

            # Get user's role in this project
            user_assignment = next(
                (a for a in project.get("assigned_users", []) if a["user_id"] == current_user.id),
                None
            )

            if user_assignment:
                project["user_role"] = user_assignment["role"]
                project["user_permissions"] = user_assignment.get("permissions", [])
                project["assigned_at"] = user_assignment.get("assigned_at")

                assigned_projects.append(project)

        return {
            "assigned_projects": assigned_projects,
            "total_count": len(assigned_projects)
        }

    except Exception as e:
        print(f"Get Assigned Projects Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get assigned projects: {str(e)}")

async def get_project_activities_data(project_id: str, limit: int = 20, offset: int = 0, current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """Get project activities for collaboration"""
    try:
        # Check if user has access to this project
        project = await db.projects.find_one({"id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Check if user is owner or assigned to project
        is_owner = project.get("user_id") == current_user.id
        is_assigned = any(a["user_id"] == current_user.id for a in project.get("assigned_users", []))

        if not is_owner and not is_assigned and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied")

        # Get activities for this project
        activities_cursor = db.user_activities.find({
            "project_id": project_id
        }).sort("timestamp", -1).skip(offset).limit(limit)

        activities = []
        async for activity in activities_cursor:
            activity["_id"] = str(activity["_id"])

            # Get user info for activity
            user = await db.users.find_one({"id": activity["user_id"]})
            if user:
                activity["user_name"] = user["full_name"]
                activity["user_email"] = user["email"]

            activities.append(activity)

        # Get total count
        total_count = await db.user_activities.count_documents({"project_id": project_id})

        return {
            "project_id": project_id,
            "activities": activities,
            "total_count": total_count,
            "offset": offset,
            "limit": limit,
            "has_more": offset + limit < total_count
        }

    except Exception as e:
        print(f"Get Project Activities Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get project activities: {str(e)}")