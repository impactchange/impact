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

# Assessment Types Configuration - Multiple Assessment Support
ASSESSMENT_TYPES = {
    "general_readiness": {
        "name": "General Change Readiness Assessment",
        "description": "Comprehensive organizational change readiness evaluation for any type of transformation project",
        "icon": "📋",
        "dimensions": [
            {
                "id": "leadership_commitment",
                "name": "Leadership Commitment & Sponsorship",
                "description": "How committed is senior leadership to this change initiative?",
                "category": "core"
            },
            {
                "id": "organizational_culture",
                "name": "Organizational Culture & Change History", 
                "description": "How well does the organization typically adapt to change?",
                "category": "core"
            },
            {
                "id": "resource_availability",
                "name": "Resource Availability & Capability",
                "description": "Are adequate financial, human, and technical resources available?",
                "category": "core"
            },
            {
                "id": "stakeholder_engagement",
                "name": "Stakeholder Engagement & Communication",
                "description": "How effective are existing stakeholder engagement capabilities?",
                "category": "core"
            },
            {
                "id": "training_capability",
                "name": "Training & Development Capability",
                "description": "What training capabilities and infrastructure exist?",
                "category": "core"
            }
        ]
    },
    "software_implementation": {
        "name": "Software Implementation Readiness Assessment",
        "description": "Specialized assessment for software implementation projects and technology adoption",
        "icon": "💻",
        "dimensions": [
            {
                "id": "leadership_commitment",
                "name": "Leadership Commitment & Sponsorship",
                "description": "How committed is senior leadership to this software implementation?",
                "category": "core"
            },
            {
                "id": "organizational_culture",
                "name": "Organizational Culture & Change History",
                "description": "How well does the organization adapt to new technology?",
                "category": "core"
            },
            {
                "id": "resource_availability", 
                "name": "Resource Availability & Capability",
                "description": "Are adequate resources available for software implementation?",
                "category": "core"
            },
            {
                "id": "stakeholder_engagement",
                "name": "Stakeholder Engagement & Communication",
                "description": "How effective are communication channels for technology changes?",
                "category": "core"
            },
            {
                "id": "training_capability",
                "name": "Training & Development Capability", 
                "description": "What technical training capabilities exist?",
                "category": "core"
            },
            {
                "id": "technical_infrastructure",
                "name": "Technical Infrastructure Readiness",
                "description": "How ready is the technical infrastructure for new software?",
                "category": "specialized"
            },
            {
                "id": "user_adoption_readiness",
                "name": "User Adoption Readiness",
                "description": "How ready are end users to adopt new software systems?",
                "category": "specialized"
            },
            {
                "id": "data_migration_readiness",
                "name": "Data Migration & Integration Readiness",
                "description": "How prepared is the organization for data migration and system integration?",
                "category": "specialized"
            }
        ]
    },
    "business_process": {
        "name": "Business Process Evaluation Assessment",
        "description": "Assessment for business process improvement and operational transformation projects",
        "icon": "⚙️",
        "dimensions": [
            {
                "id": "leadership_commitment",
                "name": "Leadership Commitment & Sponsorship",
                "description": "How committed is leadership to business process improvement?",
                "category": "core"
            },
            {
                "id": "organizational_culture",
                "name": "Organizational Culture & Change History",
                "description": "How well does the organization adapt to process changes?",
                "category": "core"
            },
            {
                "id": "resource_availability",
                "name": "Resource Availability & Capability", 
                "description": "Are adequate resources available for process transformation?",
                "category": "core"
            },
            {
                "id": "stakeholder_engagement",
                "name": "Stakeholder Engagement & Communication",
                "description": "How effective are stakeholder engagement strategies?",
                "category": "core"
            },
            {
                "id": "training_capability",
                "name": "Training & Development Capability",
                "description": "What process training capabilities exist?",
                "category": "core"
            },
            {
                "id": "process_maturity",
                "name": "Current Process Maturity",
                "description": "How mature and documented are current business processes?",
                "category": "specialized"
            },
            {
                "id": "cross_functional_collaboration",
                "name": "Cross-Functional Collaboration",
                "description": "How effectively do departments collaborate on process improvements?",
                "category": "specialized"
            },
            {
                "id": "performance_measurement",
                "name": "Performance Measurement Capability",
                "description": "How well can the organization measure and track process performance?",
                "category": "specialized"
            }
        ]
    },
    "manufacturing_operations": {
        "name": "Manufacturing Operations Assessment",
        "description": "Assessment for manufacturing line evaluations and operational improvements",
        "icon": "🏭",
        "dimensions": [
            {
                "id": "leadership_commitment",
                "name": "Leadership Commitment & Sponsorship", 
                "description": "How committed is leadership to operational improvements?",
                "category": "core"
            },
            {
                "id": "organizational_culture",
                "name": "Organizational Culture & Change History",
                "description": "How well does the organization adapt to operational changes?",
                "category": "core"
            },
            {
                "id": "resource_availability",
                "name": "Resource Availability & Capability",
                "description": "Are adequate resources available for operational transformation?",
                "category": "core"
            },
            {
                "id": "stakeholder_engagement",
                "name": "Stakeholder Engagement & Communication",
                "description": "How effective are communication channels in the manufacturing environment?",
                "category": "core"
            },
            {
                "id": "training_capability",
                "name": "Training & Development Capability",
                "description": "What operational training capabilities exist?",
                "category": "core"
            },
            {
                "id": "operational_constraints",
                "name": "Operational Constraints Management",
                "description": "How manageable are operational constraints during improvements?",
                "category": "specialized"
            },
            {
                "id": "maintenance_operations_alignment",
                "name": "Maintenance-Operations Alignment",
                "description": "How well aligned are maintenance and operations teams?",
                "category": "specialized"
            },
            {
                "id": "shift_coordination",
                "name": "Shift Work & Coordination",
                "description": "How well can shift patterns accommodate improvement activities?",
                "category": "specialized"
            },
            {
                "id": "safety_compliance",
                "name": "Safety & Compliance Integration",
                "description": "How well can safety and regulatory requirements be integrated?",
                "category": "specialized"
            }
        ]
    }
}

