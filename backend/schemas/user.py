from pydantic import BaseModel
from typing import Optional

class UserRegistration(BaseModel):
    email: str
    username: str
    password: str
    full_name: Optional[str]
    organization: Optional[str]
    role: Optional[str] = "member"

class UserLogin(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: Optional[str]
    email: str
    username: str
    full_name: Optional[str]
    organization: Optional[str]
    role: Optional[str]
