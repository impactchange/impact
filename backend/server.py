import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
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
    user_id: Optional[str] = None
    organization: Optional[str] = None
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
    newton_analysis: Optional[Dict[str, Any]] = None
    risk_factors: Optional[List[str]] = None
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

class AdvancedAnalytics(BaseModel):
    trend_analysis: Dict[str, Any]
    newton_laws_data: Dict[str, Any]
    predictive_insights: Dict[str, Any]
    dimension_breakdown: Dict[str, Any]
    organizational_benchmarks: Dict[str, Any]

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

def calculate_newton_laws_analysis(assessment: ChangeReadinessAssessment) -> Dict[str, Any]:
    """Calculate Newton's laws analysis for organizational change"""
    scores = [
        assessment.change_management_maturity.score,
        assessment.communication_effectiveness.score,
        assessment.leadership_support.score,
        assessment.workforce_adaptability.score,
        assessment.resource_adequacy.score
    ]
    avg_score = sum(scores) / len(scores)
    
    # First Law (Inertia) - resistance to change
    organizational_inertia = (5 - avg_score) * 20  # Higher score = lower inertia
    
    # Second Law (Force) - effort required
    force_required = 100 - (avg_score * 15)  # Higher readiness = less force needed
    acceleration_potential = avg_score * 20  # How fast change can happen
    
    # Third Law (Action-Reaction) - expected resistance
    resistance_magnitude = organizational_inertia * 0.8
    
    return {
        "inertia": {
            "value": round(organizational_inertia, 1),
            "interpretation": "Low" if organizational_inertia < 40 else "Medium" if organizational_inertia < 70 else "High",
            "description": f"Organization shows {'low' if organizational_inertia < 40 else 'medium' if organizational_inertia < 70 else 'high'} resistance to change"
        },
        "force": {
            "required": round(force_required, 1),
            "acceleration": round(acceleration_potential, 1),
            "description": f"{'Low' if force_required < 50 else 'Medium' if force_required < 75 else 'High'} effort required for successful change"
        },
        "reaction": {
            "resistance": round(resistance_magnitude, 1),
            "description": f"Expect {'minimal' if resistance_magnitude < 30 else 'moderate' if resistance_magnitude < 60 else 'significant'} organizational pushback"
        }
    }

