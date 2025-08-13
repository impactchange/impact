# backend/routers/auth.py
import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.mongo import db
from schemas.user import UserRegistration, UserLogin, User
from core.security import hash_password, verify_password, create_access_token, get_current_user
from services.user_management_utils import create_admin_notification, log_user_activity
from datetime import datetime
import jwt
from core.config import SECRET_KEY

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegistration):
    """Register a new user with admin approval required"""
    try:
        existing_user = await db.users.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        existing_username = await db.users.find_one({"username": user.username})
        if existing_username:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

        hashed_password = hash_password(user.password)

        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "username": user.username,
            "email": user.email,
            "hashed_password": hashed_password,
            "full_name": user.full_name,
            "organization": user.organization,
            "role": user.role,
            "status": "pending_approval",
            "created_at": datetime.utcnow(),
            "approved_at": None,
            "approved_by": None,
            "rejection_reason": None,
            "is_admin": False,
            "is_active": False
        }

        await db.users.insert_one(user_data)

        await create_admin_notification(
            "user_registration",
            f"New user registration: {user.full_name} ({user.email})",
            {"user_id": user_id, "user_email": user.email, "user_name": user.full_name}
        )

        return {
            "message": "Registration submitted successfully. Your account is pending admin approval.",
            "user_id": user_id,
            "status": "pending_approval"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Registration failed: {str(e)}")

@router.post("/login")
async def login_user(user_credentials: UserLogin):
    """Login user with approval status check"""
    try:
        user_data = await db.users.find_one({"email": user_credentials.email})
        if not user_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if user_data.get("status") != "approved":
            status_message = user_data.get("status", "pending_approval")
            if status_message == "pending_approval":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account pending admin approval")
            elif status_message == "rejected":
                rejection_reason = user_data.get("rejection_reason", "No reason provided")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Account rejected: {rejection_reason}")
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account not approved")

        if not verify_password(user_credentials.password, user_data["hashed_password"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        access_token = create_access_token(data={"sub": user_data["email"], "user_id": user_data["id"]})

        await log_user_activity(
            user_data["id"],
            "login",
            f"User {user_data['full_name']} logged in successfully"
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": User(**user_data)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Login failed: {str(e)}")

@router.get("/me", response_model=User)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user
