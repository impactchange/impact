from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class Deliverable(BaseModel):
    id: Optional[str] = None
    name: str
    type: str
    required: bool = True
    status: str = "pending"
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
    category: str
    status: str = "pending"
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    priority: str = "medium"
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
    status: str = "pending"
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
    status: str = "pending"
    completion_percentage: float
    deliverables_status: Dict[str, str]
    success_criteria_met: List[str]
    issues_identified: List[str]
    recommendations: List[str]
    next_phase_readiness: str
    notes: Optional[str] = None

class ProjectPhase(BaseModel):
    phase_name: str
    phase_number: int
    status: str = "not_started"
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    completion_percentage: float = 0.0
    success_status: Optional[str] = None
    success_reason: Optional[str] = None
    failure_reason: Optional[str] = None
    lessons_learned: Optional[str] = None
    budget_spent: float = 0.0
    scope_changes: List[str] = []
    recommendations: List[str] = []
    next_phase_suggestions: List[str] = []
    tasks: List[Dict] = []
    deliverables: List[Dict] = []
    risks_identified: List[str] = []
    mitigation_actions: List[str] = []

class Project(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    organization: str
    owner_id: str
    current_phase: str = "identify"
    status: str = "active"
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
