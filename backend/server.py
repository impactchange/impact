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

# Enhanced IMPACT Phases Configuration with Complete Workflows
IMPACT_PHASES = {
    "identify": {
        "name": "Identify",
        "description": "Define the change initiative and its scope",
        "order": 1,
        "newton_law": "First Law - Overcoming Organizational Inertia",
        "newton_insight": "Organizations at rest tend to stay at rest. Significant force is required to overcome initial inertia and establish change momentum.",
        "objectives": [
            "Clearly define the change vision and objectives",
            "Establish the business case for change",
            "Identify key stakeholders and their interests",
            "Assess current state and desired future state",
            "Create project governance structure"
        ],
        "key_activities": [
            "Conduct change vision workshops",
            "Develop business case and ROI analysis",
            "Create comprehensive stakeholder map",
            "Perform current state assessment",
            "Establish project charter and governance",
            "Define scope boundaries and constraints",
            "Identify change drivers and barriers"
        ],
        "deliverables": [
            {"name": "Change Charter", "type": "document", "required": True},
            {"name": "Business Case", "type": "document", "required": True},
            {"name": "Stakeholder Analysis", "type": "analysis", "required": True},
            {"name": "Current State Assessment", "type": "assessment", "required": True},
            {"name": "Project Scope Statement", "type": "document", "required": True},
            {"name": "Initial Risk Assessment", "type": "assessment", "required": False}
        ],
        "tools": [
            "Stakeholder Mapping Template",
            "Business Case Canvas",
            "Current State Analysis Framework",
            "Change Vision Worksheet"
        ],
        "completion_criteria": [
            "Change charter approved by sponsors",
            "Stakeholder map validated by key leaders",
            "Business case demonstrates clear ROI",
            "Scope boundaries clearly defined"
        ],
        "ai_focus": "Analyze organizational inertia and recommend force application strategies to initiate change momentum."
    },
    "measure": {
        "name": "Measure",
        "description": "Assess organizational readiness and establish baselines",
        "order": 2,
        "newton_law": "Second Law - Measuring Forces and Acceleration",
        "newton_insight": "Acceleration equals force applied divided by organizational mass. Measure resistance to calculate required force accurately.",
        "objectives": [
            "Conduct comprehensive change readiness assessment",
            "Establish baseline metrics and KPIs",
            "Quantify organizational capability gaps",
            "Measure communication effectiveness",
            "Assess resource adequacy and constraints"
        ],
        "key_activities": [
            "Execute change readiness assessment across all dimensions",
            "Establish baseline performance metrics",
            "Conduct organizational capability assessment",
            "Analyze communication channels and effectiveness",
            "Evaluate resource capacity and constraints",
            "Measure cultural readiness for change",
            "Assess leadership alignment and commitment"
        ],
        "deliverables": [
            {"name": "Change Readiness Report", "type": "assessment", "required": True},
            {"name": "Baseline Metrics Dashboard", "type": "dashboard", "required": True},
            {"name": "Capability Gap Analysis", "type": "analysis", "required": True},
            {"name": "Communication Audit", "type": "audit", "required": True},
            {"name": "Resource Assessment", "type": "assessment", "required": True},
            {"name": "Cultural Readiness Analysis", "type": "analysis", "required": False}
        ],
        "tools": [
            "5-Dimension Readiness Assessment",
            "Newton's Laws Calculator",
            "Capability Maturity Framework",
            "Communication Effectiveness Audit"
        ],
        "completion_criteria": [
            "All five readiness dimensions assessed",
            "Baseline metrics established and approved",
            "Capability gaps identified and quantified",
            "Communication audit completed with recommendations"
        ],
        "ai_focus": "Calculate precise force requirements using Newton's laws and predict change acceleration based on organizational mass."
    },
    "plan": {
        "name": "Plan",
        "description": "Develop comprehensive change management strategy",
        "order": 3,
        "newton_law": "Third Law - Planning for Action-Reaction",
        "newton_insight": "For every action, there is an equal and opposite reaction. Plan comprehensively for predictable resistance patterns.",
        "objectives": [
            "Develop detailed change management strategy",
            "Create implementation roadmap with timelines",
            "Design communication and engagement plans",
            "Plan training and capability development",
            "Establish resistance management approaches"
        ],
        "key_activities": [
            "Develop comprehensive change strategy",
            "Create detailed implementation roadmap",
            "Design multi-channel communication plan",
            "Plan training and development programs",
            "Develop resistance management strategy",
            "Create stakeholder engagement plan",
            "Design success metrics and monitoring approach"
        ],
        "deliverables": [
            {"name": "Change Management Strategy", "type": "strategy", "required": True},
            {"name": "Implementation Roadmap", "type": "plan", "required": True},
            {"name": "Communication Plan", "type": "plan", "required": True},
            {"name": "Training and Development Plan", "type": "plan", "required": True},
            {"name": "Resistance Management Plan", "type": "plan", "required": True},
            {"name": "Stakeholder Engagement Plan", "type": "plan", "required": True},
            {"name": "Success Metrics Framework", "type": "framework", "required": False}
        ],
        "tools": [
            "Change Strategy Canvas",
            "Implementation Planning Template",
            "Communication Plan Template",
            "Resistance Management Toolkit"
        ],
        "completion_criteria": [
            "Change strategy approved by steering committee",
            "Implementation roadmap with clear milestones",
            "Communication plan covers all stakeholder groups",
            "Training plans address all capability gaps"
        ],
        "ai_focus": "Apply Third Law principles to predict resistance patterns and develop proactive mitigation strategies."
    },
    "act": {
        "name": "Act",
        "description": "Execute the change management plan",
        "order": 4,
        "newton_law": "Applied Force - Implementation in Motion",
        "newton_insight": "Apply consistent force to maintain momentum and overcome organizational inertia during implementation.",
        "objectives": [
            "Execute communication campaigns effectively",
            "Deliver training and skill development",
            "Implement new processes and systems",
            "Maintain stakeholder engagement",
            "Address resistance and barriers actively"
        ],
        "key_activities": [
            "Launch multi-channel communication campaigns",
            "Execute training and development programs",
            "Implement new processes and systems",
            "Facilitate change adoption activities",
            "Monitor stakeholder engagement levels",
            "Address resistance and remove barriers",
            "Collect and act on continuous feedback"
        ],
        "deliverables": [
            {"name": "Communication Campaign Materials", "type": "materials", "required": True},
            {"name": "Training Records and Assessments", "type": "records", "required": True},
            {"name": "Implementation Progress Reports", "type": "reports", "required": True},
            {"name": "Stakeholder Feedback Analysis", "type": "analysis", "required": True},
            {"name": "Issue Resolution Log", "type": "log", "required": True},
            {"name": "Change Adoption Metrics", "type": "metrics", "required": False}
        ],
        "tools": [
            "Communication Campaign Toolkit",
            "Training Delivery Framework",
            "Implementation Tracking Dashboard",
            "Feedback Collection System"
        ],
        "completion_criteria": [
            "Communication campaigns achieving target reach",
            "Training completion rates above 90%",
            "Key implementation milestones achieved",
            "Stakeholder satisfaction above baseline"
        ],
        "ai_focus": "Monitor force application effectiveness and recommend adjustments to maintain optimal change momentum."
    },
    "control": {
        "name": "Control",
        "description": "Monitor progress and maintain momentum",
        "order": 5,
        "newton_law": "Continuous Force Application",
        "newton_insight": "Continuous force application prevents the organization from returning to its original state due to natural inertia.",
        "objectives": [
            "Monitor implementation progress continuously",
            "Track adoption and compliance metrics",
            "Manage issues and implement corrections",
            "Maintain stakeholder engagement momentum",
            "Ensure sustainable change adoption"
        ],
        "key_activities": [
            "Monitor KPIs and success metrics continuously",
            "Track change adoption across organization",
            "Conduct regular stakeholder pulse surveys",
            "Identify and resolve implementation issues",
            "Adjust plans based on performance data",
            "Maintain communication momentum",
            "Celebrate milestones and quick wins"
        ],
        "deliverables": [
            {"name": "Progress Monitoring Dashboard", "type": "dashboard", "required": True},
            {"name": "Adoption Metrics Reports", "type": "reports", "required": True},
            {"name": "Issue Management Log", "type": "log", "required": True},
            {"name": "Stakeholder Pulse Survey Results", "type": "results", "required": True},
            {"name": "Course Correction Plans", "type": "plans", "required": True},
            {"name": "Success Stories Documentation", "type": "documentation", "required": False}
        ],
        "tools": [
            "KPI Monitoring Dashboard",
            "Adoption Tracking System",
            "Issue Management Platform",
            "Stakeholder Pulse Survey Tool"
        ],
        "completion_criteria": [
            "All KPIs trending toward targets",
            "Adoption rates meet or exceed expectations",
            "Critical issues resolved within SLA",
            "Stakeholder engagement sustained above baseline"
        ],
        "ai_focus": "Analyze performance data to predict trajectory and recommend course corrections to maintain momentum."
    },
    "transform": {
        "name": "Transform",
        "description": "Institutionalize change and capture benefits",
        "order": 6,
        "newton_law": "New Equilibrium State",
        "newton_insight": "The organization has reached a new equilibrium state with the change fully integrated and sustainable.",
        "objectives": [
            "Measure and validate benefits realization",
            "Institutionalize new ways of working",
            "Capture and share lessons learned",
            "Celebrate successes and recognize contributors",
            "Establish sustainable operating model"
        ],
        "key_activities": [
            "Conduct comprehensive benefits assessment",
            "Institutionalize new processes and behaviors",
            "Document lessons learned and best practices",
            "Recognize and celebrate change champions",
            "Transfer ownership to business operations",
            "Establish continuous improvement processes",
            "Plan for future change readiness"
        ],
        "deliverables": [
            {"name": "Benefits Realization Report", "type": "report", "required": True},
            {"name": "Standard Operating Procedures", "type": "procedures", "required": True},
            {"name": "Lessons Learned Documentation", "type": "documentation", "required": True},
            {"name": "Success Recognition Program", "type": "program", "required": True},
            {"name": "Business Transition Plan", "type": "plan", "required": True},
            {"name": "Continuous Improvement Framework", "type": "framework", "required": False}
        ],
        "tools": [
            "Benefits Tracking Framework",
            "Process Documentation Templates",
            "Lessons Learned Capture Tool",
            "Recognition Program Toolkit"
        ],
        "completion_criteria": [
            "Target benefits achieved and validated",
            "New processes fully documented and embedded",
            "Lessons learned captured and shared",
            "Business ownership successfully transferred"
        ],
        "ai_focus": "Analyze transformation success and provide recommendations for sustainable change and future readiness."
    }
}