async def get_enhanced_ai_analysis(assessment: ChangeReadinessAssessment) -> dict:
    """Get enhanced AI analysis from Claude with structured insights"""
    try:
        # Create AI chat instance
        chat = LlmChat(
            api_key=ANTHROPIC_API_KEY,
            session_id=f"enhanced_assessment_{assessment.id}",
            system_message="""You are an expert organizational change management consultant specializing in the IMPACT Methodology and Newton's laws of motion applied to organizational change. 

            Provide comprehensive analysis using these principles:
            - First Law (Inertia): Organizations at rest tend to stay at rest
            - Second Law (Force): Change acceleration = Force applied / Organizational mass (resistance)
            - Third Law (Action-Reaction): Every change action produces equal opposite resistance

            Structure your response as detailed but actionable insights."""
        ).with_model("anthropic", "claude-sonnet-4-20250514")

        # Calculate Newton's laws data
        newton_data = calculate_newton_laws_analysis(assessment)

        # Create enhanced analysis prompt
        prompt = f"""
        Analyze this comprehensive organizational change readiness assessment for {assessment.project_name}:

        ASSESSMENT SCORES (1-5 scale):
        • Change Management Maturity: {assessment.change_management_maturity.score}/5 - {assessment.change_management_maturity.notes or 'No notes'}
        • Communication Effectiveness: {assessment.communication_effectiveness.score}/5 - {assessment.communication_effectiveness.notes or 'No notes'}
        • Leadership Support: {assessment.leadership_support.score}/5 - {assessment.leadership_support.notes or 'No notes'}
        • Workforce Adaptability: {assessment.workforce_adaptability.score}/5 - {assessment.workforce_adaptability.notes or 'No notes'}
        • Resource Adequacy: {assessment.resource_adequacy.score}/5 - {assessment.resource_adequacy.notes or 'No notes'}

        NEWTON'S LAWS ANALYSIS:
        • Organizational Inertia: {newton_data['inertia']['value']} ({newton_data['inertia']['interpretation']})
        • Force Required: {newton_data['force']['required']} units
        • Expected Resistance: {newton_data['reaction']['resistance']} units

        Please provide:

        1. EXECUTIVE SUMMARY (2-3 sentences)
        A concise overview of the organization's change readiness and key findings.

        2. NEWTON'S LAWS INSIGHTS
        - How organizational inertia affects this change initiative
        - Force and acceleration recommendations
        - Expected resistance patterns and mitigation

        3. STRATEGIC RECOMMENDATIONS (5 specific actions)
        Prioritized, actionable recommendations with expected impact.

        4. RISK ANALYSIS (3-4 key risks)
        Primary risks with specific mitigation strategies.

        5. SUCCESS STRATEGIES
        Proven approaches for this specific readiness profile.

        Keep responses practical, science-based, and immediately actionable.
        """

        # Get AI response
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Calculate success probability based on scores and Newton's analysis
        scores = [
            assessment.change_management_maturity.score,
            assessment.communication_effectiveness.score,
            assessment.leadership_support.score,
            assessment.workforce_adaptability.score,
            assessment.resource_adequacy.score
        ]
        avg_score = sum(scores) / len(scores)
        
        # Adjust success probability based on Newton's laws
        base_probability = (avg_score / 5) * 100
        inertia_adjustment = (100 - newton_data['inertia']['value']) * 0.2
        success_probability = min(95, base_probability + inertia_adjustment)
        
        # Generate structured recommendations
        recommendations = [
            f"Address organizational inertia through {['communication', 'leadership alignment', 'gradual implementation'][int(newton_data['inertia']['value']) // 25]}",
            f"Apply {['minimal', 'moderate', 'significant'][int(newton_data['force']['required']) // 35]} change force through structured approach",
            f"Prepare for {['low', 'medium', 'high'][int(newton_data['reaction']['resistance']) // 30]} resistance with specific mitigation plans",
            "Leverage high-scoring dimensions to accelerate change adoption",
            "Focus immediate efforts on lowest-scoring assessment areas"
        ]
        
        # Identify risk factors based on low scores
        risk_factors = []
        if assessment.change_management_maturity.score <= 2:
            risk_factors.append("Immature change management processes")
        if assessment.communication_effectiveness.score <= 2:
            risk_factors.append("Poor communication infrastructure")
        if assessment.leadership_support.score <= 2:
            risk_factors.append("Lack of leadership commitment")
        if assessment.workforce_adaptability.score <= 2:
            risk_factors.append("Workforce resistance to new ways of working")
        if assessment.resource_adequacy.score <= 2:
            risk_factors.append("Insufficient resources for change initiative")
        
        if not risk_factors:
            risk_factors = ["Overconfidence due to high scores", "Maintaining momentum during implementation"]
        
        return {
            "analysis": response,
            "recommendations": recommendations,
            "success_probability": round(success_probability, 1),
            "newton_analysis": newton_data,
            "risk_factors": risk_factors,
            "insights": {
                "strongest_dimension": max([(d, s) for d, s in [
                    ("Change Management Maturity", assessment.change_management_maturity.score),
                    ("Communication Effectiveness", assessment.communication_effectiveness.score),
                    ("Leadership Support", assessment.leadership_support.score),
                    ("Workforce Adaptability", assessment.workforce_adaptability.score),
                    ("Resource Adequacy", assessment.resource_adequacy.score)
                ]], key=lambda x: x[1]),
                "weakest_dimension": min([(d, s) for d, s in [
                    ("Change Management Maturity", assessment.change_management_maturity.score),
                    ("Communication Effectiveness", assessment.communication_effectiveness.score),
                    ("Leadership Support", assessment.leadership_support.score),
                    ("Workforce Adaptability", assessment.workforce_adaptability.score),
                    ("Resource Adequacy", assessment.resource_adequacy.score)
                ]], key=lambda x: x[1]),
                "improvement_potential": round((5 - avg_score) * 20, 1)
            }
        }
    
    except Exception as e:
        print(f"Enhanced AI Analysis Error: {str(e)}")
        # Fallback analysis with Newton's laws calculation
        newton_data = calculate_newton_laws_analysis(assessment)
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
            "analysis": f"Comprehensive assessment analysis: Overall readiness score of {avg_score:.1f}/5 indicates {'strong' if avg_score >= 4 else 'moderate' if avg_score >= 3 else 'developing'} organizational change readiness. Newton's laws analysis shows {newton_data['inertia']['interpretation'].lower()} organizational inertia requiring {newton_data['force']['required']:.0f} units of change force.",
            "recommendations": [
                "Strengthen change management processes and capabilities",
                "Improve communication strategies and channels",
                "Secure stronger leadership commitment and sponsorship",
                "Enhance workforce adaptability through training",
                "Ensure adequate resource allocation for success"
            ],
            "success_probability": round(success_probability, 1),
            "newton_analysis": newton_data,
            "risk_factors": ["Change resistance", "Resource constraints", "Communication gaps"],
            "insights": {
                "strongest_dimension": ("Overall Assessment", avg_score),
                "weakest_dimension": ("Areas for Improvement", 5 - avg_score),
                "improvement_potential": round((5 - avg_score) * 20, 1)
            }
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
        
        # Get enhanced AI analysis
        ai_result = await get_enhanced_ai_analysis(assessment)
        assessment.ai_analysis = ai_result.get("analysis", "")
        assessment.recommendations = ai_result.get("recommendations", [])
        assessment.success_probability = ai_result.get("success_probability", 0.0)
        assessment.newton_analysis = ai_result.get("newton_analysis", {})
        assessment.risk_factors = ai_result.get("risk_factors", [])
        
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