# Enhanced IMPACT Phases Configuration - Universal Change Management
IMPACT_PHASES = {
    "investigate": {
        "name": "Investigate & Assess",
        "description": "Understanding current state and establishing transformation foundation",
        "order": 1,
        "newton_law": "First Law - Overcoming Organizational Inertia",
        "newton_insight": "Organizations at rest tend to stay at rest. Significant force is required to overcome initial inertia and establish change momentum.",
        "objectives": [
            "Comprehensively evaluate current state and organizational readiness",
            "Assess stakeholder landscape and change capacity",
            "Identify risks, opportunities, and critical success factors",
            "Establish baseline measurements and performance metrics",
            "Map cultural factors and organizational dynamics"
        ],
        "key_activities": [
            "Conduct comprehensive stakeholder analysis",
            "Execute multi-dimensional change readiness assessment",
            "Perform current state analysis and gap identification",
            "Assess organizational culture and change history",
            "Identify risks and develop mitigation strategies",
            "Map informal networks and influence patterns",
            "Evaluate technical and operational capabilities"
        ],
        "deliverables": [
            {"name": "Stakeholder Analysis Report", "type": "analysis", "required": True},
            {"name": "Change Readiness Assessment", "type": "assessment", "required": True},
            {"name": "Current State Analysis", "type": "baseline", "required": True},
            {"name": "Risk Assessment Matrix", "type": "assessment", "required": True},
            {"name": "Cultural Assessment Report", "type": "analysis", "required": True},
            {"name": "Technical Readiness Evaluation", "type": "assessment", "required": False}
        ],
        "tools": [
            "Stakeholder Analysis Template",
            "Change Readiness Assessment Survey",
            "Risk Assessment Matrix",
            "Cultural Assessment Framework",
            "Current State Analysis Tool"
        ],
        "completion_criteria": [
            "All stakeholders identified and analyzed",
            "Change readiness score of 3.5+ achieved or improvement plan established",
            "Current state baseline documented with improvement opportunities",
            "Critical risks identified with mitigation strategies",
            "Cultural factors mapped with engagement strategies"
        ],
        "universal_focus": "Understand the current organizational state and identify the specific factors that will impact transformation success for any type of change initiative."
    },
    "mobilize": {
        "name": "Mobilize & Prepare", 
        "description": "Building infrastructure and preparing for transformation success",
        "order": 2,
        "newton_law": "Second Law - Measuring Forces and Preparing for Acceleration",
        "newton_insight": "Acceleration equals force applied divided by organizational mass. Prepare the right resources and remove resistance to calculate required force accurately.",
        "objectives": [
            "Develop comprehensive change management strategy",
            "Establish governance structures and communication frameworks",
            "Create training and development programs for all stakeholders",
            "Build change champion networks across the organization",
            "Prepare measurement systems and success criteria"
        ],
        "key_activities": [
            "Develop detailed change management plan and strategy",
            "Create multi-channel communication strategy and materials",
            "Design role-based training programs for diverse audiences",
            "Establish change champion network covering all areas",
            "Develop success metrics and measurement frameworks",
            "Create resource allocation plans and timelines",
            "Establish issue escalation and support procedures"
        ],
        "deliverables": [
            {"name": "Change Management Plan", "type": "plan", "required": True},
            {"name": "Communication Strategy and Plan", "type": "plan", "required": True},
            {"name": "Training Program Design", "type": "plan", "required": True},
            {"name": "Change Champion Network Plan", "type": "plan", "required": True},
            {"name": "Success Metrics Framework", "type": "framework", "required": True},
            {"name": "Resource Allocation Plan", "type": "plan", "required": False}
        ],
        "tools": [
            "Change Management Plan Template",
            "Communication Plan Template", 
            "Training Strategy Framework",
            "Champion Network Development Guide",
            "Success Metrics Template"
        ],
        "completion_criteria": [
            "Comprehensive change plan approved by leadership",
            "Champion network established covering all key areas",
            "Communication strategy tested and validated with audiences",
            "Training materials developed and tested for effectiveness",
            "Success metrics defined and measurement systems prepared"
        ],
        "universal_focus": "Ensure all stakeholders understand the transformation objectives and benefits, and are prepared to support the change initiative with appropriate resources and capabilities."
    },
    "pilot": {
        "name": "Pilot & Adapt",
        "description": "Testing approach with limited group and refining strategies",
        "order": 3,
        "newton_law": "Third Law - Testing Action-Reaction in Controlled Environment", 
        "newton_insight": "For every action, there is an equal and opposite reaction. Test with pilot group to measure and understand resistance patterns before full deployment.",
        "objectives": [
            "Validate change strategies in real manufacturing environment",
            "Test maintenance-operations integration in controlled setting",
            "Identify and resolve issues before full-scale deployment", 
            "Build confidence through demonstrated maintenance excellence results",
            "Refine approaches based on manufacturing-specific feedback"
        ],
        "key_activities": [
            "Select representative pilot group from maintenance and operations",
            "Execute pilot implementation with intensive support",
            "Monitor pilot performance and gather comprehensive feedback",
            "Demonstrate connection between maintenance improvements and operational results", 
            "Capture lessons learned and refine strategies",
            "Develop success stories proving maintenance-manufacturing excellence connection",
            "Prepare scaling plan based on pilot learnings"
        ],
        "deliverables": [
            {"name": "Pilot Implementation Plan", "type": "plan", "required": True},
            {"name": "Pilot Results Analysis", "type": "analysis", "required": True},
            {"name": "Lessons Learned Report", "type": "report", "required": True},
            {"name": "Success Stories Documentation", "type": "documentation", "required": True},
            {"name": "Refined Implementation Strategy", "type": "strategy", "required": True},
            {"name": "Scaling Preparation Plan", "type": "plan", "required": False}
        ],
        "tools": [
            "Pilot Implementation Guide",
            "Pilot Feedback Collection Tools",
            "Performance Measurement Dashboard",
            "Success Story Template",
            "Strategy Refinement Framework"
        ],
        "completion_criteria": [
            "Pilot success metrics achieved demonstrating maintenance-operations benefits", 
            "Key learnings captured and strategies refined",
            "Pilot participants serve as advocates for full deployment",
            "Success stories document clear maintenance-manufacturing performance connection",
            "Scaling plan validated and approved"
        ],
        "manufacturing_focus": "Prove that maintenance improvements directly drive operational benefits in your specific manufacturing environment."
    },
    "activate": {
        "name": "Activate & Deploy",
        "description": "Full-scale implementation with comprehensive support",
        "order": 4,
        "newton_law": "Applied Force - Implementation in Motion",
        "newton_insight": "Apply consistent force to maintain momentum and overcome organizational inertia during full manufacturing implementation.",
        "objectives": [
            "Execute full-scale deployment across entire manufacturing organization",
            "Maintain momentum while managing resistance effectively", 
            "Ensure maintenance excellence becomes embedded in operations",
            "Track performance improvements and demonstrate manufacturing impact",
            "Provide intensive support during transition period"
        ],
        "key_activities": [
            "Launch full deployment with manufacturing-appropriate sequencing",
            "Execute comprehensive training across all shifts and departments",
            "Monitor adoption rates and performance metrics continuously",
            "Manage resistance with manufacturing-specific strategies",
            "Support maintenance and operations teams through transition",
            "Collect and communicate success stories regularly",
            "Maintain focus on maintenance-manufacturing excellence connection"
        ],
        "deliverables": [
            {"name": "Deployment Execution Plan", "type": "plan", "required": True},
            {"name": "Training Delivery Records", "type": "records", "required": True},
            {"name": "Performance Monitoring Reports", "type": "reports", "required": True},
            {"name": "Resistance Management Log", "type": "log", "required": True},
            {"name": "Success Communication Materials", "type": "materials", "required": True},
            {"name": "Manufacturing Impact Analysis", "type": "analysis", "required": False}
        ],
        "tools": [
            "Deployment Management Dashboard",
            "Resistance Management Toolkit", 
            "Performance Tracking System",
            "Communication Campaign Tools",
            "Manufacturing Metrics Monitor"
        ],
        "completion_criteria": [
            "90%+ user adoption achieved across maintenance and operations",
            "Manufacturing performance improvements documented and validated",
            "Resistance successfully managed with minimal operational disruption",
            "Training completion rates above 95% across all shifts",
            "Maintenance-operations collaboration demonstrably improved"
        ],
        "manufacturing_focus": "Ensure that maintenance excellence becomes embedded throughout the organization and drives measurable manufacturing performance improvements."
    },
    "cement": {
        "name": "Cement & Transfer",
        "description": "Institutionalizing change and transferring ownership",
        "order": 5,
        "newton_law": "Continuous Force Application for Sustainable Motion",
        "newton_insight": "Continuous force application prevents the organization from returning to its original state due to natural inertia.",
        "objectives": [
            "Institutionalize maintenance excellence as part of organizational culture",
            "Transfer ownership from implementation team to operational management",
            "Embed new practices in organizational systems and processes",
            "Establish sustainable maintenance-operations collaboration",
            "Create self-reinforcing systems for continuous improvement"
        ],
        "key_activities": [
            "Document and standardize new maintenance excellence practices",
            "Transfer knowledge and ownership to internal teams",
            "Integrate new practices into performance management systems",
            "Establish ongoing governance and oversight structures",
            "Create sustainability plans for maintenance excellence culture",
            "Implement internal capability development programs",
            "Establish mechanisms for continuous improvement"
        ],
        "deliverables": [
            {"name": "Process Documentation and Standards", "type": "documentation", "required": True},
            {"name": "Knowledge Transfer Plan", "type": "plan", "required": True},
            {"name": "Sustainability Framework", "type": "framework", "required": True},
            {"name": "Internal Capability Development Plan", "type": "plan", "required": True},
            {"name": "Governance Structure Documentation", "type": "documentation", "required": True},
            {"name": "Continuous Improvement Procedures", "type": "procedures", "required": False}
        ],
        "tools": [
            "Process Documentation Templates",
            "Knowledge Transfer Checklist",
            "Sustainability Planning Guide",
            "Governance Framework Template",
            "Continuous Improvement Toolkit"
        ],
        "completion_criteria": [
            "New practices fully documented and embedded in organizational systems",
            "Internal teams capable of sustaining maintenance excellence independently",
            "Performance management systems reflect maintenance-manufacturing connection",
            "Governance structures functioning effectively",
            "Continuous improvement culture established and functioning"
        ],
        "manufacturing_focus": "Ensure that the connection between maintenance excellence and operational performance becomes part of your organizational culture."
    },
    "track": {
        "name": "Track & Optimize",
        "description": "Long-term monitoring and continuous improvement",
        "order": 6,
        "newton_law": "New Equilibrium State with Continuous Optimization",
        "newton_insight": "The organization has reached a new equilibrium state with maintenance excellence integrated and sustainable, enabling continuous optimization.",
        "objectives": [
            "Monitor long-term performance and sustain improvements",
            "Validate implementation guarantee commitments",
            "Identify opportunities for additional manufacturing performance gains",
            "Share best practices and lessons learned",
            "Plan for future manufacturing excellence initiatives"
        ],
        "key_activities": [
            "Monitor KPIs and manufacturing performance metrics continuously",
            "Conduct regular assessment of maintenance excellence sustainability",
            "Identify and implement additional improvement opportunities",
            "Validate guarantee commitments and document achievement",
            "Share success stories and best practices across organization",
            "Plan for advanced maintenance excellence capabilities",
            "Establish long-term strategic planning for manufacturing excellence"
        ],
        "deliverables": [
            {"name": "Performance Monitoring Dashboard", "type": "dashboard", "required": True},
            {"name": "Guarantee Validation Report", "type": "report", "required": True},
            {"name": "Optimization Opportunities Analysis", "type": "analysis", "required": True},
            {"name": "Best Practices Documentation", "type": "documentation", "required": True},
            {"name": "Strategic Planning Report", "type": "report", "required": True},
            {"name": "ROI and Benefits Realization Report", "type": "report", "required": False}
        ],
        "tools": [
            "Performance Dashboard System",
            "Guarantee Validation Framework",
            "Optimization Analysis Tools",
            "Best Practice Capture Templates",
            "Strategic Planning Framework"
        ],
        "completion_criteria": [
            "All guarantee commitments met and validated",
            "Manufacturing performance improvements sustained over 12+ months",
            "Continuous improvement processes functioning effectively",
            "Organization recognized as maintenance excellence leader",
            "Strategic plan developed for future manufacturing excellence initiatives"
        ],
        "manufacturing_focus": "Demonstrate that maintenance excellence continues to drive manufacturing performance improvements and creates sustainable competitive advantage."
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

class ProjectPhase(BaseModel):
    phase_name: str
    phase_number: int
    status: str = "not_started"  # not_started, in_progress, completed, failed
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    completion_percentage: float = 0.0
    success_status: Optional[str] = None  # successful, failed, partially_successful
    success_reason: Optional[str] = None
    failure_reason: Optional[str] = None
    lessons_learned: Optional[str] = None
    budget_spent: float = 0.0
    scope_changes: List[str] = []
    recommendations: List[str] = []
    next_phase_suggestions: List[str] = []
    tasks: List[dict] = []
    deliverables: List[dict] = []
    risks_identified: List[str] = []
    mitigation_actions: List[str] = []

class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    description: Optional[str] = None
    client_organization: Optional[str] = None
    objectives: Optional[List[str]] = None
    scope: Optional[str] = None
    total_budget: Optional[float] = None
    estimated_end_date: Optional[str] = None
    current_phase: Optional[str] = None
    health_status: Optional[str] = None
    spent_budget: Optional[float] = None
    phases: Optional[List[ProjectPhase]] = None
    team_members: Optional[List[str]] = None
    stakeholders: Optional[List[str]] = None
    key_milestones: Optional[List[dict]] = None
    
class PhaseProgressUpdate(BaseModel):
    phase_name: str
    completion_percentage: float
    status: str
    success_status: Optional[str] = None
    success_reason: Optional[str] = None
    failure_reason: Optional[str] = None
    lessons_learned: Optional[str] = None
    budget_spent: float = 0.0
    scope_changes: Optional[List[str]] = None
    tasks_completed: Optional[List[str]] = None
    deliverables_completed: Optional[List[str]] = None
    risks_identified: Optional[List[str]] = None

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

class ManufacturingAssessmentDimension(BaseModel):
    name: str
    score: int = Field(ge=1, le=5)
    notes: Optional[str] = None
    category: str = "core"  # core, specialized
    improvement_actions: List[str] = []
    priority: str = "medium"  # low, medium, high
    impact_on_operations: Optional[float] = None
    current_state_description: Optional[str] = None
    target_state_description: Optional[str] = None
    responsible_stakeholders: List[str] = []
    dependencies: List[str] = []
    implementation_complexity: str = "medium"  # low, medium, high
    resource_requirements: Dict[str, Any] = {}
    success_criteria: List[str] = []
    risks: List[Dict[str, Any]] = []
    timeline_estimate: Optional[int] = None  # in weeks
    cost_estimate: Optional[float] = None
    roi_estimate: Optional[float] = None
    kpis: List[str] = []
    assessment_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    status: str = "pending"  # pending, in_progress, completed
    completion_percentage: float = 0.0
    actual_impact: Optional[float] = None
    lessons_learned: List[str] = []
    related_dimensions: List[str] = []

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

def calculate_universal_readiness_analysis(assessment_data: dict, assessment_type: str) -> Dict[str, Any]:
    """Calculate universal readiness analysis for any assessment type"""
    # Extract scores from assessment data
    scores = []
    dimension_scores = {}
    
    type_config = ASSESSMENT_TYPES.get(assessment_type, ASSESSMENT_TYPES["general_readiness"])
    
    for dimension in type_config["dimensions"]:
        dim_id = dimension["id"]
        if dim_id in assessment_data and "score" in assessment_data[dim_id]:
            score = assessment_data[dim_id]["score"]
            scores.append(score)
            dimension_scores[dim_id] = score
    
    avg_score = sum(scores) / len(scores) if scores else 0
    
    # Calculate organizational inertia based on type
    base_inertia = (5 - avg_score) * 20
    type_multiplier = {
        "software_implementation": 1.1,  # Slightly higher resistance to tech
        "business_process": 1.0,  # Standard resistance
        "manufacturing_operations": 1.2,  # Higher resistance in manufacturing
        "general_readiness": 1.0
    }.get(assessment_type, 1.0)
    
    organizational_inertia = base_inertia * type_multiplier
    
    # Calculate required force
    base_force = 100 - (avg_score * 15)
    force_required = base_force * type_multiplier
    
    # Calculate resistance
    resistance_magnitude = organizational_inertia * 0.8
    
    return {
        "inertia": {
            "value": round(organizational_inertia, 1),
            "interpretation": "Low" if organizational_inertia < 48 else "Medium" if organizational_inertia < 84 else "High",
            "description": f"Organization shows {'low' if organizational_inertia < 48 else 'medium' if organizational_inertia < 84 else 'high'} resistance to {assessment_type.replace('_', ' ')} changes"
        },
        "force": {
            "required": round(force_required, 1),
            "type_factor": round(type_multiplier, 1),
            "description": f"{'Low' if force_required < 60 else 'Medium' if force_required < 90 else 'High'} effort required for successful {assessment_type.replace('_', ' ')} transformation"
        },
        "reaction": {
            "resistance": round(resistance_magnitude, 1),
            "description": f"Expect {'minimal' if resistance_magnitude < 36 else 'moderate' if resistance_magnitude < 72 else 'significant'} organizational pushback"
        }
    }

def generate_typed_ai_analysis(assessment_data: dict, assessment_type: str, overall_score: float, readiness_level: str, analysis_data: dict) -> str:
    """Generate AI analysis based on assessment type"""
    
    type_names = {
        "general_readiness": "Change Management",
        "software_implementation": "Software Implementation", 
        "business_process": "Business Process Improvement",
        "manufacturing_operations": "Manufacturing Operations"
    }
    
    type_name = type_names.get(assessment_type, "Change Management")
    
    analysis = f"""# {type_name} Readiness Analysis

## Executive Summary
Your organization shows an overall readiness score of {overall_score:.1f}/5 for {type_name.lower()} projects.
Readiness Level: **{readiness_level}**

## Newton's Laws Application
- **Organizational Inertia**: {analysis_data['inertia']['value']} - {analysis_data['inertia']['interpretation']}
- **Required Force**: {analysis_data['force']['required']} units
- **Expected Resistance**: {analysis_data['reaction']['resistance']} units

## IMPACT Phase Recommendations
Based on your readiness assessment, focus areas for each phase:

**Investigate & Assess**: Understand current state and stakeholder landscape
**Mobilize & Prepare**: Build strong foundation and prepare resources
**Pilot & Adapt**: Test approach and refine strategies
**Activate & Deploy**: Execute with comprehensive support
**Cement & Transfer**: Institutionalize changes and transfer ownership
**Track & Optimize**: Monitor success and continuous improvement

## Strategic Recommendations
1. Focus on strengthening lowest-scoring dimensions
2. Build comprehensive stakeholder engagement strategy
3. Develop targeted training and communication programs
4. Establish clear success metrics and monitoring systems
5. Create change champion network for peer support

This assessment provides the foundation for your DigitalThinker implementation success."""

    return analysis

def generate_typed_recommendations(assessment_type: str, dimension_scores: dict, overall_score: float) -> List[str]:
    """Generate recommendations based on assessment type"""
    
    base_recommendations = [
        "Focus on strengthening lowest-scoring assessment dimensions",
        "Develop comprehensive change champion network",
        "Create clear communication strategy for all stakeholders",
        "Establish baseline performance metrics",
        "Design training programs for affected teams",
        "Build resistance management plan addressing organizational culture"
    ]
    
    type_specific = {
        "software_implementation": [
            "Ensure technical infrastructure readiness",
            "Plan comprehensive user training and support",
            "Develop data migration and integration strategy",
            "Create system performance monitoring protocols"
        ],
        "business_process": [
            "Document current process workflows and dependencies",
            "Establish process performance baselines", 
            "Design cross-functional collaboration frameworks",
            "Create process improvement measurement systems"
        ],
        "manufacturing_operations": [
            "Address shift work coordination challenges",
            "Leverage safety culture for change adoption",
            "Ensure maintenance-operations alignment",
            "Plan for operational constraint management"
        ]
    }
    
    recommendations = base_recommendations.copy()
    if assessment_type in type_specific:
        recommendations.extend(type_specific[assessment_type])
    
    return recommendations

def generate_week_by_week_plan(assessment_data: dict, assessment_type: str, overall_score: float) -> dict:
    """Generate tailored week-by-week implementation plan based on assessment results"""
    
    # Base 10-week implementation structure
    base_weeks = {
        1: {
            "week": 1,
            "phase": "Plan",
            "task_id": "task_1",
            "title": "Kick-off Week",
            "description": "Create Project Charter, detailed project plan, and establish core team members",
            "base_activities": [
                "Project Charter creation",
                "Detailed project planning",
                "Core team establishment",
                "Stakeholder identification"
            ],
            "deliverables": ["Project Charter", "Project Plan", "Team Charter"],
            "duration_hours": 40,
            "base_budget": 8000
        },
        2: {
            "week": 2,
            "phase": "Plan",
            "task_id": "task_2",
            "title": "Core Team Training",
            "description": "Hands-on training where participants experience full capabilities and limitations",
            "base_activities": [
                "Core team training delivery",
                "Hands-on system exploration",
                "Capability assessment",
                "Limitation identification"
            ],
            "deliverables": ["Training Materials", "Capability Assessment", "Team Readiness Report"],
            "duration_hours": 40,
            "base_budget": 6000
        },
        3: {
            "week": 3,
            "phase": "Plan",
            "task_id": "task_3",
            "title": "Business Process Review",
            "description": "Determine configuration regarding user groups, menus, permissions, and authorizations",
            "base_activities": [
                "Business process analysis",
                "User group definition",
                "Permission mapping",
                "Authorization framework"
            ],
            "deliverables": ["Business Process Document", "User Group Matrix", "Permission Framework"],
            "duration_hours": 40,
            "base_budget": 7000
        },
        4: {
            "week": 4,
            "phase": "Configure/Develop/Implement",
            "task_id": "task_4",
            "title": "Configuration & Data Preparation",
            "description": "Set installation parameters, build user groups, prepare data migration",
            "base_activities": [
                "System configuration",
                "User group creation",
                "Data extraction and mapping",
                "Migration preparation"
            ],
            "deliverables": ["Configuration Document", "Data Mapping", "Migration Plan"],
            "duration_hours": 45,
            "base_budget": 9000
        },
        5: {
            "week": 5,
            "phase": "Configure/Develop/Implement",
            "task_id": "task_5",
            "title": "Configuration Completion & Data Loading",
            "description": "Complete configuration and load data into training environment",
            "base_activities": [
                "Configuration finalization",
                "Data validation",
                "Training environment setup",
                "Data loading execution"
            ],
            "deliverables": ["Final Configuration", "Data Validation Report", "Training Environment"],
            "duration_hours": 45,
            "base_budget": 8500
        },
        6: {
            "week": 6,
            "phase": "User Acceptance Testing",
            "task_id": "task_6",
            "title": "Pilot Testing",
            "description": "Pilot testing of functions in training environment by user groups",
            "base_activities": [
                "Pilot user selection",
                "Testing execution",
                "Issue identification",
                "Feedback collection"
            ],
            "deliverables": ["Pilot Test Results", "Issue Log", "User Feedback Report"],
            "duration_hours": 40,
            "base_budget": 6000
        },
        7: {
            "week": 7,
            "phase": "User Acceptance Testing",
            "task_id": "task_7",
            "title": "Configuration Modifications",
            "description": "Modify configuration based on pilot testing and prepare production",
            "base_activities": [
                "Configuration adjustments",
                "User experience optimization",
                "Production preparation",
                "Environment copying"
            ],
            "deliverables": ["Modified Configuration", "Production Environment", "Deployment Plan"],
            "duration_hours": 45,
            "base_budget": 7500
        },
        8: {
            "week": 8,
            "phase": "User Acceptance Testing",
            "task_id": "task_8",
            "title": "Production Setup & Training",
            "description": "Configure production environment and deliver end-user training",
            "base_activities": [
                "Production configuration",
                "Data loading production",
                "End-user training",
                "Role-based instruction"
            ],
            "deliverables": ["Production System", "Training Records", "User Competency Matrix"],
            "duration_hours": 50,
            "base_budget": 10000
        },
        9: {
            "week": 9,
            "phase": "Production Deployment",
            "task_id": "task_9",
            "title": "Go Live - Week 1",
            "description": "Initial go-live with intensive support and monitoring",
            "base_activities": [
                "Go-live execution",
                "Intensive support",
                "Issue resolution",
                "Performance monitoring"
            ],
            "deliverables": ["Go-Live Report", "Issue Resolution Log", "Performance Metrics"],
            "duration_hours": 60,
            "base_budget": 12000
        },
        10: {
            "week": 10,
            "phase": "Production Deployment",
            "task_id": "task_10",
            "title": "Go Live - Week 2",
            "description": "Continued go-live support and stabilization",
            "base_activities": [
                "Ongoing support",
                "System stabilization",
                "User assistance",
                "Success validation"
            ],
            "deliverables": ["Stabilization Report", "User Success Metrics", "Project Closure"],
            "duration_hours": 50,
            "base_budget": 8000
        }
    }
    
    # Apply assessment-based customizations
    customized_weeks = {}
    
    for week_num, week_data in base_weeks.items():
        customized_week = week_data.copy()
        
        # Apply readiness-based modifications
        if overall_score < 3.0:  # Low readiness
            customized_week["risk_level"] = "High"
            customized_week["duration_hours"] = int(week_data["duration_hours"] * 1.3)
            customized_week["base_budget"] = int(week_data["base_budget"] * 1.25)
            customized_week["additional_activities"] = get_low_readiness_activities(week_num, assessment_data)
        elif overall_score < 4.0:  # Medium readiness
            customized_week["risk_level"] = "Medium"
            customized_week["duration_hours"] = int(week_data["duration_hours"] * 1.1)
            customized_week["base_budget"] = int(week_data["base_budget"] * 1.1)
            customized_week["additional_activities"] = get_medium_readiness_activities(week_num, assessment_data)
        else:  # High readiness
            customized_week["risk_level"] = "Low"
            customized_week["duration_hours"] = week_data["duration_hours"]
            customized_week["base_budget"] = week_data["base_budget"]
            customized_week["additional_activities"] = get_high_readiness_activities(week_num, assessment_data)
        
        # Apply assessment type-specific modifications
        customized_week["type_specific_activities"] = get_type_specific_activities(week_num, assessment_type)
        
        # Add IMPACT phase alignment
        customized_week["impact_phase_alignment"] = get_impact_alignment(week_num, assessment_data)
        
        # Calculate final budget with contingency
        risk_multiplier = {"High": 1.2, "Medium": 1.1, "Low": 1.0}[customized_week["risk_level"]]
        customized_week["final_budget"] = int(customized_week["base_budget"] * risk_multiplier)
        
        customized_weeks[week_num] = customized_week
    
    # Generate summary metrics
    total_budget = sum(week["final_budget"] for week in customized_weeks.values())
    total_hours = sum(week["duration_hours"] for week in customized_weeks.values())
    
    return {
        "weeks": customized_weeks,
        "summary": {
            "total_weeks": 10,
            "total_budget": total_budget,
            "total_hours": total_hours,
            "overall_risk_level": "High" if overall_score < 3.0 else "Medium" if overall_score < 4.0 else "Low",
            "success_probability": calculate_success_probability(overall_score, assessment_data),
            "key_risk_factors": identify_key_risks(assessment_data),
            "critical_success_factors": identify_critical_success_factors(assessment_data)
        }
    }

def get_low_readiness_activities(week_num: int, assessment_data: dict) -> List[str]:
    """Additional activities for low readiness organizations"""
    activities_by_week = {
        1: ["Additional stakeholder alignment sessions", "Change resistance assessment", "Communication strategy enhancement"],
        2: ["Extended training sessions", "Change champion identification", "Readiness gap analysis"],
        3: ["Cultural assessment integration", "Additional process documentation", "Resistance point mapping"],
        4: ["Enhanced testing protocols", "Additional quality checks", "Risk mitigation planning"],
        5: ["Extended validation cycles", "Additional user feedback sessions", "Performance optimization"],
        6: ["Expanded pilot group", "Additional testing scenarios", "Enhanced support protocols"],
        7: ["Extended modification cycles", "Additional validation steps", "Risk assessment updates"],
        8: ["Enhanced training delivery", "Additional practice sessions", "Confidence building activities"],
        9: ["Intensive support protocols", "Additional monitoring systems", "Rapid response procedures"],
        10: ["Extended support period", "Additional stabilization activities", "Success reinforcement"]
    }
    return activities_by_week.get(week_num, [])

def get_medium_readiness_activities(week_num: int, assessment_data: dict) -> List[str]:
    """Additional activities for medium readiness organizations"""
    activities_by_week = {
        1: ["Stakeholder engagement optimization", "Communication plan refinement"],
        2: ["Training effectiveness measurement", "Change champion training"],
        3: ["Process optimization workshops", "Best practice integration"],
        4: ["Quality assurance protocols", "Performance baseline establishment"],
        5: ["User experience optimization", "Efficiency improvements"],
        6: ["Pilot success validation", "Feedback integration"],
        7: ["Configuration optimization", "User experience refinement"],
        8: ["Training reinforcement", "Competency validation"],
        9: ["Performance monitoring enhancement", "Success metric tracking"],
        10: ["Best practice documentation", "Continuous improvement planning"]
    }
    return activities_by_week.get(week_num, [])

def get_high_readiness_activities(week_num: int, assessment_data: dict) -> List[str]:
    """Additional activities for high readiness organizations"""
    activities_by_week = {
        1: ["Accelerated planning protocols", "Innovation opportunities identification"],
        2: ["Advanced capability exploration", "Best practice development"],
        3: ["Process excellence initiatives", "Innovation integration"],
        4: ["Advanced configuration options", "Optimization opportunities"],
        5: ["Performance enhancement features", "Advanced functionality"],
        6: ["Innovation pilot testing", "Advanced use case validation"],
        7: ["Advanced feature implementation", "Innovation integration"],
        8: ["Leadership development", "Advanced user empowerment"],
        9: ["Excellence achievement validation", "Success amplification"],
        10: ["Innovation showcase", "Excellence model development"]
    }
    return activities_by_week.get(week_num, [])

def get_type_specific_activities(week_num: int, assessment_type: str) -> List[str]:
    """Get activities specific to assessment type"""
    if assessment_type == "manufacturing_operations":
        return {
            1: ["Maintenance-operations alignment assessment", "Shift work coordination planning"],
            2: ["Manufacturing excellence training", "Operational impact education"],
            3: ["Maintenance process optimization", "Operations integration planning"],
            4: ["Manufacturing-specific configuration", "Operational workflow integration"],
            5: ["Production impact validation", "Operational efficiency testing"],
            6: ["Shift-based pilot testing", "Operations team validation"],
            7: ["Manufacturing optimization", "Operational workflow refinement"],
            8: ["Shift-based training delivery", "Operations team empowerment"],
            9: ["Manufacturing performance monitoring", "Operational excellence tracking"],
            10: ["Maintenance excellence validation", "Manufacturing performance optimization"]
        }.get(week_num, [])
    
    return []

def get_impact_alignment(week_num: int, assessment_data: dict) -> str:
    """Map weeks to IMPACT phases"""
    impact_mapping = {
        1: "Investigate & Assess",
        2: "Investigate & Assess", 
        3: "Mobilize & Prepare",
        4: "Mobilize & Prepare",
        5: "Pilot & Adapt",
        6: "Pilot & Adapt",
        7: "Activate & Deploy",
        8: "Activate & Deploy",
        9: "Cement & Transfer",
        10: "Track & Optimize"
    }
    return impact_mapping.get(week_num, "Unknown")

def calculate_success_probability(overall_score: float, assessment_data: dict) -> float:
    """Calculate implementation success probability"""
    base_probability = min(95, max(15, overall_score * 18))
    
    # Apply bonus factors based on specific strengths
    if assessment_data.get("leadership_support", 0) >= 4:
        base_probability += 5
    if assessment_data.get("resource_availability", 0) >= 4:
        base_probability += 5
    if assessment_data.get("change_management_maturity", 0) >= 4:
        base_probability += 5
    
    return min(95, base_probability)

def identify_key_risks(assessment_data: dict) -> List[str]:
    """Identify key risk factors based on assessment scores"""
    risks = []
    
    if assessment_data.get("leadership_support", 5) < 3:
        risks.append("Limited leadership engagement and support")
    if assessment_data.get("resource_availability", 5) < 3:
        risks.append("Insufficient resource allocation")
    if assessment_data.get("change_management_maturity", 5) < 3:
        risks.append("Low organizational change maturity")
    if assessment_data.get("communication_effectiveness", 5) < 3:
        risks.append("Inadequate communication infrastructure")
    if assessment_data.get("workforce_adaptability", 5) < 3:
        risks.append("Workforce resistance to change")
    
    return risks

def identify_critical_success_factors(assessment_data: dict) -> List[str]:
    """Identify critical success factors based on assessment"""
    factors = []
    
    if assessment_data.get("leadership_support", 0) >= 4:
        factors.append("Strong leadership commitment")
    if assessment_data.get("resource_availability", 0) >= 4:
        factors.append("Adequate resource allocation")
    if assessment_data.get("change_management_maturity", 0) >= 4:
        factors.append("High organizational change maturity")
    if assessment_data.get("communication_effectiveness", 0) >= 4:
        factors.append("Effective communication capabilities")
    if assessment_data.get("workforce_adaptability", 0) >= 4:
        factors.append("Adaptable workforce")
    
    return factors

# ====================================================================================
# ENHANCEMENT 2: PREDICTIVE ANALYTICS ENGINE
# ====================================================================================

def predict_task_success_probability(task_id: str, assessment_data: dict, overall_score: float) -> dict:
    """Predict success probability for specific implementation tasks"""
    
    # Task-specific risk factors based on DigitalThinker methodology
    task_risk_factors = {
        "task_1": {  # Kick-off Week
            "primary_factors": ["leadership_support", "stakeholder_engagement"],
            "base_risk": 0.15,
            "description": "Project Charter and team establishment",
            "critical_dependencies": ["Executive sponsorship", "Resource allocation"]
        },
        "task_2": {  # Core Team Training
            "primary_factors": ["resource_availability", "workforce_adaptability"],
            "base_risk": 0.20,
            "description": "Hands-on training and capability assessment",
            "critical_dependencies": ["Team availability", "Learning capacity"]
        },
        "task_3": {  # Business Process Review
            "primary_factors": ["change_management_maturity", "communication_effectiveness"],
            "base_risk": 0.35,
            "description": "Process analysis and configuration planning",
            "critical_dependencies": ["Process documentation", "Stakeholder engagement"]
        },
        "task_4": {  # EAM Configuration
            "primary_factors": ["technical_readiness", "resource_availability"],
            "base_risk": 0.25,
            "description": "System configuration and data preparation",
            "critical_dependencies": ["Technical expertise", "Data quality"]
        },
        "task_5": {  # Data Migration
            "primary_factors": ["technical_readiness", "change_management_maturity"],
            "base_risk": 0.40,
            "description": "Data loading and environment setup",
            "critical_dependencies": ["Data accuracy", "System stability"]
        },
        "task_6": {  # Pilot Testing
            "primary_factors": ["workforce_adaptability", "communication_effectiveness"],
            "base_risk": 0.30,
            "description": "User acceptance testing and feedback",
            "critical_dependencies": ["User engagement", "Feedback integration"]
        },
        "task_7": {  # Configuration Modifications
            "primary_factors": ["technical_readiness", "change_management_maturity"],
            "base_risk": 0.35,
            "description": "System refinement and optimization",
            "critical_dependencies": ["Technical agility", "Change adaptability"]
        },
        "task_8": {  # Production Setup & Training
            "primary_factors": ["workforce_adaptability", "resource_availability"],
            "base_risk": 0.25,
            "description": "Production deployment and user training",
            "critical_dependencies": ["Training effectiveness", "System readiness"]
        },
        "task_9": {  # Go Live - Week 1
            "primary_factors": ["leadership_support", "workforce_adaptability"],
            "base_risk": 0.45,
            "description": "Initial go-live with intensive support",
            "critical_dependencies": ["Support availability", "Issue resolution"]
        },
        "task_10": {  # Go Live - Week 2
            "primary_factors": ["change_management_maturity", "communication_effectiveness"],
            "base_risk": 0.35,
            "description": "Stabilization and success validation",
            "critical_dependencies": ["System stability", "User adoption"]
        }
    }
    
    if task_id not in task_risk_factors:
        return {"success_probability": 70.0, "risk_level": "Medium", "confidence": "Low"}
    
    task_info = task_risk_factors[task_id]
    
    # Calculate risk score based on primary factors
    factor_scores = []
    for factor in task_info["primary_factors"]:
        score = assessment_data.get(factor, 3.0)
        factor_scores.append(score)
    
    avg_factor_score = sum(factor_scores) / len(factor_scores)
    
    # Calculate success probability
    base_success = 100 - (task_info["base_risk"] * 100)
    readiness_adjustment = (avg_factor_score - 3.0) * 15  # ±15% per point from neutral
    overall_adjustment = (overall_score - 3.0) * 10  # ±10% per point from neutral
    
    success_probability = base_success + readiness_adjustment + overall_adjustment
    success_probability = max(10, min(95, success_probability))
    
    # Determine risk level
    if success_probability >= 80:
        risk_level = "Low"
    elif success_probability >= 60:
        risk_level = "Medium"
    else:
        risk_level = "High"
    
    return {
        "task_id": task_id,
        "task_description": task_info["description"],
        "success_probability": round(success_probability, 1),
        "risk_level": risk_level,
        "primary_factors": task_info["primary_factors"],
        "factor_scores": {factor: assessment_data.get(factor, 3.0) for factor in task_info["primary_factors"]},
        "critical_dependencies": task_info["critical_dependencies"],
        "confidence": "High" if len(factor_scores) >= 2 else "Medium"
    }

def predict_budget_overrun_risk(assessment_data: dict, overall_score: float, total_budget: float) -> dict:
    """Predict budget overrun risk based on assessment data and historical patterns"""
    
    # Risk factors that historically correlate with budget overruns
    budget_risk_factors = {
        "leadership_support": {
            "weight": 0.25,
            "impact": "Low leadership support leads to scope creep and rework"
        },
        "change_management_maturity": {
            "weight": 0.30,
            "impact": "Poor change management causes resistance and delays"
        },
        "resource_availability": {
            "weight": 0.20,
            "impact": "Inadequate resources require additional expertise"
        },
        "communication_effectiveness": {
            "weight": 0.15,
            "impact": "Poor communication leads to misunderstandings and rework"
        },
        "workforce_adaptability": {
            "weight": 0.10,
            "impact": "Low adaptability requires extended training and support"
        }
    }
    
    # Calculate weighted risk score
    weighted_risk = 0
    risk_details = []
    
    for factor, config in budget_risk_factors.items():
        score = assessment_data.get(factor, 3.0)
        risk_contribution = (3.0 - score) * config["weight"]  # Higher risk for lower scores
        weighted_risk += risk_contribution
        
        risk_details.append({
            "factor": factor,
            "score": score,
            "risk_contribution": round(risk_contribution, 2),
            "impact_description": config["impact"]
        })
    
    # Calculate overrun probability and amount
    base_overrun_rate = 0.15  # 15% base overrun rate
    risk_adjusted_rate = base_overrun_rate + (weighted_risk * 0.20)  # Up to 20% additional risk
    
    overrun_probability = min(80, max(5, risk_adjusted_rate * 100))
    expected_overrun_percentage = max(0, (weighted_risk * 25))  # Up to 25% overrun
    expected_overrun_amount = total_budget * (expected_overrun_percentage / 100)
    
    # Determine risk level
    if overrun_probability < 20:
        risk_level = "Low"
    elif overrun_probability < 40:
        risk_level = "Medium"
    else:
        risk_level = "High"
    
    return {
        "overrun_probability": round(overrun_probability, 1),
        "expected_overrun_percentage": round(expected_overrun_percentage, 1),
        "expected_overrun_amount": round(expected_overrun_amount, 2),
        "risk_level": risk_level,
        "total_budget": total_budget,
        "risk_adjusted_budget": round(total_budget + expected_overrun_amount, 2),
        "risk_factors": risk_details,
        "recommendations": generate_budget_risk_recommendations(risk_details)
    }

def predict_scope_creep_risk(assessment_data: dict, assessment_type: str) -> dict:
    """Predict scope creep risk based on assessment data and project type"""
    
    # Scope creep risk factors by assessment type
    scope_risk_patterns = {
        "general_readiness": {
            "high_risk_factors": ["change_management_maturity", "stakeholder_engagement"],
            "base_risk": 0.25,
            "typical_scope_additions": ["Additional training", "Extended pilot phase", "More stakeholder sessions"]
        },
        "software_implementation": {
            "high_risk_factors": ["technical_readiness", "change_management_maturity"],
            "base_risk": 0.35,
            "typical_scope_additions": ["Custom integrations", "Additional data migration", "Enhanced training"]
        },
        "business_process": {
            "high_risk_factors": ["change_management_maturity", "communication_effectiveness"],
            "base_risk": 0.30,
            "typical_scope_additions": ["Process redesign", "Additional documentation", "Change management activities"]
        },
        "manufacturing_operations": {
            "high_risk_factors": ["technical_readiness", "workforce_adaptability"],
            "base_risk": 0.40,
            "typical_scope_additions": ["Safety compliance", "Shift coordination", "Operations integration"]
        }
    }
    
    pattern = scope_risk_patterns.get(assessment_type, scope_risk_patterns["general_readiness"])
    
    # Calculate scope creep probability
    risk_scores = []
    for factor in pattern["high_risk_factors"]:
        score = assessment_data.get(factor, 3.0)
        risk_scores.append(3.0 - score)  # Higher risk for lower scores
    
    avg_risk_score = sum(risk_scores) / len(risk_scores)
    scope_creep_probability = (pattern["base_risk"] + avg_risk_score * 0.15) * 100
    scope_creep_probability = max(10, min(70, scope_creep_probability))
    
    # Determine scope impact
    if scope_creep_probability < 25:
        impact_level = "Low"
        expected_impact = "5-10% additional effort"
    elif scope_creep_probability < 45:
        impact_level = "Medium"
        expected_impact = "10-20% additional effort"
    else:
        impact_level = "High"
        expected_impact = "20-35% additional effort"
    
    return {
        "scope_creep_probability": round(scope_creep_probability, 1),
        "impact_level": impact_level,
        "expected_impact": expected_impact,
        "high_risk_factors": pattern["high_risk_factors"],
        "factor_scores": {factor: assessment_data.get(factor, 3.0) for factor in pattern["high_risk_factors"]},
        "typical_scope_additions": pattern["typical_scope_additions"],
        "mitigation_strategies": generate_scope_creep_mitigation(pattern["high_risk_factors"], assessment_data)
    }

def predict_timeline_optimization(assessment_data: dict, overall_score: float) -> dict:
    """Predict timeline optimization opportunities based on organizational readiness"""
    
    # Timeline factors that can accelerate or delay implementation
    timeline_factors = {
        "leadership_support": {
            "acceleration_potential": 0.15,
            "delay_risk": 0.20,
            "impact": "Strong leadership can accelerate decisions and approvals"
        },
        "resource_availability": {
            "acceleration_potential": 0.10,
            "delay_risk": 0.25,
            "impact": "Adequate resources prevent delays and bottlenecks"
        },
        "change_management_maturity": {
            "acceleration_potential": 0.20,
            "delay_risk": 0.30,
            "impact": "High maturity enables faster adoption and fewer iterations"
        },
        "workforce_adaptability": {
            "acceleration_potential": 0.15,
            "delay_risk": 0.15,
            "impact": "Adaptable workforce learns faster and requires less support"
        }
    }
    
    total_acceleration = 0
    total_delay_risk = 0
    optimization_opportunities = []
    
    for factor, config in timeline_factors.items():
        score = assessment_data.get(factor, 3.0)
        
        if score >= 4:
            # High score enables acceleration
            acceleration = config["acceleration_potential"] * (score - 3)
            total_acceleration += acceleration
            optimization_opportunities.append({
                "factor": factor,
                "opportunity": "Acceleration",
                "impact": f"{acceleration:.1%} faster",
                "description": config["impact"]
            })
        elif score < 3:
            # Low score causes delays
            delay = config["delay_risk"] * (3 - score)
            total_delay_risk += delay
            optimization_opportunities.append({
                "factor": factor,
                "opportunity": "Risk Mitigation",
                "impact": f"{delay:.1%} slower without intervention",
                "description": config["impact"]
            })
    
    # Calculate net timeline impact
    net_timeline_impact = total_acceleration - total_delay_risk
    
    if net_timeline_impact > 0.10:
        timeline_outlook = "Accelerated"
        expected_timeline = "2-3 weeks faster than standard"
    elif net_timeline_impact > 0:
        timeline_outlook = "Optimized"
        expected_timeline = "On schedule or slightly faster"
    elif net_timeline_impact > -0.10:
        timeline_outlook = "Standard"
        expected_timeline = "Standard 10-week timeline"
    else:
        timeline_outlook = "At Risk"
        expected_timeline = "1-2 weeks additional time may be needed"
    
    return {
        "timeline_outlook": timeline_outlook,
        "expected_timeline": expected_timeline,
        "net_timeline_impact": round(net_timeline_impact, 2),
        "acceleration_potential": round(total_acceleration, 2),
        "delay_risk": round(total_delay_risk, 2),
        "optimization_opportunities": optimization_opportunities,
        "recommendations": generate_timeline_optimization_recommendations(optimization_opportunities)
    }

def generate_predictive_risk_trending(assessment_data: dict, overall_score: float) -> dict:
    """Generate risk trending analysis for ongoing project monitoring"""
    
    # Risk categories and their trending patterns
    risk_categories = {
        "Technical Risk": {
            "factors": ["technical_readiness", "resource_availability"],
            "trend_pattern": "Decreases over time with proper preparation",
            "peak_weeks": [4, 5, 7]  # Configuration and data migration weeks
        },
        "Adoption Risk": {
            "factors": ["workforce_adaptability", "change_management_maturity"],
            "trend_pattern": "Increases during training, decreases post go-live",
            "peak_weeks": [6, 8, 9]  # Testing and go-live weeks
        },
        "Stakeholder Risk": {
            "factors": ["leadership_support", "communication_effectiveness"],
            "trend_pattern": "Constant vigilance required throughout project",
            "peak_weeks": [1, 3, 9]  # Kickoff, process review, go-live
        },
        "Resource Risk": {
            "factors": ["resource_availability", "leadership_support"],
            "trend_pattern": "Typically increases toward go-live",
            "peak_weeks": [8, 9, 10]  # Training and go-live weeks
        }
    }
    
    risk_trends = []
    
    for category, config in risk_categories.items():
        # Calculate category risk level
        category_scores = [assessment_data.get(factor, 3.0) for factor in config["factors"]]
        category_avg = sum(category_scores) / len(category_scores)
        
        risk_level = "High" if category_avg < 2.5 else "Medium" if category_avg < 3.5 else "Low"
        
        risk_trends.append({
            "category": category,
            "current_risk_level": risk_level,
            "factor_scores": {factor: assessment_data.get(factor, 3.0) for factor in config["factors"]},
            "trend_pattern": config["trend_pattern"],
            "peak_weeks": config["peak_weeks"],
            "monitoring_recommendations": generate_risk_monitoring_recommendations(category, risk_level)
        })
    
    return {
        "overall_risk_score": round(overall_score, 2),
        "risk_trends": risk_trends,
        "critical_monitoring_weeks": list(set([week for trend in risk_trends for week in trend["peak_weeks"]])),
        "early_warning_indicators": generate_early_warning_indicators(risk_trends)
    }

def generate_budget_risk_recommendations(risk_details: List[dict]) -> List[str]:
    """Generate specific recommendations for budget risk mitigation"""
    recommendations = []
    
    for risk in risk_details:
        if risk["risk_contribution"] > 0.15:
            if risk["factor"] == "leadership_support":
                recommendations.append("Establish executive steering committee with clear decision-making authority")
            elif risk["factor"] == "change_management_maturity":
                recommendations.append("Implement comprehensive change management program with dedicated resources")
            elif risk["factor"] == "resource_availability":
                recommendations.append("Secure dedicated team members and establish contingency resource pool")
            elif risk["factor"] == "communication_effectiveness":
                recommendations.append("Develop robust communication plan with multiple channels and feedback loops")
            elif risk["factor"] == "workforce_adaptability":
                recommendations.append("Invest in early adopter identification and change champion development")
    
    return recommendations

def generate_scope_creep_mitigation(high_risk_factors: List[str], assessment_data: dict) -> List[str]:
    """Generate specific mitigation strategies for scope creep"""
    strategies = []
    
    for factor in high_risk_factors:
        score = assessment_data.get(factor, 3.0)
        if score < 3:
            if factor == "change_management_maturity":
                strategies.append("Implement formal change control process with approval gates")
            elif factor == "stakeholder_engagement":
                strategies.append("Establish clear stakeholder roles and communication protocols")
            elif factor == "technical_readiness":
                strategies.append("Conduct thorough technical assessment and establish boundaries")
            elif factor == "communication_effectiveness":
                strategies.append("Create detailed project charter with explicit scope boundaries")
    
    return strategies

def generate_timeline_optimization_recommendations(opportunities: List[dict]) -> List[str]:
    """Generate timeline optimization recommendations"""
    recommendations = []
    
    for opp in opportunities:
        if opp["opportunity"] == "Acceleration":
            recommendations.append(f"Leverage {opp['factor']} strength to accelerate project phases")
        elif opp["opportunity"] == "Risk Mitigation":
            recommendations.append(f"Address {opp['factor']} weakness to prevent timeline delays")
    
    return recommendations

def generate_risk_monitoring_recommendations(category: str, risk_level: str) -> List[str]:
    """Generate risk monitoring recommendations by category"""
    recommendations = []
    
    if risk_level == "High":
        recommendations.append(f"Implement daily monitoring for {category}")
        recommendations.append(f"Establish escalation procedures for {category}")
    elif risk_level == "Medium":
        recommendations.append(f"Monitor {category} weekly with regular checkpoints")
    else:
        recommendations.append(f"Standard monitoring for {category} is sufficient")
    
    return recommendations

def generate_early_warning_indicators(risk_trends: List[dict]) -> List[str]:
    """Generate early warning indicators for project monitoring"""
    indicators = []
    
    for trend in risk_trends:
        if trend["current_risk_level"] == "High":
            indicators.append(f"Monitor {trend['category']} closely during weeks {trend['peak_weeks']}")
    
    return indicators

# ====================================================================================
# ENHANCEMENT 3: DETAILED PROJECT MANAGEMENT WITH BUDGET TRACKING
# ====================================================================================

def generate_detailed_budget_tracking(project_data: dict, assessment_data: dict, implementation_plan: dict) -> dict:
    """Generate detailed task-level and phase-level budget tracking"""
    
    # Extract implementation plan weeks for budget analysis
    weeks = implementation_plan.get("weeks", {})
    
    # Calculate task-level budget breakdown
    task_level_budgets = []
    phase_level_budgets = {}
    
    for week_num, week_data in weeks.items():
        task_budget = {
            "week": int(week_num),
            "task_id": week_data.get("task_id", f"task_{week_num}"),
            "task_name": week_data.get("title", ""),
            "phase": week_data.get("phase", ""),
            "budgeted_amount": week_data.get("final_budget", 0),
            "spent_amount": 0,  # To be updated as project progresses
            "remaining_amount": week_data.get("final_budget", 0),
            "variance": 0,
            "variance_percentage": 0,
            "risk_level": week_data.get("risk_level", "Medium"),
            "completion_percentage": 0,
            "burn_rate": 0,
            "projected_final_cost": week_data.get("final_budget", 0),
            "cost_performance_index": 1.0,
            "budget_alerts": []
        }
        task_level_budgets.append(task_budget)
        
        # Aggregate by phase
        phase = week_data.get("phase", "Unknown")
        if phase not in phase_level_budgets:
            phase_level_budgets[phase] = {
                "phase_name": phase,
                "total_budgeted": 0,
                "total_spent": 0,
                "total_remaining": 0,
                "variance": 0,
                "variance_percentage": 0,
                "completion_percentage": 0,
                "risk_level": "Low",
                "tasks_count": 0,
                "on_track_tasks": 0,
                "at_risk_tasks": 0,
                "overrun_tasks": 0
            }
        
        phase_level_budgets[phase]["total_budgeted"] += week_data.get("final_budget", 0)
        phase_level_budgets[phase]["total_remaining"] += week_data.get("final_budget", 0)
        phase_level_budgets[phase]["tasks_count"] += 1
        
        if week_data.get("risk_level") == "Low":
            phase_level_budgets[phase]["on_track_tasks"] += 1
        elif week_data.get("risk_level") == "High":
            phase_level_budgets[phase]["at_risk_tasks"] += 1
    
    # Calculate overall project budget metrics
    total_budgeted = sum(task["budgeted_amount"] for task in task_level_budgets)
    total_spent = sum(task["spent_amount"] for task in task_level_budgets)
    total_remaining = total_budgeted - total_spent
    
    # Generate budget alerts
    budget_alerts = generate_budget_alerts(task_level_budgets, phase_level_budgets, total_budgeted, total_spent)
    
    # Calculate cost performance metrics
    cost_performance = calculate_cost_performance_metrics(task_level_budgets, total_budgeted, total_spent)
    
    return {
        "project_id": project_data.get("id", ""),
        "project_name": project_data.get("project_name", ""),
        "budget_tracking": {
            "task_level_budgets": task_level_budgets,
            "phase_level_budgets": list(phase_level_budgets.values()),
            "overall_metrics": {
                "total_budgeted": total_budgeted,
                "total_spent": total_spent,
                "total_remaining": total_remaining,
                "budget_utilization": (total_spent / total_budgeted * 100) if total_budgeted > 0 else 0,
                "projected_final_cost": cost_performance["projected_final_cost"],
                "cost_variance": total_spent - total_budgeted,
                "cost_variance_percentage": ((total_spent - total_budgeted) / total_budgeted * 100) if total_budgeted > 0 else 0,
                "cost_performance_index": cost_performance["cost_performance_index"],
                "budget_health": cost_performance["budget_health"]
            }
        },
        "budget_alerts": budget_alerts,
        "cost_forecasting": cost_performance["forecasting"],
        "generated_at": datetime.utcnow()
    }

def generate_budget_alerts(task_budgets: List[dict], phase_budgets: List[dict], total_budgeted: float, total_spent: float) -> List[dict]:
    """Generate real-time budget alerts based on spending patterns"""
    alerts = []
    
    # Overall budget alerts
    utilization = (total_spent / total_budgeted * 100) if total_budgeted > 0 else 0
    
    if utilization > 90:
        alerts.append({
            "type": "Critical",
            "category": "Overall Budget",
            "severity": "High",
            "message": f"Project budget {utilization:.1f}% utilized - immediate action required",
            "recommended_action": "Implement emergency cost controls and review remaining scope",
            "threshold": 90,
            "current_value": utilization
        })
    elif utilization > 75:
        alerts.append({
            "type": "Warning",
            "category": "Overall Budget", 
            "severity": "Medium",
            "message": f"Project budget {utilization:.1f}% utilized - monitor closely",
            "recommended_action": "Review upcoming expenses and optimize resource allocation",
            "threshold": 75,
            "current_value": utilization
        })
    
    # Task-level alerts
    for task in task_budgets:
        if task["risk_level"] == "High" and task["budgeted_amount"] > 5000:  # High-value, high-risk tasks
            alerts.append({
                "type": "Risk",
                "category": "Task Budget",
                "severity": "Medium",
                "message": f"High-risk task '{task['task_name']}' requires attention (${task['budgeted_amount']:,.0f} budget)",
                "recommended_action": "Implement additional oversight and controls for this task",
                "task_id": task["task_id"],
                "budgeted_amount": task["budgeted_amount"]
            })
    
    # Phase-level alerts
    for phase in phase_budgets:
        if phase["at_risk_tasks"] > phase["on_track_tasks"]:
            alerts.append({
                "type": "Risk",
                "category": "Phase Budget",
                "severity": "Medium",
                "message": f"Phase '{phase['phase_name']}' has more at-risk tasks ({phase['at_risk_tasks']}) than on-track tasks ({phase['on_track_tasks']})",
                "recommended_action": "Focus additional resources on this phase",
                "phase_name": phase["phase_name"],
                "at_risk_tasks": phase["at_risk_tasks"]
            })
    
    return alerts

def calculate_cost_performance_metrics(task_budgets: List[dict], total_budgeted: float, total_spent: float) -> dict:
    """Calculate advanced cost performance metrics"""
    
    # Cost Performance Index (CPI)
    earned_value = sum(task["budgeted_amount"] * (task["completion_percentage"] / 100) for task in task_budgets)
    cpi = earned_value / total_spent if total_spent > 0 else 1.0
    
    # Estimate at Completion (EAC)
    eac = total_budgeted / cpi if cpi > 0 else total_budgeted
    
    # Variance at Completion (VAC)
    vac = total_budgeted - eac
    
    # Budget health assessment
    if cpi >= 1.1:
        budget_health = "Excellent"
    elif cpi >= 0.95:
        budget_health = "Good"
    elif cpi >= 0.85:
        budget_health = "Concerning"
    else:
        budget_health = "Critical"
    
    return {
        "cost_performance_index": round(cpi, 2),
        "projected_final_cost": round(eac, 2),
        "variance_at_completion": round(vac, 2),
        "budget_health": budget_health,
        "forecasting": {
            "estimated_final_cost": round(eac, 2),
            "cost_overrun_risk": max(0, round((eac - total_budgeted) / total_budgeted * 100, 1)) if total_budgeted > 0 else 0,
            "funds_remaining": max(0, round(total_budgeted - eac, 2)),
            "performance_trend": "Above Budget" if cpi < 0.95 else "On Budget" if cpi < 1.05 else "Under Budget"
        }
    }

def generate_advanced_project_forecasting(project_data: dict, assessment_data: dict, predictive_analytics: dict, budget_tracking: dict) -> dict:
    """Generate advanced project outcome forecasting"""
    
    # Extract key metrics
    overall_score = assessment_data.get("overall_score", 3.0)
    success_probability = predictive_analytics.get("project_outlook", {}).get("success_probability", 70)
    budget_health = budget_tracking.get("budget_tracking", {}).get("overall_metrics", {}).get("budget_health", "Good")
    
    # Calculate delivery confidence
    delivery_factors = {
        "technical_readiness": assessment_data.get("technical_readiness", 3.0),
        "resource_availability": assessment_data.get("resource_availability", 3.0),
        "stakeholder_engagement": assessment_data.get("stakeholder_engagement", 3.0),
        "change_management_maturity": assessment_data.get("change_management_maturity", 3.0)
    }
    
    delivery_confidence = sum(delivery_factors.values()) / len(delivery_factors) * 20  # Convert to percentage
    delivery_confidence = max(20, min(95, delivery_confidence))
    
    # Predict final delivery outcomes
    outcomes = {
        "on_time_probability": calculate_timeline_probability(assessment_data, budget_health),
        "on_budget_probability": calculate_budget_probability(assessment_data, budget_health),
        "scope_completion_probability": calculate_scope_probability(assessment_data),
        "quality_achievement_probability": calculate_quality_probability(assessment_data),
        "stakeholder_satisfaction_probability": calculate_satisfaction_probability(assessment_data)
    }
    
    # Calculate overall project success score
    overall_success_score = (
        outcomes["on_time_probability"] * 0.25 +
        outcomes["on_budget_probability"] * 0.25 +
        outcomes["scope_completion_probability"] * 0.20 +
        outcomes["quality_achievement_probability"] * 0.15 +
        outcomes["stakeholder_satisfaction_probability"] * 0.15
    )
    
    # Generate success recommendations
    recommendations = generate_success_recommendations(outcomes, assessment_data)
    
    # Manufacturing excellence correlation
    manufacturing_correlation = calculate_manufacturing_excellence_correlation(assessment_data, outcomes)
    
    return {
        "project_id": project_data.get("id", ""),
        "forecasting_confidence": round(delivery_confidence, 1),
        "overall_success_score": round(overall_success_score, 1),
        "delivery_outcomes": {
            "on_time_delivery": round(outcomes["on_time_probability"], 1),
            "budget_compliance": round(outcomes["on_budget_probability"], 1),
            "scope_completion": round(outcomes["scope_completion_probability"], 1),
            "quality_achievement": round(outcomes["quality_achievement_probability"], 1),
            "stakeholder_satisfaction": round(outcomes["stakeholder_satisfaction_probability"], 1)
        },
        "success_drivers": identify_success_drivers(assessment_data),
        "risk_mitigations": identify_risk_mitigations(assessment_data, outcomes),
        "manufacturing_excellence": manufacturing_correlation,
        "recommendations": recommendations,
        "confidence_level": "High" if delivery_confidence > 80 else "Medium" if delivery_confidence > 60 else "Low",
        "generated_at": datetime.utcnow()
    }

def generate_stakeholder_communications(project_data: dict, budget_tracking: dict, project_forecasting: dict, assessment_data: dict) -> dict:
    """Generate automated stakeholder communication content"""
    
    # Determine communication urgency and tone
    budget_health = budget_tracking.get("budget_tracking", {}).get("overall_metrics", {}).get("budget_health", "Good")
    success_score = project_forecasting.get("overall_success_score", 70)
    budget_alerts = budget_tracking.get("budget_alerts", [])
    
    # Generate executive summary
    executive_summary = generate_executive_summary(project_data, budget_health, success_score, budget_alerts)
    
    # Generate detailed status report
    detailed_report = generate_detailed_status_report(project_data, budget_tracking, project_forecasting)
    
    # Generate stakeholder-specific messages
    stakeholder_messages = {
        "executive_leadership": generate_executive_message(executive_summary, budget_health, success_score),
        "project_team": generate_team_message(project_data, budget_tracking, project_forecasting),
        "client_stakeholders": generate_client_message(project_data, success_score, project_forecasting),
        "technical_teams": generate_technical_message(budget_tracking, assessment_data)
    }
    
    # Generate alert notifications
    alert_notifications = generate_alert_notifications(budget_alerts, success_score)
    
    return {
        "project_id": project_data.get("id", ""),
        "communication_date": datetime.utcnow(),
        "executive_summary": executive_summary,
        "detailed_report": detailed_report,
        "stakeholder_messages": stakeholder_messages,
        "alert_notifications": alert_notifications,
        "recommended_frequency": determine_communication_frequency(budget_health, success_score),
        "next_communication_date": calculate_next_communication_date(budget_health, success_score),
        "escalation_required": len([alert for alert in budget_alerts if alert.get("severity") == "High"]) > 0
    }

# Helper functions for advanced forecasting
def calculate_timeline_probability(assessment_data: dict, budget_health: str) -> float:
    baseline = 75
    if assessment_data.get("resource_availability", 3) >= 4:
        baseline += 10
    if assessment_data.get("change_management_maturity", 3) >= 4:
        baseline += 10
    if budget_health in ["Critical", "Concerning"]:
        baseline -= 15
    return max(30, min(95, baseline))

def calculate_budget_probability(assessment_data: dict, budget_health: str) -> float:
    if budget_health == "Excellent":
        return 90
    elif budget_health == "Good":
        return 80
    elif budget_health == "Concerning":
        return 60
    else:
        return 40

def calculate_scope_probability(assessment_data: dict) -> float:
    baseline = 80
    if assessment_data.get("stakeholder_engagement", 3) >= 4:
        baseline += 10
    if assessment_data.get("change_management_maturity", 3) < 3:
        baseline -= 15
    return max(50, min(95, baseline))

def calculate_quality_probability(assessment_data: dict) -> float:
    baseline = 85
    if assessment_data.get("technical_readiness", 3) >= 4:
        baseline += 10
    if assessment_data.get("resource_availability", 3) < 3:
        baseline -= 10
    return max(60, min(95, baseline))

def calculate_satisfaction_probability(assessment_data: dict) -> float:
    baseline = 75
    if assessment_data.get("communication_effectiveness", 3) >= 4:
        baseline += 15
    if assessment_data.get("stakeholder_engagement", 3) >= 4:
        baseline += 10
    return max(50, min(95, baseline))

def calculate_manufacturing_excellence_correlation(assessment_data: dict, outcomes: dict) -> dict:
    """Calculate correlation between project outcomes and manufacturing excellence"""
    
    # Manufacturing excellence factors
    maintenance_readiness = assessment_data.get("maintenance_operations_alignment", 3.0)
    operational_impact = (outcomes["quality_achievement_probability"] + outcomes["scope_completion_probability"]) / 2
    
    # Calculate correlation strength
    correlation_strength = min(1.0, (maintenance_readiness / 5.0) * (operational_impact / 100))
    
    return {
        "correlation_strength": round(correlation_strength, 2),
        "maintenance_excellence_potential": round(maintenance_readiness * 20, 1),
        "operational_performance_impact": round(operational_impact, 1),
        "manufacturing_readiness": "High" if maintenance_readiness >= 4 else "Medium" if maintenance_readiness >= 3 else "Low",
        "excellence_pathway": generate_excellence_pathway(maintenance_readiness, operational_impact)
    }

def generate_excellence_pathway(maintenance_readiness: float, operational_impact: float) -> List[str]:
    """Generate pathway to manufacturing excellence"""
    pathway = []
    
    if maintenance_readiness >= 4:
        pathway.append("Strong foundation for maintenance excellence established")
    else:
        pathway.append("Focus on building maintenance-operations alignment")
    
    if operational_impact >= 80:
        pathway.append("High potential for operational performance improvements")
    else:
        pathway.append("Develop operational excellence capabilities")
    
    pathway.append("Implement continuous improvement processes")
    pathway.append("Measure and track manufacturing performance metrics")
    
    return pathway

def generate_success_recommendations(outcomes: dict, assessment_data: dict) -> List[str]:
    """Generate specific recommendations for project success"""
    recommendations = []
    
    if outcomes["on_time_probability"] < 70:
        recommendations.append("Implement accelerated timeline recovery plan")
    
    if outcomes["on_budget_probability"] < 70:
        recommendations.append("Activate budget control measures immediately")
    
    if outcomes["stakeholder_satisfaction_probability"] < 70:
        recommendations.append("Enhance stakeholder engagement and communication")
    
    return recommendations

def identify_success_drivers(assessment_data: dict) -> List[str]:
    """Identify key success drivers for the project"""
    drivers = []
    
    if assessment_data.get("leadership_support", 3) >= 4:
        drivers.append("Strong leadership commitment")
    if assessment_data.get("resource_availability", 3) >= 4:
        drivers.append("Adequate resource allocation")
    if assessment_data.get("change_management_maturity", 3) >= 4:
        drivers.append("High change management maturity")
    
    return drivers

def identify_risk_mitigations(assessment_data: dict, outcomes: dict) -> List[str]:
    """Identify specific risk mitigation strategies"""
    mitigations = []
    
    if outcomes["on_budget_probability"] < 70:
        mitigations.append("Implement weekly budget review and approval process")
    
    if assessment_data.get("technical_readiness", 3) < 3:
        mitigations.append("Provide additional technical training and support")
    
    return mitigations

def generate_executive_summary(project_data: dict, budget_health: str, success_score: float, alerts: List[dict]) -> str:
    """Generate executive summary for stakeholder communications"""
    
    project_name = project_data.get("project_name", "Project")
    alert_count = len([alert for alert in alerts if alert.get("severity") in ["High", "Critical"]])
    
    summary = f"Project {project_name} Status Update:\n\n"
    summary += f"Overall Success Score: {success_score}%\n"
    summary += f"Budget Health: {budget_health}\n"
    
    if alert_count > 0:
        summary += f"Critical Alerts: {alert_count} requiring immediate attention\n"
    else:
        summary += "No critical issues identified\n"
    
    return summary

def generate_detailed_status_report(project_data: dict, budget_tracking: dict, forecasting: dict) -> str:
    """Generate detailed project status report"""
    
    budget_metrics = budget_tracking.get("budget_tracking", {}).get("overall_metrics", {})
    
    report = f"Detailed Project Status Report\n"
    report += f"="*50 + "\n\n"
    report += f"Budget Utilization: {budget_metrics.get('budget_utilization', 0):.1f}%\n"
    report += f"Cost Performance Index: {budget_metrics.get('cost_performance_index', 1.0)}\n"
    report += f"Projected Final Cost: ${budget_metrics.get('projected_final_cost', 0):,.0f}\n"
    report += f"Overall Success Probability: {forecasting.get('overall_success_score', 0):.1f}%\n"
    
    return report

def generate_executive_message(summary: str, budget_health: str, success_score: float) -> str:
    """Generate message for executive leadership"""
    message = f"Executive Leadership Update:\n\n{summary}\n"
    
    if budget_health in ["Critical", "Concerning"]:
        message += "Immediate executive attention required for budget situation.\n"
    
    return message

def generate_team_message(project_data: dict, budget_tracking: dict, forecasting: dict) -> str:
    """Generate message for project team"""
    return f"Team Update: Project progressing with focus on budget management and quality delivery."

def generate_client_message(project_data: dict, success_score: float, forecasting: dict) -> str:
    """Generate message for client stakeholders"""
    return f"Client Update: Project {project_data.get('project_name', '')} maintaining {success_score}% success probability."

def generate_technical_message(budget_tracking: dict, assessment_data: dict) -> str:
    """Generate message for technical teams"""
    return f"Technical Update: Focus on technical readiness and resource optimization."

def generate_alert_notifications(alerts: List[dict], success_score: float) -> List[dict]:
    """Generate structured alert notifications"""
    notifications = []
    
    for alert in alerts:
        notifications.append({
            "type": alert.get("type", "Info"),
            "severity": alert.get("severity", "Low"),
            "message": alert.get("message", ""),
            "action_required": alert.get("recommended_action", ""),
            "urgent": alert.get("severity") in ["High", "Critical"]
        })
    
    return notifications

def determine_communication_frequency(budget_health: str, success_score: float) -> str:
    """Determine recommended communication frequency"""
    if budget_health in ["Critical"] or success_score < 60:
        return "Daily"
    elif budget_health in ["Concerning"] or success_score < 75:
        return "Weekly"
    else:
        return "Bi-weekly"

def calculate_next_communication_date(budget_health: str, success_score: float) -> datetime:
    """Calculate next recommended communication date"""
    frequency = determine_communication_frequency(budget_health, success_score)
    
    if frequency == "Daily":
        return datetime.utcnow() + timedelta(days=1)
    elif frequency == "Weekly":
        return datetime.utcnow() + timedelta(weeks=1)
    else:
        return datetime.utcnow() + timedelta(weeks=2)

# ====================================================================================
# ENHANCEMENT 4: ADVANCED PROJECT WORKFLOW MANAGEMENT WITH PHASE-BASED INTELLIGENCE
# ====================================================================================

def generate_phase_based_intelligence(phase_name: str, assessment_data: dict, project_data: dict, completed_phases: List[dict] = None) -> dict:
    """Generate intelligent recommendations for each IMPACT phase based on assessment data and project context"""
    
    # Phase name mapping from short names to full names
    phase_name_mapping = {
        "investigate": "Investigate & Assess",
        "mobilize": "Mobilize & Prepare", 
        "pilot": "Pilot & Adapt",
        "activate": "Activate & Deploy",
        "cement": "Cement & Transfer",
        "track": "Track & Optimize"
    }
    
    # IMPACT phases mapping
    impact_phases = {
        "Investigate & Assess": {
            "phase_number": 1,
            "key_activities": ["Stakeholder analysis", "Current state assessment", "Gap analysis", "Risk identification"],
            "critical_success_factors": ["leadership_support", "stakeholder_engagement", "communication_effectiveness"],
            "typical_duration_weeks": 2,
            "budget_percentage": 15
        },
        "Mobilize & Prepare": {
            "phase_number": 2,
            "key_activities": ["Change management planning", "Team formation", "Communication strategy", "Training preparation"],
            "critical_success_factors": ["resource_availability", "change_management_maturity", "leadership_support"],
            "typical_duration_weeks": 2,
            "budget_percentage": 20
        },
        "Pilot & Adapt": {
            "phase_number": 3,
            "key_activities": ["Pilot implementation", "Testing and validation", "Feedback collection", "Strategy refinement"],
            "critical_success_factors": ["workforce_adaptability", "technical_readiness", "communication_effectiveness"],
            "typical_duration_weeks": 3,
            "budget_percentage": 25
        },
        "Activate & Deploy": {
            "phase_number": 4,
            "key_activities": ["Full deployment", "Training delivery", "Support systems", "Performance monitoring"],
            "critical_success_factors": ["workforce_adaptability", "resource_availability", "technical_readiness"],
            "typical_duration_weeks": 2,
            "budget_percentage": 25
        },
        "Cement & Transfer": {
            "phase_number": 5,
            "key_activities": ["Knowledge transfer", "Process documentation", "Sustainability planning", "Ownership transition"],
            "critical_success_factors": ["change_management_maturity", "leadership_support", "workforce_adaptability"],
            "typical_duration_weeks": 1,
            "budget_percentage": 10
        },
        "Track & Optimize": {
            "phase_number": 6,
            "key_activities": ["Performance monitoring", "Continuous improvement", "Best practice sharing", "Strategic planning"],
            "critical_success_factors": ["communication_effectiveness", "leadership_support", "change_management_maturity"],
            "typical_duration_weeks": 2,
            "budget_percentage": 5
        }
    }
    
    # Map short phase name to full name
    full_phase_name = phase_name_mapping.get(phase_name, phase_name)
    
    if full_phase_name not in impact_phases:
        return {"error": f"Unknown phase: {phase_name}"}
    
    phase_info = impact_phases[full_phase_name]
    
    # Calculate phase-specific recommendations based on assessment data
    phase_recommendations = generate_phase_recommendations(full_phase_name, assessment_data, project_data, phase_info)
    
    # Generate budget recommendations
    budget_recommendations = generate_phase_budget_recommendations(full_phase_name, assessment_data, project_data, phase_info)
    
    # Generate scope recommendations
    scope_recommendations = generate_phase_scope_recommendations(full_phase_name, assessment_data, project_data, phase_info)
    
    # Generate success probability for this phase
    phase_success_probability = calculate_phase_success_probability(full_phase_name, assessment_data, project_data, phase_info)
    
    # Generate risks and mitigation strategies
    phase_risks = identify_phase_risks(full_phase_name, assessment_data, project_data, phase_info)
    
    # Generate lessons learned from previous phases
    lessons_from_previous = extract_lessons_from_previous_phases(completed_phases) if completed_phases else []
    
    return {
        "phase_name": phase_name,  # Return original short name
        "full_phase_name": full_phase_name,  # Also return full name
        "phase_number": phase_info["phase_number"],
        "phase_intelligence": {
            "key_activities": phase_info["key_activities"],
            "critical_success_factors": phase_info["critical_success_factors"],
            "typical_duration_weeks": phase_info["typical_duration_weeks"],
            "budget_percentage": phase_info["budget_percentage"],
            "success_probability": phase_success_probability,
            "recommendations": phase_recommendations,
            "budget_recommendations": budget_recommendations,
            "scope_recommendations": scope_recommendations,
            "risks_and_mitigations": phase_risks,
            "lessons_from_previous": lessons_from_previous
        },
        "generated_at": datetime.utcnow()
    }

def generate_phase_recommendations(phase_name: str, assessment_data: dict, project_data: dict, phase_info: dict) -> List[str]:
    """Generate specific recommendations for each phase"""
    recommendations = []
    
    # Base recommendations for each phase
    base_recommendations = {
        "Investigate & Assess": [
            "Conduct comprehensive stakeholder mapping and engagement planning",
            "Establish baseline performance metrics and current state documentation",
            "Identify and prioritize key change management challenges",
            "Develop detailed communication strategy for all stakeholder groups"
        ],
        "Mobilize & Prepare": [
            "Form cross-functional project team with clear roles and responsibilities",
            "Develop comprehensive change management plan with timeline and milestones",
            "Create training program design tailored to different user groups",
            "Establish governance structure and decision-making processes"
        ],
        "Pilot & Adapt": [
            "Select representative pilot group that reflects broader organization",
            "Implement comprehensive testing and validation protocols",
            "Establish feedback collection mechanisms and rapid response processes",
            "Document lessons learned and adapt strategies based on pilot results"
        ],
        "Activate & Deploy": [
            "Execute full-scale deployment with comprehensive support systems",
            "Deliver role-based training to all affected users",
            "Implement performance monitoring and issue resolution processes",
            "Maintain intensive support during initial deployment period"
        ],
        "Cement & Transfer": [
            "Transfer knowledge and ownership to internal teams",
            "Document all processes and establish sustainable practices",
            "Develop internal change management capabilities",
            "Create sustainability plan for long-term success"
        ],
        "Track & Optimize": [
            "Implement continuous performance monitoring and measurement",
            "Identify and capture best practices for sharing",
            "Develop continuous improvement processes",
            "Plan for future enhancements and scaling opportunities"
        ]
    }
    
    recommendations.extend(base_recommendations.get(phase_name, []))
    
    # Add assessment-specific recommendations
    overall_score = assessment_data.get("overall_score", 3.0)
    
    for factor in phase_info["critical_success_factors"]:
        factor_score = assessment_data.get(factor, 3.0)
        if factor_score < 3.0:
            recommendations.append(generate_factor_specific_recommendation(factor, phase_name))
    
    # Add project-specific recommendations based on budget and scope
    total_budget = project_data.get("total_budget", 100000)
    if total_budget < 50000:
        recommendations.append(f"Given limited budget, focus on highest-impact activities for {phase_name}")
    elif total_budget > 200000:
        recommendations.append(f"Leverage substantial budget to implement comprehensive {phase_name} activities")
    
    return recommendations[:6]  # Limit to 6 recommendations

def generate_phase_budget_recommendations(phase_name: str, assessment_data: dict, project_data: dict, phase_info: dict) -> dict:
    """Generate budget recommendations for each phase"""
    total_budget = project_data.get("total_budget", 100000)
    phase_budget = total_budget * (phase_info["budget_percentage"] / 100)
    
    # Adjust based on assessment readiness
    overall_score = assessment_data.get("overall_score", 3.0)
    
    if overall_score < 2.5:
        budget_multiplier = 1.3  # Need more budget for low readiness
        risk_level = "High"
    elif overall_score < 3.5:
        budget_multiplier = 1.1  # Slight increase for medium readiness
        risk_level = "Medium"
    else:
        budget_multiplier = 1.0  # Standard budget for high readiness
        risk_level = "Low"
    
    recommended_budget = phase_budget * budget_multiplier
    
    return {
        "recommended_budget": round(recommended_budget, 2),
        "budget_percentage": phase_info["budget_percentage"],
        "risk_level": risk_level,
        "budget_multiplier": budget_multiplier,
        "budget_breakdown": generate_budget_breakdown(phase_name, recommended_budget),
        "contingency_percentage": 20 if risk_level == "High" else 15 if risk_level == "Medium" else 10
    }

def generate_phase_scope_recommendations(phase_name: str, assessment_data: dict, project_data: dict, phase_info: dict) -> List[str]:
    """Generate scope recommendations for each phase"""
    scope_recommendations = []
    
    # Base scope guidance
    scope_recommendations.append(f"Focus on core {phase_name} activities: {', '.join(phase_info['key_activities'][:2])}")
    
    # Assessment-based scope adjustments
    overall_score = assessment_data.get("overall_score", 3.0)
    
    if overall_score < 2.5:
        scope_recommendations.append("Consider reducing scope complexity due to organizational readiness challenges")
        scope_recommendations.append("Implement additional change management activities to address readiness gaps")
    elif overall_score > 4.0:
        scope_recommendations.append("Organization readiness allows for accelerated scope delivery")
        scope_recommendations.append("Consider adding value-enhancement activities within phase budget")
    
    return scope_recommendations

def calculate_phase_success_probability(phase_name: str, assessment_data: dict, project_data: dict, phase_info: dict) -> float:
    """Calculate success probability for specific phase"""
    base_probability = 75  # Base 75% success rate
    
    # Adjust based on critical success factors
    for factor in phase_info["critical_success_factors"]:
        factor_score = assessment_data.get(factor, 3.0)
        if factor_score >= 4:
            base_probability += 5
        elif factor_score < 3:
            base_probability -= 10
    
    # Adjust based on overall readiness
    overall_score = assessment_data.get("overall_score", 3.0)
    readiness_adjustment = (overall_score - 3.0) * 10
    
    final_probability = base_probability + readiness_adjustment
    return max(20, min(95, final_probability))

def identify_phase_risks(phase_name: str, assessment_data: dict, project_data: dict, phase_info: dict) -> List[dict]:
    """Identify risks and mitigation strategies for each phase"""
    risks = []
    
    # Phase-specific risks
    phase_risks = {
        "Investigate & Assess": [
            {"risk": "Incomplete stakeholder identification", "mitigation": "Conduct comprehensive stakeholder mapping exercise"},
            {"risk": "Resistance to current state assessment", "mitigation": "Emphasize improvement focus rather than criticism"},
            {"risk": "Inadequate baseline data", "mitigation": "Implement systematic data collection protocols"}
        ],
        "Mobilize & Prepare": [
            {"risk": "Insufficient resource allocation", "mitigation": "Secure executive commitment for dedicated resources"},
            {"risk": "Competing priorities", "mitigation": "Establish clear project governance and priority framework"},
            {"risk": "Team skill gaps", "mitigation": "Provide targeted training and external expertise"}
        ],
        "Pilot & Adapt": [
            {"risk": "Pilot group not representative", "mitigation": "Carefully select diverse, representative pilot participants"},
            {"risk": "Limited pilot feedback", "mitigation": "Implement multiple feedback channels and regular check-ins"},
            {"risk": "Resistance to changes", "mitigation": "Emphasize pilot nature and incorporate participant input"}
        ],
        "Activate & Deploy": [
            {"risk": "System performance issues", "mitigation": "Conduct thorough performance testing and optimization"},
            {"risk": "Training effectiveness", "mitigation": "Implement role-based training with competency validation"},
            {"risk": "Support system overload", "mitigation": "Scale support resources and implement tiered support model"}
        ],
        "Cement & Transfer": [
            {"risk": "Knowledge transfer gaps", "mitigation": "Implement systematic knowledge transfer protocols"},
            {"risk": "Sustainability challenges", "mitigation": "Develop comprehensive sustainability plan and internal capabilities"},
            {"risk": "Loss of momentum", "mitigation": "Maintain engagement through continuous improvement activities"}
        ],
        "Track & Optimize": [
            {"risk": "Measurement system gaps", "mitigation": "Implement comprehensive performance measurement framework"},
            {"risk": "Continuous improvement fatigue", "mitigation": "Balance improvement activities with operational stability"},
            {"risk": "Benefits realization delays", "mitigation": "Establish clear benefits tracking and reporting mechanisms"}
        ]
    }
    
    risks.extend(phase_risks.get(phase_name, []))
    
    # Add assessment-specific risks
    for factor in phase_info["critical_success_factors"]:
        factor_score = assessment_data.get(factor, 3.0)
        if factor_score < 3.0:
            risks.append({
                "risk": f"Low {factor.replace('_', ' ')} may impact {phase_name} success",
                "mitigation": generate_factor_mitigation(factor, phase_name)
            })
    
    return risks[:5]  # Limit to 5 key risks

def generate_factor_specific_recommendation(factor: str, phase_name: str) -> str:
    """Generate specific recommendations for assessment factors"""
    recommendations = {
        "leadership_support": f"Secure stronger leadership engagement for {phase_name} through executive briefings and governance participation",
        "resource_availability": f"Ensure adequate resource allocation for {phase_name} activities through detailed resource planning",
        "change_management_maturity": f"Enhance change management capabilities through training and methodology adoption for {phase_name}",
        "communication_effectiveness": f"Improve communication strategies and channels for {phase_name} stakeholder engagement",
        "workforce_adaptability": f"Develop workforce readiness for {phase_name} through targeted training and support",
        "technical_readiness": f"Strengthen technical capabilities and infrastructure for {phase_name} requirements",
        "stakeholder_engagement": f"Increase stakeholder participation and buy-in for {phase_name} activities"
    }
    
    return recommendations.get(factor, f"Address {factor.replace('_', ' ')} challenges for {phase_name} success")

def generate_factor_mitigation(factor: str, phase_name: str) -> str:
    """Generate mitigation strategies for assessment factors"""
    mitigations = {
        "leadership_support": f"Implement executive engagement plan with regular updates and decision points",
        "resource_availability": f"Develop resource sharing agreements and contingency resource plans",
        "change_management_maturity": f"Provide change management training and establish change champion network",
        "communication_effectiveness": f"Implement multi-channel communication strategy with feedback loops",
        "workforce_adaptability": f"Create comprehensive training program with ongoing support",
        "technical_readiness": f"Conduct technical readiness assessment and capability development",
        "stakeholder_engagement": f"Establish stakeholder engagement plan with regular touchpoints"
    }
    
    return mitigations.get(factor, f"Develop targeted improvement plan for {factor.replace('_', ' ')}")

def generate_budget_breakdown(phase_name: str, total_budget: float) -> dict:
    """Generate detailed budget breakdown for each phase"""
    breakdowns = {
        "Investigate & Assess": {
            "stakeholder_analysis": 0.25,
            "current_state_assessment": 0.30,
            "gap_analysis": 0.20,
            "documentation": 0.15,
            "risk_assessment": 0.10
        },
        "Mobilize & Prepare": {
            "team_formation": 0.20,
            "change_management_planning": 0.25,
            "communication_strategy": 0.20,
            "training_design": 0.25,
            "governance_setup": 0.10
        },
        "Pilot & Adapt": {
            "pilot_implementation": 0.40,
            "testing_validation": 0.25,
            "feedback_collection": 0.15,
            "strategy_refinement": 0.20
        },
        "Activate & Deploy": {
            "full_deployment": 0.35,
            "training_delivery": 0.30,
            "support_systems": 0.25,
            "performance_monitoring": 0.10
        },
        "Cement & Transfer": {
            "knowledge_transfer": 0.40,
            "process_documentation": 0.25,
            "sustainability_planning": 0.20,
            "ownership_transition": 0.15
        },
        "Track & Optimize": {
            "performance_monitoring": 0.30,
            "continuous_improvement": 0.25,
            "best_practice_sharing": 0.20,
            "strategic_planning": 0.25
        }
    }
    
    breakdown = breakdowns.get(phase_name, {"general_activities": 1.0})
    return {activity: round(total_budget * percentage, 2) for activity, percentage in breakdown.items()}

def extract_lessons_from_previous_phases(completed_phases: List[dict]) -> List[str]:
    """Extract lessons learned from previously completed phases"""
    lessons = []
    
    for phase in completed_phases:
        if phase.get("lessons_learned"):
            lessons.append(f"From {phase['phase_name']}: {phase['lessons_learned']}")
        
        if phase.get("success_status") == "failed" and phase.get("failure_reason"):
            lessons.append(f"Avoid: {phase['failure_reason']} (from {phase['phase_name']})")
        
        if phase.get("scope_changes"):
            lessons.append(f"Scope management: Monitor {', '.join(phase['scope_changes'])} (from {phase['phase_name']})")
    
    return lessons[:3]  # Limit to 3 key lessons

def generate_phase_completion_analysis(phase_data: dict, assessment_data: dict, project_data: dict) -> dict:
    """Generate comprehensive analysis when a phase is completed"""
    
    phase_name = phase_data.get("phase_name", "")
    completion_percentage = phase_data.get("completion_percentage", 0)
    success_status = phase_data.get("success_status", "")
    budget_spent = phase_data.get("budget_spent", 0)
    
    # Analyze completion effectiveness
    completion_analysis = {
        "completion_score": calculate_completion_score(phase_data),
        "budget_performance": analyze_budget_performance(phase_data, project_data),
        "timeline_performance": analyze_timeline_performance(phase_data),
        "success_factors": identify_success_factors(phase_data, assessment_data),
        "improvement_areas": identify_improvement_areas(phase_data, assessment_data),
        "next_phase_readiness": assess_next_phase_readiness(phase_data, assessment_data),
        "recommendations_for_next_phase": generate_next_phase_recommendations(phase_data, assessment_data, project_data)
    }
    
    return completion_analysis

def calculate_completion_score(phase_data: dict) -> float:
    """Calculate overall completion score for a phase"""
    completion_percentage = phase_data.get("completion_percentage", 0)
    success_status = phase_data.get("success_status", "")
    
    base_score = completion_percentage
    
    if success_status == "successful":
        base_score += 10
    elif success_status == "partially_successful":
        base_score += 5
    elif success_status == "failed":
        base_score -= 20
    
    return max(0, min(100, base_score))

def analyze_budget_performance(phase_data: dict, project_data: dict) -> dict:
    """Analyze budget performance for completed phase"""
    budget_spent = phase_data.get("budget_spent", 0)
    # Calculate expected budget based on phase and project data
    # This is a simplified calculation - in practice, would use phase budget allocation
    total_budget = project_data.get("total_budget", 100000)
    expected_budget = total_budget * 0.15  # Simplified - would vary by phase
    
    variance = budget_spent - expected_budget
    variance_percentage = (variance / expected_budget * 100) if expected_budget > 0 else 0
    
    if variance_percentage <= 5:
        performance = "Excellent"
    elif variance_percentage <= 15:
        performance = "Good"
    elif variance_percentage <= 25:
        performance = "Acceptable"
    else:
        performance = "Concerning"
    
    return {
        "budget_spent": budget_spent,
        "expected_budget": expected_budget,
        "variance": variance,
        "variance_percentage": variance_percentage,
        "performance": performance
    }

def analyze_timeline_performance(phase_data: dict) -> dict:
    """Analyze timeline performance for completed phase"""
    start_date = phase_data.get("start_date")
    completion_date = phase_data.get("completion_date")
    
    if not start_date or not completion_date:
        return {"performance": "Unable to assess"}
    
    # Calculate actual duration (simplified)
    actual_duration = "N/A"  # Would calculate based on dates
    expected_duration = "N/A"  # Would be based on phase expectations
    
    return {
        "actual_duration": actual_duration,
        "expected_duration": expected_duration,
        "performance": "On Schedule"  # Would be calculated
    }

def identify_success_factors(phase_data: dict, assessment_data: dict) -> List[str]:
    """Identify what contributed to phase success"""
    success_factors = []
    
    if phase_data.get("success_status") == "successful":
        success_factors.append("Strong execution of planned activities")
        success_factors.append("Effective stakeholder engagement")
        success_factors.append("Adequate resource allocation")
    
    # Add assessment-based success factors
    for factor, score in assessment_data.items():
        if isinstance(score, (int, float)) and score >= 4:
            success_factors.append(f"High {factor.replace('_', ' ')} contributed to success")
    
    return success_factors[:5]

def identify_improvement_areas(phase_data: dict, assessment_data: dict) -> List[str]:
    """Identify areas for improvement in future phases"""
    improvement_areas = []
    
    if phase_data.get("failure_reason"):
        improvement_areas.append(f"Address: {phase_data['failure_reason']}")
    
    if phase_data.get("scope_changes"):
        improvement_areas.append("Improve scope management and change control")
    
    # Add assessment-based improvement areas
    for factor, score in assessment_data.items():
        if isinstance(score, (int, float)) and score < 3:
            improvement_areas.append(f"Strengthen {factor.replace('_', ' ')} for future phases")
    
    return improvement_areas[:5]

def assess_next_phase_readiness(phase_data: dict, assessment_data: dict) -> dict:
    """Assess readiness for next phase"""
    completion_percentage = phase_data.get("completion_percentage", 0)
    success_status = phase_data.get("success_status", "")
    
    if completion_percentage >= 90 and success_status == "successful":
        readiness_level = "High"
        readiness_score = 85
    elif completion_percentage >= 75 and success_status in ["successful", "partially_successful"]:
        readiness_level = "Medium"
        readiness_score = 70
    else:
        readiness_level = "Low"
        readiness_score = 50
    
    return {
        "readiness_level": readiness_level,
        "readiness_score": readiness_score,
        "prerequisites_met": completion_percentage >= 75,
        "recommendations": generate_readiness_recommendations(readiness_level)
    }

def generate_readiness_recommendations(readiness_level: str) -> List[str]:
    """Generate recommendations based on readiness level"""
    recommendations = {
        "High": [
            "Proceed to next phase with standard approach",
            "Leverage momentum from current phase success",
            "Consider accelerated timeline if resources permit"
        ],
        "Medium": [
            "Address any remaining gaps before proceeding",
            "Implement additional monitoring for next phase",
            "Consider additional resources for next phase"
        ],
        "Low": [
            "Complete current phase activities before proceeding",
            "Conduct readiness assessment for next phase",
            "Consider extended timeline or additional resources"
        ]
    }
    
    return recommendations.get(readiness_level, [])

def generate_next_phase_recommendations(phase_data: dict, assessment_data: dict, project_data: dict) -> List[str]:
    """Generate specific recommendations for the next phase"""
    recommendations = []
    
    current_phase = phase_data.get("phase_name", "")
    
    # Map to next phase
    phase_sequence = [
        "Investigate & Assess",
        "Mobilize & Prepare", 
        "Pilot & Adapt",
        "Activate & Deploy",
        "Cement & Transfer",
        "Track & Optimize"
    ]
    
    try:
        current_index = phase_sequence.index(current_phase)
        if current_index < len(phase_sequence) - 1:
            next_phase = phase_sequence[current_index + 1]
            
            # Generate next phase intelligence
            next_phase_intelligence = generate_phase_based_intelligence(next_phase, assessment_data, project_data)
            
            recommendations.extend(next_phase_intelligence["phase_intelligence"]["recommendations"][:3])
            
            # Add transition-specific recommendations
            recommendations.append(f"Prepare for {next_phase} by building on current phase successes")
            
            if phase_data.get("lessons_learned"):
                recommendations.append(f"Apply lessons learned: {phase_data['lessons_learned']}")
    
    except ValueError:
        recommendations.append("Review phase sequence and plan next steps")
    
    return recommendations[:5]

def get_type_specific_bonus(assessment_type: str, dimension_scores: dict) -> float:
    """Calculate type-specific success probability bonus"""
    
    bonus = 0.0
    
    if assessment_type == "software_implementation":
        if dimension_scores.get("technical_infrastructure", 3) >= 4:
            bonus += 5
        if dimension_scores.get("user_adoption_readiness", 3) >= 4:
            bonus += 5
    elif assessment_type == "business_process":
        if dimension_scores.get("process_maturity", 3) >= 4:
            bonus += 5
        if dimension_scores.get("cross_functional_collaboration", 3) >= 4:
            bonus += 5
    elif assessment_type == "manufacturing_operations":
        if dimension_scores.get("maintenance_operations_alignment", 3) >= 4:
            bonus += 5
        if dimension_scores.get("safety_compliance", 3) >= 4:
            bonus += 5
    
    return bonus

def get_type_specific_risks(assessment_type: str, dimension_scores: dict) -> List[str]:
    """Get risks specific to assessment type"""
    
    base_risks = ["Organizational resistance to change", "Resource constraints"]
    
    type_risks = {
        "software_implementation": [
            "Technical infrastructure limitations",
            "User adoption challenges", 
            "Data migration complexity",
            "System integration issues"
        ],
        "business_process": [
            "Process complexity and dependencies",
            "Cross-functional coordination challenges",
            "Performance measurement gaps",
            "Change fatigue from process modifications"
        ],
        "manufacturing_operations": [
            "Operational constraint management",
            "Shift work coordination challenges", 
            "Safety and compliance requirements",
            "Maintenance-operations alignment issues"
        ]
    }
    
    risks = base_risks.copy()
    if assessment_type in type_risks:
        risks.extend(type_risks[assessment_type])
    
    return risks

def get_phase_recommendations_for_type(assessment_type: str) -> Dict[str, str]:
    """Get IMPACT phase recommendations specific to assessment type"""
    
    base_recommendations = {
        "investigate": "Comprehensive current state analysis and stakeholder mapping",
        "mobilize": "Build strong foundation and prepare all resources",
        "pilot": "Test approach with representative group",
        "activate": "Execute with comprehensive support and monitoring",
        "cement": "Institutionalize changes and transfer ownership",
        "track": "Monitor success and drive continuous improvement"
    }
    
    type_specific = {
        "software_implementation": {
            "investigate": "Assess technical infrastructure and user readiness",
            "mobilize": "Prepare training programs and technical environment",
            "pilot": "Test system functionality and user experience",
            "activate": "Deploy with technical support and user training",
            "cement": "Establish ongoing support and maintenance procedures",
            "track": "Monitor system performance and user adoption"
        },
        "business_process": {
            "investigate": "Map current processes and identify improvement opportunities",
            "mobilize": "Design new processes and prepare training materials",
            "pilot": "Test new processes with key stakeholder groups",
            "activate": "Implement across all affected departments",
            "cement": "Standardize processes and embed in operations",
            "track": "Monitor process performance and continuous improvement"
        },
        "manufacturing_operations": {
            "investigate": "Assess operational constraints and stakeholder alignment",
            "mobilize": "Build cross-shift communication and training programs",
            "pilot": "Test improvements in controlled operational environment",
            "activate": "Implement with minimal operational disruption",
            "cement": "Embed in operational procedures and culture",
            "track": "Monitor operational performance improvements"
        }
    }
    
    return type_specific.get(assessment_type, base_recommendations)

def generate_implementation_plan(assessment_type: str, overall_score: float) -> Dict[str, Any]:
    """Generate implementation plan based on type and readiness"""
    
    # Base timeline calculation
    base_weeks = 16
    if overall_score < 2.5:
        base_weeks = 24  # More time needed for low readiness
    elif overall_score > 4.0:
        base_weeks = 12  # Less time needed for high readiness
    
    type_adjustments = {
        "software_implementation": 1.2,  # Tech projects take longer
        "business_process": 1.0,  # Standard timeline
        "manufacturing_operations": 1.3,  # Manufacturing takes longer
        "general_readiness": 1.0
    }
    
    adjusted_weeks = int(base_weeks * type_adjustments.get(assessment_type, 1.0))
    
    return {
        "suggested_duration_weeks": adjusted_weeks,
        "critical_success_factors": [
            "Strong leadership engagement",
            "Comprehensive stakeholder communication",
            "Adequate resource allocation",
            "Effective training and support"
        ],
        "resource_priorities": [
            "Change management expertise",
            "Training and communication resources",
            "Technical support and infrastructure",
            "Stakeholder engagement systems"
        ],
        "key_milestones": [
            {"phase": "investigate", "milestone": "Readiness assessment complete", "week": 2},
            {"phase": "mobilize", "milestone": "Implementation plan approved", "week": 4},
            {"phase": "pilot", "milestone": "Pilot success validated", "week": 8},
            {"phase": "activate", "milestone": "Full deployment complete", "week": adjusted_weeks - 4},
            {"phase": "cement", "milestone": "Knowledge transfer complete", "week": adjusted_weeks - 2},
            {"phase": "track", "milestone": "Success metrics achieved", "week": adjusted_weeks}
        ]
    }

def calculate_manufacturing_readiness_analysis(assessment_data: dict) -> Dict[str, Any]:
    """Calculate manufacturing-specific readiness analysis using Newton's laws"""
    # Extract scores from assessment data
    scores = []
    dimension_scores = {}
    
    # Core dimensions
    core_dimensions = [
        'leadership_commitment', 'organizational_culture', 'resource_availability',
        'stakeholder_engagement', 'training_capability'
    ]
    
    # Manufacturing-specific dimensions
    manufacturing_dimensions = [
        'manufacturing_constraints', 'maintenance_operations_alignment',
        'shift_work_considerations', 'technical_readiness', 'safety_compliance'
    ]
    
    all_dimensions = core_dimensions + manufacturing_dimensions
    
    for dim in all_dimensions:
        if dim in assessment_data and 'score' in assessment_data[dim]:
            score = assessment_data[dim]['score']
            scores.append(score)
            dimension_scores[dim] = score
    
    avg_score = sum(scores) / len(scores) if scores else 0
    
    # Calculate manufacturing-specific inertia
    manufacturing_weight = 1.2  # Higher weight for manufacturing environment
    organizational_inertia = (5 - avg_score) * 20 * manufacturing_weight
    
    # Calculate required force considering manufacturing constraints
    base_force = 100 - (avg_score * 15)
    maintenance_alignment_score = dimension_scores.get('maintenance_operations_alignment', 3)
    force_required = base_force * (1 + (5 - maintenance_alignment_score) * 0.2)
    
    # Calculate resistance considering shift work
    shift_work_score = dimension_scores.get('shift_work_considerations', 3)
    resistance_magnitude = organizational_inertia * (1 + (5 - shift_work_score) * 0.15)
    
    return {
        "inertia": {
            "value": round(organizational_inertia, 1),
            "interpretation": "Low" if organizational_inertia < 48 else "Medium" if organizational_inertia < 84 else "High",
            "description": f"Manufacturing organization shows {'low' if organizational_inertia < 48 else 'medium' if organizational_inertia < 84 else 'high'} resistance to change"
        },
        "force": {
            "required": round(force_required, 1),
            "maintenance_factor": round(maintenance_alignment_score, 1),
            "description": f"{'Low' if force_required < 60 else 'Medium' if force_required < 90 else 'High'} effort required for successful manufacturing change"
        },
        "reaction": {
            "resistance": round(resistance_magnitude, 1),
            "shift_impact": round(shift_work_score, 1),
            "description": f"Expect {'minimal' if resistance_magnitude < 36 else 'moderate' if resistance_magnitude < 72 else 'significant'} organizational pushback"
        }
    }

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
        # Create AI chat instance with timeout handling
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

        # Get AI response with timeout handling
        user_message = UserMessage(text=prompt)
        
        # Try to get AI response with a shorter timeout
        try:
            response = await asyncio.wait_for(chat.send_message(user_message), timeout=15.0)
        except asyncio.TimeoutError:
            print("AI analysis timed out, using fallback analysis")
            # Use fallback analysis if AI times out
            response = f"""
            EXECUTIVE SUMMARY:
            Your organization shows an overall readiness score of {sum([assessment.change_management_maturity.score, assessment.communication_effectiveness.score, assessment.leadership_support.score, assessment.workforce_adaptability.score, assessment.resource_adequacy.score])/5:.1f}/5 for change initiatives.

            NEWTON'S LAWS INSIGHTS:
            - Organizational inertia is {newton_data['inertia']['interpretation'].lower()} based on current readiness
            - Force required: {newton_data['force']['description'].lower()}
            - Expected resistance: {newton_data['reaction']['description'].lower()}

            STRATEGIC RECOMMENDATIONS:
            1. Focus on strengthening the lowest-scoring assessment dimension
            2. Implement gradual change approach to overcome inertia
            3. Build strong communication channels for change management
            4. Engage leadership early and consistently
            5. Prepare comprehensive training and support programs

            RISK ANALYSIS:
            - Monitor resistance patterns closely
            - Ensure adequate resources throughout the process
            - Maintain momentum through regular wins and celebrations
            """
        
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
    
    except asyncio.TimeoutError:
        print("AI analysis timed out, using fallback analysis")
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
        
        # Simple fallback analysis
        fallback_analysis = f"""
        EXECUTIVE SUMMARY:
        Your organization shows an overall readiness score of {avg_score:.1f}/5 for change initiatives.

        NEWTON'S LAWS INSIGHTS:
        - Organizational inertia is {newton_data['inertia']['interpretation'].lower()} based on current readiness
        - Force required: {newton_data['force']['description'].lower()}
        - Expected resistance: {newton_data['reaction']['description'].lower()}

        STRATEGIC RECOMMENDATIONS:
        1. Focus on strengthening the lowest-scoring assessment dimension
        2. Implement gradual change approach to overcome inertia
        3. Build strong communication channels for change management
        4. Engage leadership early and consistently
        5. Prepare comprehensive training and support programs
        """
        
        base_probability = (avg_score / 5) * 100
        inertia_adjustment = (100 - newton_data['inertia']['value']) * 0.2
        success_probability = min(95, base_probability + inertia_adjustment)
        
        return {
            "analysis": fallback_analysis,
            "recommendations": [
                "Focus on strengthening the lowest-scoring assessment dimension",
                "Implement gradual change approach to overcome inertia",
                "Build strong communication channels for change management",
                "Engage leadership early and consistently",
                "Prepare comprehensive training and support programs"
            ],
            "success_probability": round(success_probability, 1),
            "newton_analysis": newton_data,
            "risk_factors": ["AI analysis timeout - using fallback analysis"],
            "phase_recommendations": {
                "identify": "Focus on clear vision and stakeholder alignment",
                "measure": "Conduct thorough readiness assessment",
                "plan": "Develop comprehensive change strategy",
                "act": "Execute with strong monitoring",
                "control": "Maintain momentum and address issues",
                "transform": "Institutionalize and celebrate success"
            },
            "recommended_project": {
                "suggested_duration_weeks": max(12, int(24 - (avg_score * 2))),
                "critical_success_factors": [
                    "Strong leadership engagement",
                    "Clear communication strategy",
                    "Adequate resource allocation"
                ],
                "resource_priorities": [
                    "Change management expertise",
                    "Communication and training resources",
                    "Stakeholder engagement systems"
                ]
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
# Assessment Types endpoint
@app.get("/api/assessment-types")
async def get_assessment_types():
    """Get all available assessment types"""
    return {"assessment_types": ASSESSMENT_TYPES}

@app.get("/api/assessment-types/{assessment_type}")
async def get_assessment_type(assessment_type: str):
    """Get specific assessment type configuration"""
    if assessment_type not in ASSESSMENT_TYPES:
        raise HTTPException(status_code=404, detail="Assessment type not found")
    return ASSESSMENT_TYPES[assessment_type]

# Enhanced assessment creation with type support
@app.post("/api/assessments/create")
async def create_typed_assessment(
    assessment_data: dict,
    current_user: User = Depends(get_current_user)
):
    try:
        assessment_type = assessment_data.get("assessment_type", "general_readiness")
        
        if assessment_type not in ASSESSMENT_TYPES:
            raise HTTPException(status_code=400, detail="Invalid assessment type")
        
        # Generate ID and timestamps
        assessment_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Get assessment type configuration
        type_config = ASSESSMENT_TYPES[assessment_type]
        
        # Calculate overall score from submitted dimensions
        all_scores = []
        dimension_scores = {}
        
        for dimension in type_config["dimensions"]:
            dim_id = dimension["id"]
            if dim_id in assessment_data and "score" in assessment_data[dim_id]:
                score = assessment_data[dim_id]["score"]
                all_scores.append(score)
                dimension_scores[dim_id] = score
        
        overall_score = sum(all_scores) / len(all_scores) if all_scores else 0
        
        # Determine readiness level
        if overall_score >= 4.5:
            readiness_level = "Excellent"
        elif overall_score >= 3.5:
            readiness_level = "Good"
        elif overall_score >= 2.5:
            readiness_level = "Fair"
        elif overall_score >= 1.5:
            readiness_level = "Poor"
        else:
            readiness_level = "Critical"
        
        # Calculate analysis based on assessment type
        analysis_data = calculate_universal_readiness_analysis(assessment_data, assessment_type)
        
        # Generate AI analysis based on type
        ai_analysis = generate_typed_ai_analysis(assessment_data, assessment_type, overall_score, readiness_level, analysis_data)
        
        # Generate recommendations based on type
        recommendations = generate_typed_recommendations(assessment_type, dimension_scores, overall_score)
        
        # Calculate success probability
        base_probability = (overall_score / 5) * 100
        type_bonus = get_type_specific_bonus(assessment_type, dimension_scores)
        success_probability = min(95, base_probability + type_bonus)
        
        # Create assessment document
        assessment_doc = {
            "id": assessment_id,
            "user_id": current_user.id,
            "organization": current_user.organization,
            "assessment_type": assessment_type,
            "project_name": assessment_data.get("project_name", ""),
            "project_type": type_config["name"],
            "assessment_version": "3.0",
            **assessment_data,  # Include all dimension data
            "overall_score": round(overall_score, 2),
            "readiness_level": readiness_level,
            "ai_analysis": ai_analysis,
            "recommendations": recommendations,
            "success_probability": round(success_probability, 1),
            "newton_analysis": analysis_data,
            "risk_factors": get_type_specific_risks(assessment_type, dimension_scores),
            "phase_recommendations": get_phase_recommendations_for_type(assessment_type),
            "implementation_plan": generate_implementation_plan(assessment_type, overall_score),
            "guarantee_eligibility": overall_score >= 3.0,
            "created_at": now,
            "updated_at": now
        }
        
        # Save to database
        result = await db.assessments.insert_one(assessment_doc)
        assessment_doc["_id"] = str(result.inserted_id)
        
        return assessment_doc
        
    except Exception as e:
        print(f"Assessment Creation Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create assessment: {str(e)}")

# Projects endpoints
@app.post("/api/projects")
async def create_project(
    project_data: dict,
    current_user: User = Depends(get_current_user)
):
    try:
        project_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        project_doc = {
            "id": project_id,
            "user_id": current_user.id,
            "client_organization": project_data.get("client_organization", current_user.organization),
            "project_name": project_data.get("project_name", ""),
            "project_type": project_data.get("project_type", "general_readiness"),
            "assessment_id": project_data.get("assessment_id"),
            "description": project_data.get("description", ""),
            "objectives": project_data.get("objectives", []),
            "scope": project_data.get("scope", ""),
            "start_date": now,
            "estimated_end_date": project_data.get("estimated_end_date"),
            "total_budget": project_data.get("total_budget", 0.0),
            "spent_budget": 0.0,
            "budget_alerts_enabled": True,
            "current_phase": "investigate",
            "overall_progress": 0.0,
            "status": "active",
            "health_status": "green",
            "phase_progress": {phase: 0.0 for phase in IMPACT_PHASES.keys()},
            "phases": [
                {
                    "phase_name": phase_key,
                    "phase_display_name": phase_info["name"],
                    "phase_number": phase_info["order"],
                    "status": "not_started",
                    "completion_percentage": 0.0,
                    "budget_spent": 0.0,
                    "start_date": None,
                    "completion_date": None,
                    "success_status": None,
                    "success_reason": None,
                    "failure_reason": None,
                    "lessons_learned": None,
                    "scope_changes": [],
                    "tasks_completed": [],
                    "deliverables_completed": [],
                    "risks_identified": [],
                    "mitigation_actions": [],
                    "recommendations": [],
                    "next_phase_suggestions": []
                }
                for phase_key, phase_info in IMPACT_PHASES.items()
            ],
            "phase_start_dates": {},
            "phase_end_dates": {},
            "deliverables": [],
            "milestones": [],
            "project_team": project_data.get("project_team", []),
            "stakeholders": project_data.get("stakeholders", []),
            "risks": [],
            "issues": [],
            "last_update": now,
            "next_milestone": None,
            "created_at": now,
            "updated_at": now
        }
        
        result = await db.projects.insert_one(project_doc)
        project_doc["_id"] = str(result.inserted_id)
        
        return project_doc
        
    except Exception as e:
        print(f"Project Creation Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

@app.get("/api/projects")
async def get_user_projects(current_user: User = Depends(get_current_user)):
    try:
        projects = []
        async for project in db.projects.find({"user_id": current_user.id}):
            project["_id"] = str(project["_id"])
            projects.append(project)
        return {"projects": projects}
    except Exception as e:
        print(f"Get Projects Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve projects")

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str, current_user: User = Depends(get_current_user)):
    try:
        project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        project["_id"] = str(project["_id"])
        return project
    except Exception as e:
        print(f"Get Project Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve project")

@app.post("/api/assessments/{assessment_id}/implementation-plan")
async def generate_implementation_plan_endpoint(
    assessment_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate customized week-by-week implementation plan based on assessment results"""
    try:
        # Get assessment data
        assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Extract assessment data for plan generation
        assessment_data = {
            "leadership_support": assessment.get("leadership_support", {}).get("score", 3),
            "resource_availability": assessment.get("resource_availability", {}).get("score", 3),
            "change_management_maturity": assessment.get("change_management_maturity", {}).get("score", 3),
            "communication_effectiveness": assessment.get("communication_effectiveness", {}).get("score", 3),
            "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3)
        }
        
        assessment_type = assessment.get("assessment_type", "general_readiness")
        overall_score = assessment.get("overall_score", 3.0)
        
        # Generate week-by-week plan
        implementation_plan = generate_week_by_week_plan(assessment_data, assessment_type, overall_score)
        
        # Add project-specific metadata
        implementation_plan["metadata"] = {
            "assessment_id": assessment_id,
            "project_name": assessment.get("project_name", ""),
            "organization": assessment.get("organization", ""),
            "assessment_type": assessment_type,
            "overall_readiness_score": overall_score,
            "readiness_level": assessment.get("readiness_level", ""),
            "generated_at": datetime.utcnow(),
            "generated_by": current_user.full_name
        }
        
        return implementation_plan
        
    except Exception as e:
        print(f"Implementation Plan Generation Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate implementation plan: {str(e)}")

@app.post("/api/assessments/{assessment_id}/customized-playbook")
async def generate_customized_playbook(
    assessment_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate customized change management playbook based on assessment results"""
    try:
        # Get assessment data
        assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Generate AI-powered customized playbook
        chat = LlmChat(
            api_key=ANTHROPIC_API_KEY,
            session_id=f"playbook_generation_{assessment_id}",
            system_message="""You are an expert change management consultant specializing in the IMPACT Methodology and DigitalThinker's proven approach to manufacturing excellence. 

            Generate a comprehensive, customized change management playbook based on the assessment results. The playbook should be tailored to the specific organization's readiness level, strengths, and challenges.

            Structure the playbook with:
            1. Executive Summary
            2. Assessment-Based Recommendations
            3. Phase-by-Phase Implementation Guide
            4. Risk Mitigation Strategies
            5. Success Metrics and Monitoring
            6. Stakeholder Engagement Strategy
            7. Communication Plan
            8. Training and Development Plan
            9. Resistance Management Approach
            10. Guarantee-Backed Success Framework

            Focus on practical, actionable guidance that consultants can implement immediately."""
        ).with_model("anthropic", "claude-sonnet-4-20250514")
        
        # Create detailed prompt for playbook generation
        assessment_data = {
            "leadership_support": assessment.get("leadership_support", {}).get("score", 3),
            "resource_availability": assessment.get("resource_availability", {}).get("score", 3),
            "change_management_maturity": assessment.get("change_management_maturity", {}).get("score", 3),
            "communication_effectiveness": assessment.get("communication_effectiveness", {}).get("score", 3),
            "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3)
        }
        
        prompt = f"""
        Generate a comprehensive, customized change management playbook for the following organization:

        PROJECT DETAILS:
        • Project Name: {assessment.get("project_name", "")}
        • Organization: {assessment.get("organization", "")}
        • Assessment Type: {assessment.get("assessment_type", "")}
        • Overall Readiness Score: {assessment.get("overall_score", 0)}/5
        • Readiness Level: {assessment.get("readiness_level", "")}

        ASSESSMENT SCORES (1-5 scale):
        • Leadership Support: {assessment_data["leadership_support"]}/5
        • Resource Availability: {assessment_data["resource_availability"]}/5
        • Change Management Maturity: {assessment_data["change_management_maturity"]}/5
        • Communication Effectiveness: {assessment_data["communication_effectiveness"]}/5
        • Workforce Adaptability: {assessment_data["workforce_adaptability"]}/5

        EXISTING RECOMMENDATIONS:
        {'; '.join(assessment.get("recommendations", []))}

        RISK FACTORS:
        {'; '.join(assessment.get("risk_factors", []))}

        SUCCESS PROBABILITY: {assessment.get("success_probability", 0)}%

        Please generate a detailed, actionable playbook that addresses the specific strengths and challenges identified in this assessment. Focus on practical implementation guidance that will ensure project success.

        The playbook should be approximately 2000-3000 words and include specific tactics, tools, and strategies tailored to this organization's unique profile.
        """
        
        # Generate playbook content
        response = await chat.send_message(UserMessage(prompt))
        playbook_content = response if isinstance(response, str) else response.text
        
        # Structure the playbook response
        playbook = {
            "assessment_id": assessment_id,
            "project_name": assessment.get("project_name", ""),
            "organization": assessment.get("organization", ""),
            "assessment_type": assessment.get("assessment_type", ""),
            "overall_readiness_score": assessment.get("overall_score", 0),
            "readiness_level": assessment.get("readiness_level", ""),
            "success_probability": assessment.get("success_probability", 0),
            "content": playbook_content,
            "generated_at": datetime.utcnow(),
            "generated_by": current_user.full_name,
            "version": "1.0",
            "customization_factors": {
                "leadership_support": assessment_data["leadership_support"],
                "resource_availability": assessment_data["resource_availability"],
                "change_management_maturity": assessment_data["change_management_maturity"],
                "communication_effectiveness": assessment_data["communication_effectiveness"],
                "workforce_adaptability": assessment_data["workforce_adaptability"]
            }
        }
        
        return playbook
        
    except Exception as e:
        print(f"Customized Playbook Generation Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate customized playbook: {str(e)}")

@app.post("/api/assessments/{assessment_id}/predictive-analytics")
async def generate_predictive_analytics(
    assessment_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate comprehensive predictive analytics based on assessment results"""
    try:
        # Get assessment data
        assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Extract assessment data for analytics
        assessment_data = {
            "leadership_support": assessment.get("leadership_support", {}).get("score", 3),
            "resource_availability": assessment.get("resource_availability", {}).get("score", 3),
            "change_management_maturity": assessment.get("change_management_maturity", {}).get("score", 3),
            "communication_effectiveness": assessment.get("communication_effectiveness", {}).get("score", 3),
            "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3),
            "technical_readiness": assessment.get("technical_readiness", {}).get("score", 3),
            "stakeholder_engagement": assessment.get("stakeholder_engagement", {}).get("score", 3)
        }
        
        assessment_type = assessment.get("assessment_type", "general_readiness")
        overall_score = assessment.get("overall_score", 3.0)
        
        # Generate task-specific success predictions
        task_predictions = []
        for task_num in range(1, 11):
            task_id = f"task_{task_num}"
            prediction = predict_task_success_probability(task_id, assessment_data, overall_score)
            task_predictions.append(prediction)
        
        # Estimate total budget from implementation plan (default if not available)
        total_budget = 90000  # Default budget estimate
        
        # Generate predictive analytics
        budget_risk = predict_budget_overrun_risk(assessment_data, overall_score, total_budget)
        scope_creep_risk = predict_scope_creep_risk(assessment_data, assessment_type)
        timeline_optimization = predict_timeline_optimization(assessment_data, overall_score)
        risk_trending = generate_predictive_risk_trending(assessment_data, overall_score)
        
        # Compile comprehensive analytics
        predictive_analytics = {
            "assessment_id": assessment_id,
            "project_name": assessment.get("project_name", ""),
            "organization": assessment.get("organization", ""),
            "assessment_type": assessment_type,
            "overall_readiness_score": overall_score,
            "generated_at": datetime.utcnow(),
            "generated_by": current_user.full_name,
            
            # Task-specific predictions
            "task_success_predictions": task_predictions,
            "highest_risk_tasks": sorted(task_predictions, key=lambda x: x["success_probability"])[:3],
            "lowest_risk_tasks": sorted(task_predictions, key=lambda x: x["success_probability"], reverse=True)[:3],
            
            # Budget predictions
            "budget_risk_analysis": budget_risk,
            
            # Scope predictions
            "scope_creep_analysis": scope_creep_risk,
            
            # Timeline predictions
            "timeline_optimization": timeline_optimization,
            
            # Risk trending
            "risk_trending": risk_trending,
            
            # Overall project outlook
            "project_outlook": {
                "overall_risk_level": "High" if overall_score < 2.5 else "Medium" if overall_score < 3.5 else "Low",
                "success_probability": round(min(95, max(15, overall_score * 18)), 1),
                "recommended_actions": generate_recommended_actions(task_predictions, budget_risk, scope_creep_risk),
                "critical_success_factors": identify_critical_success_factors(assessment_data),
                "key_monitoring_points": risk_trending["critical_monitoring_weeks"]
            }
        }
        
        return predictive_analytics
        
    except Exception as e:
        print(f"Predictive Analytics Generation Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate predictive analytics: {str(e)}")

@app.post("/api/projects/{project_id}/risk-monitoring")
async def generate_real_time_risk_monitoring(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate real-time risk monitoring dashboard for active projects"""
    try:
        # Get project data
        project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get associated assessment if available
        assessment_id = project.get("assessment_id")
        assessment_data = {}
        if assessment_id:
            assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
            if assessment:
                assessment_data = {
                    "leadership_support": assessment.get("leadership_support", {}).get("score", 3),
                    "resource_availability": assessment.get("resource_availability", {}).get("score", 3),
                    "change_management_maturity": assessment.get("change_management_maturity", {}).get("score", 3),
                    "communication_effectiveness": assessment.get("communication_effectiveness", {}).get("score", 3),
                    "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3)
                }
        
        # Calculate current project metrics
        overall_progress = calculate_project_progress(project)
        spent_budget = project.get("spent_budget", 0)
        total_budget = project.get("total_budget", 90000)
        budget_utilization = (spent_budget / total_budget * 100) if total_budget > 0 else 0
        
        # Generate risk alerts
        risk_alerts = []
        
        # Budget risk alerts
        if budget_utilization > 80:
            risk_alerts.append({
                "type": "Budget",
                "severity": "High",
                "message": f"Budget utilization at {budget_utilization:.1f}% - immediate attention required",
                "recommended_action": "Review remaining activities and implement cost controls"
            })
        elif budget_utilization > 60:
            risk_alerts.append({
                "type": "Budget",
                "severity": "Medium",
                "message": f"Budget utilization at {budget_utilization:.1f}% - monitor closely",
                "recommended_action": "Review upcoming expenses and optimize resource allocation"
            })
        
        # Schedule risk alerts
        if overall_progress < 60 and budget_utilization > 70:
            risk_alerts.append({
                "type": "Schedule",
                "severity": "High",
                "message": "Project behind schedule with high budget utilization",
                "recommended_action": "Accelerate critical path activities and review scope"
            })
        
        # Generate trending analysis
        current_week = min(10, max(1, int(overall_progress / 10) + 1))
        
        risk_monitoring = {
            "project_id": project_id,
            "project_name": project.get("project_name", ""),
            "current_status": {
                "overall_progress": round(overall_progress, 1),
                "current_week": current_week,
                "budget_utilization": round(budget_utilization, 1),
                "health_status": project.get("health_status", "green")
            },
            "risk_alerts": risk_alerts,
            "trend_analysis": {
                "budget_trend": "On Track" if budget_utilization <= overall_progress else "Over Budget",
                "schedule_trend": "On Track" if overall_progress >= (current_week * 10) else "Behind Schedule",
                "scope_trend": "Stable" if len(risk_alerts) == 0 else "At Risk"
            },
            "predictive_insights": {
                "completion_probability": min(95, max(30, 100 - len(risk_alerts) * 20)),
                "budget_overrun_risk": "Low" if budget_utilization < 80 else "High",
                "timeline_risk": "Low" if overall_progress >= (current_week * 8) else "High"
            },
            "recommendations": generate_real_time_recommendations(risk_alerts, overall_progress, budget_utilization),
            "generated_at": datetime.utcnow()
        }
        
        return risk_monitoring
        
    except Exception as e:
        print(f"Risk Monitoring Generation Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate risk monitoring: {str(e)}")

@app.post("/api/projects/{project_id}/detailed-budget-tracking")
async def generate_detailed_budget_tracking_endpoint(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate detailed task-level and phase-level budget tracking"""
    try:
        # Get project data
        project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get associated assessment and implementation plan
        assessment_id = project.get("assessment_id")
        assessment_data = {}
        implementation_plan = {}
        
        if assessment_id:
            assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
            if assessment:
                assessment_data = {
                    "leadership_support": assessment.get("leadership_support", {}).get("score", 3),
                    "resource_availability": assessment.get("resource_availability", {}).get("score", 3),
                    "change_management_maturity": assessment.get("change_management_maturity", {}).get("score", 3),
                    "communication_effectiveness": assessment.get("communication_effectiveness", {}).get("score", 3),
                    "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3),
                    "technical_readiness": assessment.get("technical_readiness", {}).get("score", 3),
                    "stakeholder_engagement": assessment.get("stakeholder_engagement", {}).get("score", 3)
                }
                
                # Generate implementation plan for budget tracking
                overall_score = assessment.get("overall_score", 3.0)
                assessment_type = assessment.get("assessment_type", "general_readiness")
                implementation_plan = generate_week_by_week_plan(assessment_data, assessment_type, overall_score)
        
        # Generate detailed budget tracking
        budget_tracking = generate_detailed_budget_tracking(project, assessment_data, implementation_plan)
        
        return budget_tracking
        
    except Exception as e:
        print(f"Detailed Budget Tracking Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate detailed budget tracking: {str(e)}")

@app.post("/api/projects/{project_id}/advanced-forecasting")
async def generate_advanced_project_forecasting_endpoint(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate advanced project outcome forecasting"""
    try:
        # Get project data
        project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get associated assessment and analytics
        assessment_id = project.get("assessment_id")
        assessment_data = {}
        predictive_analytics = {}
        budget_tracking = {}
        
        if assessment_id:
            assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
            if assessment:
                assessment_data = {
                    "overall_score": assessment.get("overall_score", 3.0),
                    "leadership_support": assessment.get("leadership_support", {}).get("score", 3),
                    "resource_availability": assessment.get("resource_availability", {}).get("score", 3),
                    "change_management_maturity": assessment.get("change_management_maturity", {}).get("score", 3),
                    "communication_effectiveness": assessment.get("communication_effectiveness", {}).get("score", 3),
                    "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3),
                    "technical_readiness": assessment.get("technical_readiness", {}).get("score", 3),
                    "stakeholder_engagement": assessment.get("stakeholder_engagement", {}).get("score", 3),
                    "maintenance_operations_alignment": assessment.get("maintenance_operations_alignment", {}).get("score", 3)
                }
                
                # Generate predictive analytics for forecasting
                assessment_type = assessment.get("assessment_type", "general_readiness")
                overall_score = assessment.get("overall_score", 3.0)
                
                # Simulate predictive analytics data
                predictive_analytics = {
                    "project_outlook": {
                        "success_probability": min(95, max(15, overall_score * 18))
                    }
                }
                
                # Simulate budget tracking data
                implementation_plan = generate_week_by_week_plan(assessment_data, assessment_type, overall_score)
                budget_tracking = generate_detailed_budget_tracking(project, assessment_data, implementation_plan)
        
        # Generate advanced forecasting
        forecasting = generate_advanced_project_forecasting(project, assessment_data, predictive_analytics, budget_tracking)
        
        return forecasting
        
    except Exception as e:
        print(f"Advanced Forecasting Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate advanced forecasting: {str(e)}")

@app.post("/api/projects/{project_id}/stakeholder-communications")
async def generate_stakeholder_communications_endpoint(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate automated stakeholder communication content"""
    try:
        # Get project data
        project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get associated assessment
        assessment_id = project.get("assessment_id")
        assessment_data = {}
        budget_tracking = {}
        project_forecasting = {}
        
        if assessment_id:
            assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
            if assessment:
                assessment_data = {
                    "leadership_support": assessment.get("leadership_support", {}).get("score", 3),
                    "resource_availability": assessment.get("resource_availability", {}).get("score", 3),
                    "change_management_maturity": assessment.get("change_management_maturity", {}).get("score", 3),
                    "communication_effectiveness": assessment.get("communication_effectiveness", {}).get("score", 3),
                    "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3),
                    "technical_readiness": assessment.get("technical_readiness", {}).get("score", 3)
                }
                
                # Generate supporting data
                overall_score = assessment.get("overall_score", 3.0)
                assessment_type = assessment.get("assessment_type", "general_readiness")
                implementation_plan = generate_week_by_week_plan(assessment_data, assessment_type, overall_score)
                budget_tracking = generate_detailed_budget_tracking(project, assessment_data, implementation_plan)
                
                predictive_analytics = {
                    "project_outlook": {
                        "success_probability": min(95, max(15, overall_score * 18))
                    }
                }
                
                project_forecasting = generate_advanced_project_forecasting(project, assessment_data, predictive_analytics, budget_tracking)
        
        # Generate stakeholder communications
        communications = generate_stakeholder_communications(project, budget_tracking, project_forecasting, assessment_data)
        
        return communications
        
    except Exception as e:
        print(f"Stakeholder Communications Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate stakeholder communications: {str(e)}")

@app.post("/api/projects/{project_id}/manufacturing-excellence-tracking")
async def generate_manufacturing_excellence_tracking(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate manufacturing excellence correlation tracking"""
    try:
        # Get project data
        project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get associated assessment
        assessment_id = project.get("assessment_id")
        assessment_data = {}
        
        if assessment_id:
            assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
            if assessment:
                assessment_data = {
                    "maintenance_operations_alignment": assessment.get("maintenance_operations_alignment", {}).get("score", 3),
                    "technical_readiness": assessment.get("technical_readiness", {}).get("score", 3),
                    "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3),
                    "safety_compliance": assessment.get("safety_compliance", {}).get("score", 3),
                    "shift_work_considerations": assessment.get("shift_work_considerations", {}).get("score", 3)
                }
        
        # Calculate manufacturing excellence metrics
        maintenance_excellence_score = assessment_data.get("maintenance_operations_alignment", 3.0)
        operational_efficiency_potential = (
            assessment_data.get("technical_readiness", 3.0) +
            assessment_data.get("workforce_adaptability", 3.0) +
            assessment_data.get("safety_compliance", 3.0)
        ) / 3
        
        # Manufacturing performance predictions
        performance_improvements = {
            "unplanned_downtime_reduction": min(60, max(10, maintenance_excellence_score * 12)),
            "overall_equipment_effectiveness": min(35, max(5, maintenance_excellence_score * 7)),
            "maintenance_cost_reduction": min(30, max(5, maintenance_excellence_score * 6)),
            "safety_performance_improvement": min(25, max(5, assessment_data.get("safety_compliance", 3.0) * 5)),
            "operational_efficiency_gain": min(40, max(5, operational_efficiency_potential * 8))
        }
        
        # ROI calculations
        estimated_annual_savings = sum(performance_improvements.values()) * 1000  # Simplified calculation
        implementation_cost = project.get("total_budget", 90000)
        roi_percentage = ((estimated_annual_savings - implementation_cost) / implementation_cost * 100) if implementation_cost > 0 else 0
        
        excellence_tracking = {
            "project_id": project_id,
            "project_name": project.get("project_name", ""),
            "maintenance_excellence": {
                "current_score": round(maintenance_excellence_score, 1),
                "potential_score": min(5.0, maintenance_excellence_score + 1.5),
                "improvement_pathway": generate_excellence_pathway(maintenance_excellence_score, operational_efficiency_potential * 20),
                "critical_success_factors": [
                    "Maintenance-operations alignment",
                    "Technical readiness and adoption",
                    "Workforce adaptability and training",
                    "Safety and compliance integration"
                ]
            },
            "performance_predictions": {
                "unplanned_downtime_reduction": f"{performance_improvements['unplanned_downtime_reduction']:.1f}%",
                "oee_improvement": f"{performance_improvements['overall_equipment_effectiveness']:.1f}%",
                "maintenance_cost_reduction": f"{performance_improvements['maintenance_cost_reduction']:.1f}%",
                "safety_improvement": f"{performance_improvements['safety_performance_improvement']:.1f}%",
                "operational_efficiency": f"{performance_improvements['operational_efficiency_gain']:.1f}%"
            },
            "roi_analysis": {
                "estimated_annual_savings": round(estimated_annual_savings, 0),
                "implementation_investment": implementation_cost,
                "roi_percentage": round(roi_percentage, 1),
                "payback_period_months": max(6, min(36, 12 / (roi_percentage / 100))) if roi_percentage > 0 else 36,
                "business_case_strength": "Strong" if roi_percentage > 50 else "Moderate" if roi_percentage > 20 else "Developing"
            },
            "correlation_metrics": {
                "maintenance_operations_correlation": round(assessment_data.get("maintenance_operations_alignment", 3.0) / 5.0, 2),
                "technology_adoption_correlation": round(assessment_data.get("technical_readiness", 3.0) / 5.0, 2),
                "workforce_readiness_correlation": round(assessment_data.get("workforce_adaptability", 3.0) / 5.0, 2)
            },
            "manufacturing_kpis": {
                "equipment_reliability": f"{60 + maintenance_excellence_score * 8:.1f}%",
                "planned_maintenance_ratio": f"{40 + maintenance_excellence_score * 12:.1f}%",
                "mean_time_to_repair": f"{24 - maintenance_excellence_score * 4:.1f} hours",
                "maintenance_productivity": f"{70 + operational_efficiency_potential * 6:.1f}%"
            },
            "generated_at": datetime.utcnow()
        }
        
        return excellence_tracking
        
    except Exception as e:
        print(f"Manufacturing Excellence Tracking Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate manufacturing excellence tracking: {str(e)}")

@app.post("/api/projects/{project_id}/phases/{phase_name}/intelligence")
async def generate_phase_intelligence(
    project_id: str,
    phase_name: str,
    current_user: User = Depends(get_current_user)
):
    """Generate phase-based intelligence and recommendations"""
    try:
        # Get project data
        project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get associated assessment data
        assessment_data = {}
        assessment_id = project.get("assessment_id")
        if assessment_id:
            assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
            if assessment:
                assessment_data = {
                    "overall_score": assessment.get("overall_score", 3.0),
                    "leadership_support": assessment.get("leadership_support", {}).get("score", 3),
                    "resource_availability": assessment.get("resource_availability", {}).get("score", 3),
                    "change_management_maturity": assessment.get("change_management_maturity", {}).get("score", 3),
                    "communication_effectiveness": assessment.get("communication_effectiveness", {}).get("score", 3),
                    "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3),
                    "technical_readiness": assessment.get("technical_readiness", {}).get("score", 3),
                    "stakeholder_engagement": assessment.get("stakeholder_engagement", {}).get("score", 3)
                }
        
        # Get completed phases for lessons learned
        completed_phases = []
        phases = project.get("phases", [])
        for phase in phases:
            if phase.get("status") == "completed":
                completed_phases.append(phase)
        
        # Generate phase-based intelligence
        phase_intelligence = generate_phase_based_intelligence(phase_name, assessment_data, project, completed_phases)
        
        return phase_intelligence
        
    except Exception as e:
        print(f"Phase Intelligence Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate phase intelligence: {str(e)}")

@app.put("/api/projects/{project_id}/phases/{phase_name}/progress")
async def update_phase_progress(
    project_id: str,
    phase_name: str,
    progress_data: PhaseProgressUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update progress for a specific phase"""
    try:
        # Get project
        project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Update phase progress
        phases = project.get("phases", [])
        phase_found = False
        
        for i, phase in enumerate(phases):
            if phase.get("phase_name") == phase_name:
                # Update phase with new progress data
                phases[i].update({
                    "completion_percentage": progress_data.completion_percentage,
                    "status": progress_data.status,
                    "success_status": progress_data.success_status,
                    "success_reason": progress_data.success_reason,
                    "failure_reason": progress_data.failure_reason,
                    "lessons_learned": progress_data.lessons_learned,
                    "budget_spent": progress_data.budget_spent,
                    "updated_at": datetime.utcnow()
                })
                
                # Add optional fields if provided
                if progress_data.scope_changes:
                    phases[i]["scope_changes"] = progress_data.scope_changes
                if progress_data.tasks_completed:
                    phases[i]["tasks_completed"] = progress_data.tasks_completed
                if progress_data.deliverables_completed:
                    phases[i]["deliverables_completed"] = progress_data.deliverables_completed
                if progress_data.risks_identified:
                    phases[i]["risks_identified"] = progress_data.risks_identified
                
                # Set completion date if phase is completed
                if progress_data.status == "completed":
                    phases[i]["completion_date"] = datetime.utcnow()
                
                phase_found = True
                break
        
        if not phase_found:
            raise HTTPException(status_code=404, detail="Phase not found in project")
        
        # Update project in database
        result = await db.projects.update_one(
            {"id": project_id, "user_id": current_user.id},
            {"$set": {"phases": phases, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update phase progress")
        
        # Get updated project
        updated_project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
        updated_project["_id"] = str(updated_project["_id"])
        
        return updated_project
        
    except Exception as e:
        print(f"Phase Progress Update Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update phase progress: {str(e)}")

@app.post("/api/projects/{project_id}/phases/{phase_name}/complete")
async def complete_phase_with_analysis(
    project_id: str,
    phase_name: str,
    completion_data: PhaseProgressUpdate,
    current_user: User = Depends(get_current_user)
):
    """Complete a phase and generate comprehensive analysis"""
    try:
        # First update the phase progress
        await update_phase_progress(project_id, phase_name, completion_data, current_user)
        
        # Get updated project and assessment data
        project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
        assessment_data = {}
        
        assessment_id = project.get("assessment_id")
        if assessment_id:
            assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
            if assessment:
                assessment_data = {
                    "overall_score": assessment.get("overall_score", 3.0),
                    "leadership_support": assessment.get("leadership_support", {}).get("score", 3),
                    "resource_availability": assessment.get("resource_availability", {}).get("score", 3),
                    "change_management_maturity": assessment.get("change_management_maturity", {}).get("score", 3),
                    "communication_effectiveness": assessment.get("communication_effectiveness", {}).get("score", 3),
                    "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3),
                    "technical_readiness": assessment.get("technical_readiness", {}).get("score", 3),
                    "stakeholder_engagement": assessment.get("stakeholder_engagement", {}).get("score", 3)
                }
        
        # Find the completed phase data
        completed_phase_data = None
        phases = project.get("phases", [])
        for phase in phases:
            if phase.get("phase_name") == phase_name:
                completed_phase_data = phase
                break
        
        if not completed_phase_data:
            raise HTTPException(status_code=404, detail="Completed phase not found")
        
        # Generate comprehensive completion analysis
        completion_analysis = generate_phase_completion_analysis(completed_phase_data, assessment_data, project)
        
        # Update the phase with analysis results
        for i, phase in enumerate(phases):
            if phase.get("phase_name") == phase_name:
                phases[i]["completion_analysis"] = completion_analysis
                phases[i]["analysis_generated_at"] = datetime.utcnow()
                break
        
        # Update project in database
        await db.projects.update_one(
            {"id": project_id, "user_id": current_user.id},
            {"$set": {"phases": phases, "updated_at": datetime.utcnow()}}
        )
        
        return {
            "phase_name": phase_name,
            "completion_status": "completed",
            "completion_analysis": completion_analysis,
            "next_phase_recommendations": completion_analysis.get("recommendations_for_next_phase", []),
            "generated_at": datetime.utcnow()
        }
        
    except Exception as e:
        print(f"Phase Completion Analysis Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to complete phase with analysis: {str(e)}")

@app.get("/api/projects/{project_id}/workflow-status")
async def get_project_workflow_status(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive workflow status for a project"""
    try:
        # Get project
        project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Calculate workflow metrics
        phases = project.get("phases", [])
        
        # Phase completion summary
        phase_summary = {
            "total_phases": len(phases),
            "completed_phases": len([p for p in phases if p.get("status") == "completed"]),
            "in_progress_phases": len([p for p in phases if p.get("status") == "in_progress"]),
            "not_started_phases": len([p for p in phases if p.get("status") == "not_started"]),
            "failed_phases": len([p for p in phases if p.get("status") == "failed"])
        }
        
        # Overall progress calculation
        total_progress = sum(p.get("completion_percentage", 0) for p in phases)
        overall_progress = total_progress / len(phases) if phases else 0
        
        # Budget analysis
        total_budget_spent = sum(p.get("budget_spent", 0) for p in phases)
        total_budget = project.get("total_budget", 0)
        budget_utilization = (total_budget_spent / total_budget * 100) if total_budget > 0 else 0
        
        # Current phase identification
        current_phase = None
        for phase in phases:
            if phase.get("status") == "in_progress":
                current_phase = phase
                break
        
        if not current_phase:
            # Find next phase to start
            for phase in phases:
                if phase.get("status") == "not_started":
                    current_phase = phase
                    break
        
        # Success metrics
        successful_phases = [p for p in phases if p.get("success_status") == "successful"]
        success_rate = (len(successful_phases) / len(phases) * 100) if phases else 0
        
        return {
            "project_id": project_id,
            "project_name": project.get("project_name", ""),
            "workflow_status": {
                "overall_progress": round(overall_progress, 1),
                "current_phase": current_phase.get("phase_name") if current_phase else None,
                "phase_summary": phase_summary,
                "budget_utilization": round(budget_utilization, 1),
                "total_budget_spent": total_budget_spent,
                "success_rate": round(success_rate, 1),
                "phases_detail": phases
            },
            "generated_at": datetime.utcnow()
        }
        
    except Exception as e:
        print(f"Workflow Status Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")

def generate_recommended_actions(task_predictions: List[dict], budget_risk: dict, scope_creep_risk: dict) -> List[str]:
    """Generate recommended actions based on predictive analytics"""
    actions = []
    
    # Task-specific recommendations
    high_risk_tasks = [task for task in task_predictions if task["success_probability"] < 60]
    if high_risk_tasks:
        actions.append(f"Focus additional attention on {len(high_risk_tasks)} high-risk tasks")
    
    # Budget recommendations
    if budget_risk["risk_level"] == "High":
        actions.append("Implement strict budget controls and regular monitoring")
    
    # Scope recommendations
    if scope_creep_risk["impact_level"] == "High":
        actions.append("Establish formal change control process immediately")
    
    return actions

def generate_real_time_recommendations(risk_alerts: List[dict], progress: float, budget_utilization: float) -> List[str]:
    """Generate real-time recommendations for project management"""
    recommendations = []
    
    if len(risk_alerts) > 2:
        recommendations.append("Implement immediate risk mitigation measures")
    
    if budget_utilization > progress + 10:
        recommendations.append("Review and optimize resource allocation")
    
    if progress < 50:
        recommendations.append("Accelerate critical path activities")
    
    return recommendations

@app.put("/api/projects/{project_id}")
async def update_project(
    project_id: str,
    update_data: ProjectUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update project details"""
    try:
        # Get existing project
        existing_project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
        if not existing_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Update with provided data
        update_dict = update_data.dict(exclude_unset=True)
        
        # Handle datetime fields
        if "estimated_end_date" in update_dict and update_dict["estimated_end_date"]:
            try:
                update_dict["estimated_end_date"] = datetime.fromisoformat(update_dict["estimated_end_date"])
            except ValueError:
                pass
        
        update_dict["updated_at"] = datetime.utcnow()
        
        # Update in database
        result = await db.projects.update_one(
            {"id": project_id, "user_id": current_user.id},
            {"$set": update_dict}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Project not found or no changes made")
        
        # Get updated project
        updated_project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
        updated_project["_id"] = str(updated_project["_id"])
        
        return updated_project
        
    except Exception as e:
        print(f"Update Project Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update project: {str(e)}")

# Assessment routes - Enhanced for Manufacturing EAM
@app.post("/api/assessments")
async def create_enhanced_assessment(
    assessment_data: dict,
    current_user: User = Depends(get_current_user)
):
    try:
        # Generate ID and timestamps
        assessment_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Calculate overall score from all dimensions
        all_scores = []
        dimension_scores = {}
        
        # Core dimensions
        core_dimensions = [
            'leadership_commitment', 'organizational_culture', 'resource_availability',
            'stakeholder_engagement', 'training_capability'
        ]
        
        # Manufacturing-specific dimensions  
        manufacturing_dimensions = [
            'manufacturing_constraints', 'maintenance_operations_alignment', 
            'shift_work_considerations', 'technical_readiness', 'safety_compliance'
        ]
        
        all_dimensions = core_dimensions + manufacturing_dimensions
        
        for dim in all_dimensions:
            if dim in assessment_data and 'score' in assessment_data[dim]:
                score = assessment_data[dim]['score']
                all_scores.append(score)
                dimension_scores[dim] = score
        
        overall_score = sum(all_scores) / len(all_scores) if all_scores else 0
        
        # Determine readiness level
        if overall_score >= 4.5:
            readiness_level = "Excellent"
        elif overall_score >= 3.5:
            readiness_level = "Good"
        elif overall_score >= 2.5:
            readiness_level = "Fair"
        elif overall_score >= 1.5:
            readiness_level = "Poor"
        else:
            readiness_level = "Critical"
        
        # Calculate manufacturing readiness analysis
        manufacturing_analysis = calculate_manufacturing_readiness_analysis(assessment_data)
        
        # Quick manufacturing-focused AI analysis
        ai_analysis = f"""# Manufacturing EAM Implementation Readiness Analysis

## Executive Summary
Your organization shows an overall readiness score of {overall_score:.1f}/5 for Manufacturing EAM implementation. 
Readiness Level: **{readiness_level}**

**Key Principle**: You can't have manufacturing excellence without maintenance excellence.

## Manufacturing Excellence Assessment
- **Maintenance-Operations Alignment**: {dimension_scores.get('maintenance_operations_alignment', 'N/A')}/5
- **Manufacturing Constraints Management**: {dimension_scores.get('manufacturing_constraints', 'N/A')}/5
- **Technical Infrastructure Readiness**: {dimension_scores.get('technical_readiness', 'N/A')}/5
- **Safety Compliance Integration**: {dimension_scores.get('safety_compliance', 'N/A')}/5

## Newton's Laws Application to Manufacturing
- **Organizational Inertia**: {manufacturing_analysis.get('inertia', {}).get('value', 0)} - {manufacturing_analysis.get('inertia', {}).get('interpretation', 'Unknown')}
- **Required Implementation Force**: {manufacturing_analysis.get('force', {}).get('required', 0)} units
- **Expected Resistance**: {manufacturing_analysis.get('reaction', {}).get('resistance', 0)} units

## IMPACT Phase Recommendations
Based on your readiness assessment, focus areas for each phase:

**Investigate & Assess**: Deepen understanding of maintenance-operations disconnects
**Mobilize & Prepare**: Build strong champion network across all shifts  
**Pilot & Adapt**: Select pilot area that demonstrates maintenance excellence impact
**Activate & Deploy**: Emphasize maintenance-manufacturing performance connection
**Cement & Transfer**: Embed maintenance excellence in organizational culture
**Track & Optimize**: Continuously demonstrate manufacturing performance gains

## Manufacturing-Specific Recommendations
1. Strengthen maintenance-operations collaboration through cross-functional teams
2. Address shift work coordination challenges with dedicated communication strategies
3. Leverage existing safety culture to drive maintenance excellence adoption
4. Ensure technical readiness through comprehensive training programs
5. Demonstrate clear connection between maintenance improvements and manufacturing KPIs

## Implementation Guarantee Eligibility
Based on current readiness: {'Eligible' if overall_score >= 3.0 else 'Requires Improvement'}

This assessment provides the foundation for your DigitalThinker Manufacturing EAM implementation success."""

        # Generate recommendations
        recommendations = [
            "Focus on strengthening maintenance-operations alignment as top priority",
            "Develop comprehensive change champion network covering all shifts",
            "Create clear communication strategy for manufacturing environment",
            "Establish baseline manufacturing performance metrics",
            "Design training programs specific to manufacturing constraints",
            "Build resistance management plan addressing manufacturing culture",
            "Demonstrate maintenance excellence impact on manufacturing KPIs"
        ]
        
        # Calculate success probability
        base_probability = (overall_score / 5) * 100
        manufacturing_bonus = dimension_scores.get('maintenance_operations_alignment', 3) * 5
        success_probability = min(95, base_probability + manufacturing_bonus)
        
        # Create assessment document
        assessment_doc = {
            "id": assessment_id,
            "user_id": current_user.id,
            "organization": current_user.organization,
            "project_name": assessment_data.get("project_name", ""),
            "project_type": "Manufacturing EAM Implementation",
            "assessment_version": "2.0",
            **assessment_data,  # Include all dimension data
            "overall_score": round(overall_score, 2),
            "readiness_level": readiness_level,
            "ai_analysis": ai_analysis,
            "recommendations": recommendations,
            "success_probability": round(success_probability, 1),
            "newton_analysis": manufacturing_analysis,
            "risk_factors": ["Manufacturing environment complexity", "Shift work coordination challenges"],
            "phase_recommendations": {
                "investigate": "Focus on maintenance-operations gap analysis",
                "mobilize": "Build cross-shift champion network",
                "pilot": "Select high-impact maintenance area for pilot",
                "activate": "Emphasize manufacturing performance connection", 
                "cement": "Embed maintenance excellence culture",
                "track": "Monitor manufacturing performance improvements"
            },
            "manufacturing_excellence_plan": {
                "focus_areas": ["Maintenance-Operations Integration", "Manufacturing Performance Metrics"],
                "key_strategies": ["Cross-functional collaboration", "Performance-based metrics"],
                "success_factors": ["Leadership commitment", "Cultural alignment"]
            },
            "guarantee_eligibility": overall_score >= 3.0,
            "created_at": now,
            "updated_at": now
        }
        
        # Save to database
        result = await db.assessments.insert_one(assessment_doc)
        assessment_doc["_id"] = str(result.inserted_id)
        
        return assessment_doc
        
    except Exception as e:
        print(f"Enhanced Assessment Creation Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create assessment: {str(e)}")
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