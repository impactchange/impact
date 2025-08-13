# backend/services/user_management_utils.py
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from db.mongo import db # Assuming db is imported from db/mongo.py

async def create_admin_notification(notification_type: str, message: str, data: dict):
    """Create notification for admin users"""
    try:
        notification_id = str(uuid.uuid4())
        notification_data = {
            "id": notification_id,
            "type": notification_type,
            "message": message,
            "data": data,
            "created_at": datetime.utcnow(),
            "read": False,
            "resolved": False
        }

        await db.admin_notifications.insert_one(notification_data)

    except Exception as e:
        print(f"Admin notification error: {str(e)}")

async def log_user_activity(user_id: str, action: str, details: str, project_id: str = None, affected_users: List[str] = None):
    """Log user activity for tracking and notifications"""
    try:
        activity_id = str(uuid.uuid4())
        activity_data = {
            "id": activity_id,
            "user_id": user_id,
            "project_id": project_id,
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow(),
            "affected_users": affected_users or []
        }

        await db.user_activities.insert_one(activity_data)

    except Exception as e:
        print(f"Activity logging error: {str(e)}")

async def create_user_notification(user_id: str, notification_type: str, message: str, data: dict):
    """Create notification for specific user"""
    try:
        notification_id = str(uuid.uuid4())
        notification_data = {
            "id": notification_id,
            "user_id": user_id,
            "type": notification_type,
            "message": message,
            "data": data,
            "created_at": datetime.utcnow(),
            "read": False
        }

        await db.user_notifications.insert_one(notification_data)

    except Exception as e:
        print(f"User notification error: {str(e)}")

async def calculate_daily_active_users() -> int:
    """Calculate daily active users"""
    try:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        count = await db.user_activities.count_documents({
            "timestamp": {"$gte": today},
            "action": "login"
        })
        return count
    except Exception as e:
        print(f"Error calculating daily active users: {e}")
        return 0

async def calculate_weekly_active_users() -> int:
    """Calculate weekly active users"""
    try:
        week_ago = datetime.utcnow() - timedelta(days=7)
        count = await db.user_activities.count_documents({
            "timestamp": {"$gte": week_ago},
            "action": "login"
        })
        return count
    except Exception as e:
        print(f"Error calculating weekly active users: {e}")
        return 0

async def calculate_monthly_active_users() -> int:
    """Calculate monthly active users"""
    try:
        month_ago = datetime.utcnow() - timedelta(days=30)
        count = await db.user_activities.count_documents({
            "timestamp": {"$gte": month_ago},
            "action": "login"
        })
        return count
    except Exception as e:
        print(f"Error calculating monthly active users: {e}")
        return 0

async def calculate_project_completion_rate() -> float:
    """Calculate project completion rate"""
    try:
        total_projects = await db.projects.count_documents({})
        completed_projects = await db.projects.count_documents({"status": "completed"})
        return (completed_projects / total_projects * 100) if total_projects > 0 else 0
    except Exception as e:
        print(f"Error calculating project completion rate: {e}")
        return 0

async def calculate_assessment_completion_rate() -> float:
    """Calculate assessment completion rate"""
    try:
        total_assessments = await db.assessments.count_documents({})
        completed_assessments = await db.assessments.count_documents({"status": "completed"})
        return (completed_assessments / total_assessments * 100) if total_assessments > 0 else 0
    except Exception as e:
        print(f"Error calculating assessment completion rate: {e}")
        return 0