@app.get("/api/analytics/advanced")
async def get_advanced_analytics(current_user: User = Depends(get_current_user)):
    try:
        # Get all assessments for the organization
        assessments = await db.assessments.find({"organization": current_user.organization}).to_list(100)
        
        if not assessments:
            return {
                "trend_analysis": {"message": "No data available for trend analysis"},
                "newton_laws_data": {"message": "No assessments to analyze"},
                "predictive_insights": {"message": "Insufficient data for predictions"},
                "dimension_breakdown": {"message": "No dimension data available"},
                "organizational_benchmarks": {"message": "No benchmark data available"}
            }
        
        # Trend Analysis
        trend_data = []
        for assessment in sorted(assessments, key=lambda x: x.get('created_at', datetime.utcnow())):
            trend_data.append({
                "date": assessment.get('created_at', datetime.utcnow()).isoformat(),
                "overall_score": assessment.get('overall_score', 0),
                "success_probability": assessment.get('success_probability', 0),
                "project_name": assessment.get('project_name', 'Unknown')
            })
        
        # Newton's Laws Aggregate Data
        total_inertia = 0
        total_force = 0
        total_resistance = 0
        newton_count = 0
        
        for assessment in assessments:
            newton_data = assessment.get('newton_analysis', {})
            if newton_data:
                total_inertia += newton_data.get('inertia', {}).get('value', 0)
                total_force += newton_data.get('force', {}).get('required', 0)
                total_resistance += newton_data.get('reaction', {}).get('resistance', 0)
                newton_count += 1
        
        avg_newton_data = {
            "average_inertia": round(total_inertia / newton_count, 1) if newton_count > 0 else 0,
            "average_force_required": round(total_force / newton_count, 1) if newton_count > 0 else 0,
            "average_resistance": round(total_resistance / newton_count, 1) if newton_count > 0 else 0,
            "assessments_count": newton_count
        }
        
        # Dimension Breakdown
        dimensions = {
            "change_management_maturity": [],
            "communication_effectiveness": [],
            "leadership_support": [],
            "workforce_adaptability": [],
            "resource_adequacy": []
        }
        
        for assessment in assessments:
            dimensions["change_management_maturity"].append(assessment.get('change_management_maturity', {}).get('score', 0))
            dimensions["communication_effectiveness"].append(assessment.get('communication_effectiveness', {}).get('score', 0))
            dimensions["leadership_support"].append(assessment.get('leadership_support', {}).get('score', 0))
            dimensions["workforce_adaptability"].append(assessment.get('workforce_adaptability', {}).get('score', 0))
            dimensions["resource_adequacy"].append(assessment.get('resource_adequacy', {}).get('score', 0))
        
        dimension_averages = {
            dim: round(sum(scores) / len(scores), 2) if scores else 0
            for dim, scores in dimensions.items()
        }
        
        # Predictive Insights
        recent_assessments = sorted(assessments, key=lambda x: x.get('created_at', datetime.utcnow()))[-5:]
        avg_recent_score = sum(a.get('overall_score', 0) for a in recent_assessments) / len(recent_assessments) if recent_assessments else 0
        
        predictive_insights = {
            "trajectory": "improving" if len(assessments) > 1 and assessments[-1].get('overall_score', 0) > assessments[0].get('overall_score', 0) else "stable",
            "predicted_next_score": min(5.0, avg_recent_score + 0.2),
            "confidence_level": min(95, len(assessments) * 10),
            "recommendations": [
                "Continue focus on lowest-scoring dimensions",
                "Maintain momentum in high-performing areas",
                "Consider advanced change management training",
                "Implement regular assessment cycles"
            ]
        }
        
        # Organizational Benchmarks
        org_benchmarks = {
            "industry_comparison": {
                "your_average": round(sum(a.get('overall_score', 0) for a in assessments) / len(assessments), 2),
                "industry_average": 3.2,  # Simulated benchmark
                "top_quartile": 4.1,
                "performance_percentile": min(95, max(5, (sum(a.get('overall_score', 0) for a in assessments) / len(assessments)) * 25))
            },
            "maturity_level": "Developing" if avg_recent_score < 3 else "Proficient" if avg_recent_score < 4 else "Advanced",
            "areas_of_strength": [dim for dim, avg in dimension_averages.items() if avg >= 4],
            "improvement_opportunities": [dim for dim, avg in dimension_averages.items() if avg < 3]
        }
        
        return {
            "trend_analysis": {
                "data": trend_data,
                "summary": f"Analyzed {len(assessments)} assessments showing {predictive_insights['trajectory']} trend"
            },
            "newton_laws_data": avg_newton_data,
            "predictive_insights": predictive_insights,
            "dimension_breakdown": dimension_averages,
            "organizational_benchmarks": org_benchmarks
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve advanced analytics: {str(e)}")

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