# Enhanced Pydantic models
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

class Deliverable(BaseModel):
    id: Optional[str] = None
    name: str
    type: str
    required: bool = True
    status: str = "pending"  # pending, in_progress, completed, approved
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    content: Optional[str] = None
    file_url: Optional[str] = None
    approval_notes: Optional[str] = None

class Task(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    phase: str
    category: str  # key_activity, deliverable, milestone, objective
    status: str = "pending"  # pending, in_progress, completed, blocked
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    priority: str = "medium"  # low, medium, high, critical
    notes: Optional[str] = None
    dependencies: List[str] = []
    completion_criteria: Optional[str] = None

class Milestone(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    phase: str
    target_date: datetime
    completion_date: Optional[datetime] = None
    status: str = "pending"  # pending, in_progress, completed, overdue
    success_criteria: List[str] = []
    deliverables: List[str] = []
    approval_required: bool = True
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None

class PhaseGateReview(BaseModel):
    id: Optional[str] = None
    phase: str
    project_id: str
    review_date: datetime
    reviewer_id: str
    status: str = "pending"  # pending, approved, rejected, conditional
    completion_percentage: float
    deliverables_status: Dict[str, str]
    success_criteria_met: List[str]
    issues_identified: List[str]
    recommendations: List[str]
    next_phase_readiness: str  # ready, not_ready, conditional
    notes: Optional[str] = None

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
    phase_recommendations: Optional[Dict[str, str]] = None
    recommended_project: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Project(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    organization: str
    owner_id: str
    current_phase: str = "identify"
    status: str = "active"  # active, on_hold, completed, cancelled
    team_members: List[str] = []
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    budget: Optional[float] = None
    progress_percentage: float = 0.0
    phase_progress: Dict[str, float] = {}
    tasks: List[Task] = []
    deliverables: List[Deliverable] = []
    milestones: List[Milestone] = []
    gate_reviews: List[PhaseGateReview] = []
    newton_insights: Dict[str, Any] = {}
    assessment_id: Optional[str] = None
    stakeholders: List[Dict[str, Any]] = []
    risks: List[Dict[str, Any]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PhaseTransition(BaseModel):
    project_id: str
    from_phase: str
    to_phase: str
    transition_date: datetime
    completion_notes: str
    lessons_learned: Optional[str] = None
    gate_review_id: Optional[str] = None

class ProjectFromAssessment(BaseModel):
    assessment_id: str
    project_name: str
    description: str
    target_completion_date: Optional[datetime] = None
    budget: Optional[float] = None

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
        print(f"Received token: {token}")
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
        print(f"Authentication error: {str(e)}")
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

def generate_comprehensive_tasks_for_phase(phase: str, project_id: str) -> List[Dict]:
    """Generate comprehensive tasks, deliverables, and milestones for a phase"""
    phase_config = IMPACT_PHASES.get(phase, {})
    tasks = []
    
    # Create tasks for objectives
    for i, objective in enumerate(phase_config.get("objectives", [])):
        task = {
            "id": str(uuid.uuid4()),
            "title": objective,
            "description": f"Achieve objective: {objective.lower()}",
            "phase": phase,
            "category": "objective",
            "status": "pending",
            "priority": "high",
            "completion_criteria": f"Successfully complete {objective.lower()}",
            "created_at": datetime.utcnow()
        }
        tasks.append(task)
    
    # Create tasks for key activities
    for i, activity in enumerate(phase_config.get("key_activities", [])):
        task = {
            "id": str(uuid.uuid4()),
            "title": activity,
            "description": f"Execute activity: {activity.lower()}",
            "phase": phase,
            "category": "key_activity",
            "status": "pending",
            "priority": "medium",
            "completion_criteria": f"Complete {activity.lower()} according to standards",
            "created_at": datetime.utcnow()
        }
        tasks.append(task)
    
    return tasks

def generate_deliverables_for_phase(phase: str, project_id: str) -> List[Dict]:
    """Generate deliverables for a phase"""
    phase_config = IMPACT_PHASES.get(phase, {})
    deliverables = []
    
    for deliverable_config in phase_config.get("deliverables", []):
        deliverable = {
            "id": str(uuid.uuid4()),
            "name": deliverable_config["name"],
            "type": deliverable_config["type"],
            "required": deliverable_config["required"],
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        deliverables.append(deliverable)
    
    return deliverables

def generate_milestones_for_phase(phase: str, project_id: str, start_date: datetime) -> List[Dict]:
    """Generate milestones for a phase"""
    phase_config = IMPACT_PHASES.get(phase, {})
    milestones = []
    
    # Create phase completion milestone
    phase_order = phase_config.get("order", 1)
    target_date = start_date + timedelta(weeks=phase_order * 2)  # 2 weeks per phase estimate
    
    milestone = {
        "id": str(uuid.uuid4()),
        "title": f"{phase_config.get('name', phase)} Phase Completion",
        "description": f"Complete all activities and deliverables for the {phase} phase",
        "phase": phase,
        "target_date": target_date,
        "status": "pending",
        "success_criteria": phase_config.get("completion_criteria", []),
        "approval_required": True,
        "created_at": datetime.utcnow()
    }
    milestones.append(milestone)
    
    return milestones

def calculate_project_progress(project_data: Dict) -> float:
    """Calculate overall project progress based on completed tasks, deliverables, and milestones"""
    total_items = 0
    completed_items = 0
    
    # Count tasks
    if project_data.get("tasks"):
        total_items += len(project_data["tasks"])
        completed_items += len([task for task in project_data["tasks"] if task.get("status") == "completed"])
    
    # Count deliverables
    if project_data.get("deliverables"):
        total_items += len(project_data["deliverables"])
        completed_items += len([deliv for deliv in project_data["deliverables"] if deliv.get("status") in ["completed", "approved"]])
    
    # Count milestones
    if project_data.get("milestones"):
        total_items += len(project_data["milestones"])
        completed_items += len([milestone for milestone in project_data["milestones"] if milestone.get("status") == "completed"])
    
    if total_items == 0:
        return 0.0
    
    return (completed_items / total_items) * 100

def calculate_phase_progress(project_data: Dict, phase: str) -> float:
    """Calculate progress for a specific phase"""
    phase_items = 0
    completed_phase_items = 0
    
    # Count phase-specific tasks
    if project_data.get("tasks"):
        phase_tasks = [task for task in project_data["tasks"] if task.get("phase") == phase]
        phase_items += len(phase_tasks)
        completed_phase_items += len([task for task in phase_tasks if task.get("status") == "completed"])
    
    # Count phase-specific deliverables
    if project_data.get("deliverables"):
        # Deliverables are associated with phases through the IMPACT_PHASES configuration
        phase_config = IMPACT_PHASES.get(phase, {})
        phase_deliverable_names = [d["name"] for d in phase_config.get("deliverables", [])]
        phase_deliverables = [d for d in project_data["deliverables"] if d.get("name") in phase_deliverable_names]
        phase_items += len(phase_deliverables)
        completed_phase_items += len([d for d in phase_deliverables if d.get("status") in ["completed", "approved"]])
    
    # Count phase-specific milestones
    if project_data.get("milestones"):
        phase_milestones = [m for m in project_data["milestones"] if m.get("phase") == phase]
        phase_items += len(phase_milestones)
        completed_phase_items += len([m for m in phase_milestones if m.get("status") == "completed"])
    
    if phase_items == 0:
        return 0.0
    
    return (completed_phase_items / phase_items) * 100

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

            Structure your response as detailed but actionable insights with specific IMPACT phase recommendations."""
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

        4. IMPACT PHASE RECOMMENDATIONS
        For each phase (Identify, Measure, Plan, Act, Control, Transform), provide specific guidance:
        - Key focus areas based on assessment scores
        - Phase-specific risks to watch
        - Success factors for this organization

        5. RISK ANALYSIS (3-4 key risks)
        Primary risks with specific mitigation strategies.

        6. PROJECT RECOMMENDATION
        Based on the assessment, recommend a project structure with:
        - Suggested timeline (phases and duration)
        - Critical success factors
        - Resource allocation priorities

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
        
        # Generate phase-specific recommendations
        phase_recommendations = {}
        
        # Identify phase
        if assessment.change_management_maturity.score <= 2:
            phase_recommendations["identify"] = "Focus heavily on establishing change governance and building initial stakeholder buy-in"
        else:
            phase_recommendations["identify"] = "Leverage existing change maturity to accelerate stakeholder alignment and vision setting"
        
        # Measure phase
        if assessment.communication_effectiveness.score <= 2:
            phase_recommendations["measure"] = "Prioritize communication channel assessment and establish robust feedback mechanisms"
        else:
            phase_recommendations["measure"] = "Use strong communication channels to gather comprehensive baseline data"
        
        # Plan phase
        if assessment.leadership_support.score <= 2:
            phase_recommendations["plan"] = "Invest significant effort in leadership alignment and sponsor engagement strategies"
        else:
            phase_recommendations["plan"] = "Leverage strong leadership support to develop ambitious and comprehensive change plans"
        
        # Act phase
        if assessment.workforce_adaptability.score <= 2:
            phase_recommendations["act"] = "Implement gradual rollout with extensive support and training to address workforce resistance"
        else:
            phase_recommendations["act"] = "Accelerate implementation leveraging workforce openness to change"
        
        # Control phase
        if assessment.resource_adequacy.score <= 2:
            phase_recommendations["control"] = "Establish lean monitoring processes and focus on essential metrics due to resource constraints"
        else:
            phase_recommendations["control"] = "Implement comprehensive monitoring and control systems with adequate resource support"
        
        # Transform phase
        phase_recommendations["transform"] = f"Plan for {'extensive' if avg_score >= 4 else 'moderate' if avg_score >= 3 else 'basic'} institutionalization based on overall readiness"
        
        # Generate recommended project structure
        recommended_project = {
            "suggested_duration_weeks": max(12, int(24 - (avg_score * 2))),  # Lower readiness = longer project
            "critical_success_factors": [
                f"Strong focus on {['leadership engagement' if assessment.leadership_support.score <= 2 else 'communication effectiveness' if assessment.communication_effectiveness.score <= 2 else 'workforce adaptation'][0]}",
                "Regular progress monitoring with course correction capability",
                f"{'Extensive' if newton_data['reaction']['resistance'] > 30 else 'Moderate'} resistance management protocols"
            ],
            "resource_priorities": [
                "Change management expertise and consulting support",
                "Communication and training resources",
                "Stakeholder engagement and feedback systems"
            ],
            "recommended_start_phase": "identify",
            "high_risk_phases": [phase for phase, score in [
                ("measure", assessment.communication_effectiveness.score),
                ("plan", assessment.leadership_support.score),
                ("act", assessment.workforce_adaptability.score)
            ] if score <= 2]
        }
        
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
            "phase_recommendations": phase_recommendations,
            "recommended_project": recommended_project,
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
            "phase_recommendations": {
                "identify": "Focus on stakeholder alignment and vision clarity",
                "measure": "Establish comprehensive baseline metrics",
                "plan": "Develop detailed implementation strategy",
                "act": "Execute with careful monitoring",
                "control": "Maintain momentum through tracking",
                "transform": "Institutionalize changes effectively"
            },
            "recommended_project": {
                "suggested_duration_weeks": 16,
                "critical_success_factors": ["Leadership engagement", "Communication effectiveness"],
                "resource_priorities": ["Change management expertise", "Training resources"],
                "recommended_start_phase": "identify",
                "high_risk_phases": []
            },
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

# Authentication routes
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

# Assessment routes
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
        assessment.phase_recommendations = ai_result.get("phase_recommendations", {})
        assessment.recommended_project = ai_result.get("recommended_project", {})
        
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
        # Convert ObjectId to string and remove _id field
        for assessment in assessments:
            if "_id" in assessment:
                del assessment["_id"]
        return assessments
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve assessments: {str(e)}")

@app.get("/api/assessments/{assessment_id}")
async def get_assessment(assessment_id: str, current_user: User = Depends(get_current_user)):
    try:
        assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        if "_id" in assessment:
            del assessment["_id"]
        return assessment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve assessment: {str(e)}")

# Project and IMPACT Workflow routes
@app.get("/api/impact/phases")
async def get_impact_phases():
    """Get IMPACT methodology phases configuration"""
    return IMPACT_PHASES

@app.get("/api/impact/phases/{phase}")
async def get_phase_details(phase: str):
    """Get detailed information about a specific IMPACT phase"""
    if phase not in IMPACT_PHASES:
        raise HTTPException(status_code=404, detail="Phase not found")
    return IMPACT_PHASES[phase]

@app.post("/api/projects")
async def create_project(project: Project, current_user: User = Depends(get_current_user)):
    try:
        project_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Set project metadata
        project.id = project_id
        project.owner_id = current_user.id
        project.organization = current_user.organization
        project.current_phase = "identify"
        project.start_date = now
        project.created_at = now
        project.updated_at = now
        
        # Initialize phase progress
        project.phase_progress = {phase: 0.0 for phase in IMPACT_PHASES.keys()}
        
        # Generate comprehensive tasks, deliverables, and milestones for the initial phase
        initial_tasks = generate_comprehensive_tasks_for_phase("identify", project_id)
        initial_deliverables = generate_deliverables_for_phase("identify", project_id)
        initial_milestones = generate_milestones_for_phase("identify", project_id, now)
        
        project.tasks = [Task(**task) for task in initial_tasks]
        project.deliverables = [Deliverable(**deliv) for deliv in initial_deliverables]
        project.milestones = [Milestone(**milestone) for milestone in initial_milestones]
        
        # Calculate initial progress
        project.progress_percentage = calculate_project_progress(project.dict())
        project.phase_progress["identify"] = calculate_phase_progress(project.dict(), "identify")
        
        # Save to database
        project_dict = project.dict()
        await db.projects.insert_one(project_dict)
        
        return project
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Project creation failed: {str(e)}")

@app.post("/api/projects/from-assessment")
async def create_project_from_assessment(
    project_data: ProjectFromAssessment,
    current_user: User = Depends(get_current_user)
):
    try:
        # Get the assessment
        assessment = await db.assessments.find_one({"id": project_data.assessment_id, "user_id": current_user.id})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Create project based on assessment recommendations
        project_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        recommended_project = assessment.get("recommended_project", {})
        suggested_duration = recommended_project.get("suggested_duration_weeks", 16)
        target_completion = project_data.target_completion_date or (now + timedelta(weeks=suggested_duration))
        
        project = Project(
            id=project_id,
            name=project_data.project_name,
            description=project_data.description,
            organization=current_user.organization,
            owner_id=current_user.id,
            current_phase="identify",
            status="active",
            start_date=now,
            target_completion_date=target_completion,
            budget=project_data.budget,
            assessment_id=project_data.assessment_id,
            newton_insights=assessment.get("newton_analysis", {}),
            created_at=now,
            updated_at=now
        )
        
        # Initialize phase progress
        project.phase_progress = {phase: 0.0 for phase in IMPACT_PHASES.keys()}
        
        # Generate comprehensive project structure based on assessment
        all_tasks = []
        all_deliverables = []
        all_milestones = []
        
        for phase_name in IMPACT_PHASES.keys():
            phase_tasks = generate_comprehensive_tasks_for_phase(phase_name, project_id)
            phase_deliverables = generate_deliverables_for_phase(phase_name, project_id)
            phase_milestones = generate_milestones_for_phase(phase_name, project_id, now)
            
            all_tasks.extend(phase_tasks)
            all_deliverables.extend(phase_deliverables)
            all_milestones.extend(phase_milestones)
        
        project.tasks = [Task(**task) for task in all_tasks]
        project.deliverables = [Deliverable(**deliv) for deliv in all_deliverables]
        project.milestones = [Milestone(**milestone) for milestone in all_milestones]
        
        # Calculate initial progress
        project.progress_percentage = calculate_project_progress(project.dict())
        for phase_name in IMPACT_PHASES.keys():
            project.phase_progress[phase_name] = calculate_phase_progress(project.dict(), phase_name)
        
        # Save to database
        project_dict = project.dict()
        await db.projects.insert_one(project_dict)
        
        return project
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Project creation from assessment failed: {str(e)}")

@app.get("/api/projects")
async def get_projects(current_user: User = Depends(get_current_user)):
    try:
        projects = await db.projects.find({"organization": current_user.organization}).to_list(100)
        # Convert ObjectId to string and remove _id field
        for project in projects:
            if "_id" in project:
                del project["_id"]
        return projects
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve projects: {str(e)}")

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str, current_user: User = Depends(get_current_user)):
    try:
        project = await db.projects.find_one({"id": project_id, "organization": current_user.organization})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if "_id" in project:
            del project["_id"]
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve project: {str(e)}")

@app.put("/api/projects/{project_id}/phase")
async def transition_project_phase(
    project_id: str, 
    transition: PhaseTransition,
    current_user: User = Depends(get_current_user)
):
    try:
        # Get project
        project = await db.projects.find_one({"id": project_id, "organization": current_user.organization})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Validate phase transition
        current_phase_order = IMPACT_PHASES.get(transition.from_phase, {}).get("order", 0)
        next_phase_order = IMPACT_PHASES.get(transition.to_phase, {}).get("order", 0)
        
        if next_phase_order != current_phase_order + 1:
            raise HTTPException(status_code=400, detail="Invalid phase transition - phases must be completed sequentially")
        
        # Check if current phase is ready for transition (optional validation)
        current_phase_progress = calculate_phase_progress(project, transition.from_phase)
        if current_phase_progress < 80:  # Require 80% completion before transition
            raise HTTPException(status_code=400, detail=f"Current phase is only {current_phase_progress:.1f}% complete. Minimum 80% required for transition.")
        
        # Update project phase
        await db.projects.update_one(
            {"id": project_id},
            {
                "$set": {
                    "current_phase": transition.to_phase,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Generate tasks and deliverables for new phase if not already exists
        existing_phase_tasks = [task for task in project.get("tasks", []) if task.get("phase") == transition.to_phase]
        if not existing_phase_tasks:
            new_tasks = generate_comprehensive_tasks_for_phase(transition.to_phase, project_id)
            new_deliverables = generate_deliverables_for_phase(transition.to_phase, project_id)
            
            await db.projects.update_one(
                {"id": project_id},
                {
                    "$push": {
                        "tasks": {"$each": [Task(**task).dict() for task in new_tasks]},
                        "deliverables": {"$each": [Deliverable(**deliv).dict() for deliv in new_deliverables]}
                    }
                }
            )
        
        # Log phase transition
        transition_log = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "from_phase": transition.from_phase,
            "to_phase": transition.to_phase,
            "transition_date": transition.transition_date,
            "completion_notes": transition.completion_notes,
            "lessons_learned": transition.lessons_learned,
            "user_id": current_user.id,
            "created_at": datetime.utcnow()
        }
        await db.phase_transitions.insert_one(transition_log)
        
        return {"message": f"Project successfully transitioned from {transition.from_phase} to {transition.to_phase} phase"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Phase transition failed: {str(e)}")

@app.put("/api/projects/{project_id}/tasks/{task_id}")
async def update_task(
    project_id: str,
    task_id: str,
    task_update: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    try:
        # Update task in project
        update_data = {
            "tasks.$.status": task_update.get("status"),
            "tasks.$.assigned_to": task_update.get("assigned_to"),
            "tasks.$.notes": task_update.get("notes"),
            "tasks.$.priority": task_update.get("priority"),
            "updated_at": datetime.utcnow()
        }
        
        if task_update.get("status") == "completed":
            update_data["tasks.$.completed_date"] = datetime.utcnow()
        
        await db.projects.update_one(
            {"id": project_id, "tasks.id": task_id, "organization": current_user.organization},
            {"$set": update_data}
        )
        
        # Recalculate project and phase progress
        project = await db.projects.find_one({"id": project_id})
        if project:
            new_progress = calculate_project_progress(project)
            phase_progress = {}
            for phase in IMPACT_PHASES.keys():
                phase_progress[phase] = calculate_phase_progress(project, phase)
            
            await db.projects.update_one(
                {"id": project_id},
                {
                    "$set": {
                        "progress_percentage": new_progress,
                        "phase_progress": phase_progress
                    }
                }
            )
        
        return {"message": "Task updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Task update failed: {str(e)}")

@app.put("/api/projects/{project_id}/deliverables/{deliverable_id}")
async def update_deliverable(
    project_id: str,
    deliverable_id: str,
    deliverable_update: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    try:
        # Update deliverable in project
        update_data = {
            "deliverables.$.status": deliverable_update.get("status"),
            "deliverables.$.assigned_to": deliverable_update.get("assigned_to"),
            "deliverables.$.content": deliverable_update.get("content"),
            "deliverables.$.file_url": deliverable_update.get("file_url"),
            "deliverables.$.approval_notes": deliverable_update.get("approval_notes"),
            "updated_at": datetime.utcnow()
        }
        
        if deliverable_update.get("status") in ["completed", "approved"]:
            update_data["deliverables.$.completed_date"] = datetime.utcnow()
        
        await db.projects.update_one(
            {"id": project_id, "deliverables.id": deliverable_id, "organization": current_user.organization},
            {"$set": update_data}
        )
        
        # Recalculate progress
        project = await db.projects.find_one({"id": project_id})
        if project:
            new_progress = calculate_project_progress(project)
            phase_progress = {}
            for phase in IMPACT_PHASES.keys():
                phase_progress[phase] = calculate_phase_progress(project, phase)
            
            await db.projects.update_one(
                {"id": project_id},
                {
                    "$set": {
                        "progress_percentage": new_progress,
                        "phase_progress": phase_progress
                    }
                }
            )
        
        return {"message": "Deliverable updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Deliverable update failed: {str(e)}")

@app.post("/api/projects/{project_id}/gate-review")
async def create_gate_review(
    project_id: str,
    gate_review: PhaseGateReview,
    current_user: User = Depends(get_current_user)
):
    try:
        # Generate ID and set metadata
        gate_review.id = str(uuid.uuid4())
        gate_review.project_id = project_id
        gate_review.reviewer_id = current_user.id
        gate_review.review_date = datetime.utcnow()
        
        # Calculate completion percentage based on phase progress
        project = await db.projects.find_one({"id": project_id, "organization": current_user.organization})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        gate_review.completion_percentage = calculate_phase_progress(project, gate_review.phase)
        
        # Add gate review to project
        await db.projects.update_one(
            {"id": project_id},
            {
                "$push": {"gate_reviews": gate_review.dict()},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return gate_review
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gate review creation failed: {str(e)}")

@app.get("/api/analytics/advanced")
async def get_advanced_analytics(current_user: User = Depends(get_current_user)):
    try:
        # Get all assessments for the organization
        assessments = await db.assessments.find({"organization": current_user.organization}).to_list(100)
        
        # Clean up ObjectId fields
        for assessment in assessments:
            if "_id" in assessment:
                del assessment["_id"]
        
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
        
        # Clean up ObjectId fields
        for assessment in recent_assessments:
            if "_id" in assessment:
                del assessment["_id"]
        
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