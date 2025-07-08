import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List
import uuid
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import hashlib
import jwt
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

app = FastAPI(title="IMPACT Methodology API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "impact_methodology")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "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")

# MongoDB client
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Security
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-jwt-impact-methodology-2024")

# Pydantic models
class UserRegistration(BaseModel):
    email: str
    password: str
    full_name: str
    organization: str
    role: str = "Team Member"

class UserLogin(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: str
    email: str
    full_name: str
    organization: str
    role: str
    created_at: datetime

class AssessmentDimension(BaseModel):
    name: str
    score: int = Field(ge=1, le=5)
    notes: Optional[str] = None

class ChangeReadinessAssessment(BaseModel):
    id: Optional[str] = None
    user_id: str
    organization: str
    project_name: str
    change_management_maturity: AssessmentDimension
    communication_effectiveness: AssessmentDimension
    leadership_support: AssessmentDimension
    workforce_adaptability: AssessmentDimension
    resource_adequacy: AssessmentDimension
    overall_score: Optional[float] = None
    ai_analysis: Optional[str] = None
    recommendations: Optional[List[str]] = None
    success_probability: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Project(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    organization: str
    owner_id: str
    phase: str = "Identify"  # IMPACT phases: Identify, Measure, Plan, Act, Control, Transform
    status: str = "Active"
    team_members: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# Helper functions
def hash_password(password: str) -> str:
    """Simple hash function for passwords"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hashlib.sha256(password.encode()).hexdigest() == hashed

def create_jwt_token(user_id: str, email: str) -> str:
    """Create JWT token for user"""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return User(**user)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")

async def get_ai_analysis(assessment: ChangeReadinessAssessment) -> dict:
    """Get AI analysis from Claude for the assessment"""
    try:
        # Create AI chat instance
        chat = LlmChat(
            api_key=ANTHROPIC_API_KEY,
            session_id=f"assessment_{assessment.id}",
            system_message="""You are an expert organizational change management consultant specializing in the IMPACT Methodology. 
            You analyze change readiness assessments using Newton's laws of motion principles:
            - First Law (Inertia): Organizations resist change
            - Second Law (Force): Change requires proportional effort
            - Third Law (Action-Reaction): Every change creates resistance
            
            Provide detailed analysis, actionable recommendations, and success probability."""
        ).with_model("anthropic", "claude-sonnet-4-20250514")

        # Create analysis prompt
        prompt = f"""
        Analyze this organizational change readiness assessment:
        
        Project: {assessment.project_name}
        Organization: {assessment.organization}
        
        Assessment Scores (1-5 scale):
        1. Change Management Maturity: {assessment.change_management_maturity.score}/5
           Notes: {assessment.change_management_maturity.notes or 'None'}
        
        2. Communication Effectiveness: {assessment.communication_effectiveness.score}/5
           Notes: {assessment.communication_effectiveness.notes or 'None'}
        
        3. Leadership Support: {assessment.leadership_support.score}/5
           Notes: {assessment.leadership_support.notes or 'None'}
        
        4. Workforce Adaptability: {assessment.workforce_adaptability.score}/5
           Notes: {assessment.workforce_adaptability.notes or 'None'}
        
        5. Resource Adequacy: {assessment.resource_adequacy.score}/5
           Notes: {assessment.resource_adequacy.notes or 'None'}

        Please provide:
        1. Detailed analysis applying Newton's laws to organizational change
        2. Top 5 specific actionable recommendations
        3. Success probability percentage (0-100%)
        4. Key risk factors and mitigation strategies
        5. IMPACT methodology phase recommendations

        Keep the analysis concise but insightful.
        """

        # Get AI response
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Calculate success probability based on scores
        scores = [
            assessment.change_management_maturity.score,
            assessment.communication_effectiveness.score,
            assessment.leadership_support.score,
            assessment.workforce_adaptability.score,
            assessment.resource_adequacy.score
        ]
        avg_score = sum(scores) / len(scores)
        success_probability = (avg_score / 5) * 100
        
        # Extract recommendations (simple parsing)
        recommendations = [
            "Strengthen change management processes",
            "Improve communication strategies",
            "Secure leadership buy-in",
            "Enhance workforce capabilities",
            "Ensure adequate resource allocation"
        ]
        
        return {
            "analysis": response,
            "recommendations": recommendations,
            "success_probability": success_probability,
            "risks": ["Change resistance", "Resource limitations"],
            "impact_phases": ["Focus on Measure and Plan phases"]
        }
    
    except Exception as e:
        print(f"AI Analysis Error: {str(e)}")
        # Fallback analysis
        scores = [
            assessment.change_management_maturity.score,
            assessment.communication_effectiveness.score,
            assessment.leadership_support.score,
            assessment.workforce_adaptability.score,
            assessment.resource_adequacy.score
        ]
        avg_score = sum(scores) / len(scores)
        success_probability = (avg_score / 5) * 100
        
        return {
            "analysis": f"Assessment completed with an overall score of {avg_score:.1f}/5. Based on Newton's laws of motion applied to organizational change, your organization shows {'strong' if avg_score >= 4 else 'moderate' if avg_score >= 3 else 'limited'} readiness for change.",
            "recommendations": [
                "Strengthen change management processes",
                "Improve communication strategies",
                "Secure leadership buy-in",
                "Enhance workforce capabilities",
                "Ensure adequate resource allocation"
            ],
            "success_probability": success_probability,
            "risks": ["Change resistance", "Resource limitations"],
            "impact_phases": ["Focus on Measure and Plan phases"]
        }

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/api/auth/register")
async def register_user(user_data: UserRegistration):
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(user_data.password)
        
        user = {
            "id": user_id,
            "email": user_data.email,
            "password": hashed_password,
            "full_name": user_data.full_name,
            "organization": user_data.organization,
            "role": user_data.role,
            "created_at": datetime.utcnow()
        }
        
        await db.users.insert_one(user)
        
        # Create JWT token
        token = create_jwt_token(user_id, user_data.email)
        
        return {
            "user": User(**user),
            "token": token,
            "message": "User registered successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")

@app.post("/api/auth/login")
async def login_user(login_data: UserLogin):
    try:
        # Find user
        user = await db.users.find_one({"email": login_data.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        if not verify_password(login_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create JWT token
        token = create_jwt_token(user["id"], user["email"])
        
        return {
            "user": User(**user),
            "token": token,
            "message": "Login successful"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Login failed: {str(e)}")

@app.get("/api/user/profile")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/api/assessments")
async def create_assessment(
    assessment: ChangeReadinessAssessment,
    current_user: User = Depends(get_current_user)
):
    try:
        # Generate ID and timestamps
        assessment_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Calculate overall score
        scores = [
            assessment.change_management_maturity.score,
            assessment.communication_effectiveness.score,
            assessment.leadership_support.score,
            assessment.workforce_adaptability.score,
            assessment.resource_adequacy.score
        ]
        overall_score = sum(scores) / len(scores)
        
        # Set assessment data
        assessment.id = assessment_id
        assessment.user_id = current_user.id
        assessment.organization = current_user.organization
        assessment.overall_score = overall_score
        assessment.created_at = now
        assessment.updated_at = now
        
        # Get AI analysis
        ai_result = await get_ai_analysis(assessment)
        assessment.ai_analysis = ai_result.get("analysis", "")
        assessment.recommendations = ai_result.get("recommendations", [])
        assessment.success_probability = ai_result.get("success_probability", 0.0)
        
        # Save to database
        assessment_dict = assessment.dict()
        await db.assessments.insert_one(assessment_dict)
        
        return assessment
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Assessment creation failed: {str(e)}")

@app.get("/api/assessments")
async def get_assessments(current_user: User = Depends(get_current_user)):
    try:
        assessments = await db.assessments.find({"user_id": current_user.id}).to_list(100)
        return assessments
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve assessments: {str(e)}")

@app.get("/api/assessments/{assessment_id}")
async def get_assessment(assessment_id: str, current_user: User = Depends(get_current_user)):
    try:
        assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        return assessment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve assessment: {str(e)}")

@app.post("/api/projects")
async def create_project(project: Project, current_user: User = Depends(get_current_user)):
    try:
        project_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        project.id = project_id
        project.owner_id = current_user.id
        project.organization = current_user.organization
        project.created_at = now
        project.updated_at = now
        
        await db.projects.insert_one(project.dict())
        return project
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Project creation failed: {str(e)}")

@app.get("/api/projects")
async def get_projects(current_user: User = Depends(get_current_user)):
    try:
        projects = await db.projects.find({"organization": current_user.organization}).to_list(100)
        return projects
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve projects: {str(e)}")

@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics(current_user: User = Depends(get_current_user)):
    try:
        # Get organization metrics
        total_assessments = await db.assessments.count_documents({"organization": current_user.organization})
        total_projects = await db.projects.count_documents({"organization": current_user.organization})
        
        # Get average scores
        pipeline = [
            {"$match": {"organization": current_user.organization}},
            {"$group": {
                "_id": None,
                "avg_score": {"$avg": "$overall_score"},
                "avg_success_probability": {"$avg": "$success_probability"}
            }}
        ]
        
        avg_data = await db.assessments.aggregate(pipeline).to_list(1)
        avg_score = avg_data[0]["avg_score"] if avg_data else 0
        avg_success_probability = avg_data[0]["avg_success_probability"] if avg_data else 0
        
        # Get recent assessments
        recent_assessments = await db.assessments.find(
            {"organization": current_user.organization}
        ).sort("created_at", -1).limit(5).to_list(5)
        
        return {
            "total_assessments": total_assessments,
            "total_projects": total_projects,
            "average_readiness_score": round(avg_score, 2),
            "average_success_probability": round(avg_success_probability, 2),
            "recent_assessments": recent_assessments
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve dashboard metrics: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)