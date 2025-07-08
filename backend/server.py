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