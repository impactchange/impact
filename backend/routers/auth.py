from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.mongo import db
from schemas.user import UserRegistration, UserLogin, User
from core.security import hash_password, verify_password, create_jwt_token
from datetime import datetime
import jwt
from core.config import SECRET_KEY

router = APIRouter()
security = HTTPBearer()

@router.post("/register", status_code=201)
async def register_user(user: UserRegistration):
    if await db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="User already exists")
    hashed = hash_password(user.password)
    user_doc = {
        "id": str(user.email),
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "organization": user.organization,
        "role": user.role,
        "password_hash": hashed,
        "created_at": datetime.utcnow()
    }
    await db.users.insert_one(user_doc)
    return {"message": "User registered successfully"}

@router.post("/login")
async def login_user(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_jwt_token(user_id=user["id"], email=user["email"])
    return {"access_token": token}

@router.get("/me", response_model=User)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = await db.users.find_one({"id": payload["user_id"]})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user")
        return User(**user)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
