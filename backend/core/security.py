import hashlib
import jwt
from datetime import datetime, timedelta
from core.config import SECRET_KEY
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.mongo import db # Assuming db object is accessible globally or passed
from schemas.user import User
# ... (rest of the file defining functions like hash_password, verify_password, create_jwt_token, create_access_token, get_current_user)

# --- Configuration ---
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
security = HTTPBearer()

# --- Password Utilities ---

def get_password_hash(password: str) -> str:
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed one."""
    return get_password_hash(plain_password) == hashed_password

# --- JWT Token Utilities ---

def create_access_token(data: dict) -> str:
    """Creates a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- User Authentication & Authorization Dependency ---

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    A FastAPI dependency to get the current user from a JWT token.
    This should be used to protect API routes that require a logged-in user.
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_identifier = payload.get("sub") # The "sub" (subject) is standard for JWT
        if user_identifier is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Placeholder for DB logic: You will uncomment and adapt the lines below
        # user = await db.users.find_one({"email": user_identifier})
        # if user is None:
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="User not found",
        #     )
        # return User(**user)

        # Using a placeholder return until your DB logic is connected
        return {"email": user_identifier}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.PyJWTError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )