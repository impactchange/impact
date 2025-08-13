import uuid
from datetime import datetime
from typing import List, Optional

# This file will need access to your asynchronous database client (db)
# from ..database import db # Example: adjust import path as needed


async def create_admin_notification(db, notification_type: str, message: str, data: dict):
    """Creates a notification for admin users in the database."""
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


async def log_user_activity(db, user_id: str, action: str, details: str, project_id: Optional[str] = None, affected_users: Optional[List[str]] = None):
    """Logs a user's activity for tracking and notification purposes."""
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