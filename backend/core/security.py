# backend/core/security.py
from datetime import datetime, timedelta, timezone 
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import ValidationError 
from db.mongo import db
from schemas.user import User 
from core.config import SECRET_KEY

# --- Configuration ---
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Password Utilities ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    return pwd_context.hash(password)

# --- JWT Token Utilities ---
def create_access_token(data: dict) -> str:
    """Creates a JWT access token."""
    to_encode = data.copy()
    # Use timezone-aware datetime for expiration
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- User Authentication & Authorization Dependency ---
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    A FastAPI dependency to get the current user from a JWT token.
    Decodes JWT token, fetches user from DB using user_id, and validates.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # REFACATORING: Use 'sub' to hold the unique user ID
        user_id: str = payload.get("sub") 
        
        if user_id is None: # Check for the user ID
            raise credentials_exception
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError: 
        raise credentials_exception

    # REFACATORING: Fetch user from database using ID instead of email
    user_data = await db.users.find_one({"id": user_id})

    if user_data is None:
        raise credentials_exception

    # Exclude hashed_password before validating with Pydantic User model
    try:
        # Create a dictionary excluding the password for validation
        user_dict_for_validation = {
            key: value for key, value in user_data.items() if key != "hashed_password"
        }
        # Validate using the User schema
        user = User(**user_dict_for_validation)
    except ValidationError as e:
        print(f"Pydantic Validation Error in get_current_user: {e}") # Log error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing user data."
        )

    # Check if user is active (using the validated Pydantic model)
    if not user.is_active:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    return user
