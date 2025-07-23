# backend/schemas/project.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Define nested models first
class ProjectPhase(BaseModel):
    phase_name: str
    phase_display_name: str
    phase_number: int
    status: str = "not_started"
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    completion_percentage: float = 0.0
    budget_spent: float = 0.0
    success_status: Optional[str] = None
    success_reason: Optional[str] = None
    failure_reason: Optional[str] = None
    lessons_learned: Optional[str] = None
    scope_changes: List[str] = []
    tasks_completed: List[str] = []
    deliverables_completed: List[str] = []
    risks_identified: List[str] = []
    mitigation_actions: List[str] = []
    recommendations: List[str] = []
    next_phase_suggestions: List[str] = []
    completion_analysis: Optional[Dict[str, Any]] = None
    analysis_generated_at: Optional[datetime] = None

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

# New class for updating phase progress
class PhaseProgressUpdate(BaseModel):
    completion_percentage: Optional[float] = None
    status: Optional[str] = None
    success_status: Optional[str] = None
    success_reason: Optional[str] = None
    failure_reason: Optional[str] = None
    lessons_learned: Optional[str] = None
    budget_spent: Optional[float] = None
    scope_changes: Optional[List[str]] = None
    tasks_completed: Optional[List[str]] = None
    deliverables_completed: Optional[List[str]] = None
    risks_identified: Optional[List[str]] = None

# Main Project Models
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
    stakeholders: Optional[List[Dict[str, Any]]] = None
    key_milestones: Optional[List[dict]] = None

class Project(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    organization: str
    owner_id: str
    current_phase: str = "investigate"
    status: str = "active"
    team_members: List[str] = []
    assigned_users: List[Dict[str, Any]] = []
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    budget: Optional[float] = None
    spent_budget: float = 0.0
    budget_alerts_enabled: bool = True
    progress_percentage: float = 0.0
    phase_progress: Dict[str, float] = {}
    phases: List[ProjectPhase] = []
    phase_start_dates: Dict[str, datetime] = {}
    phase_end_dates: Dict[str, datetime] = {}
    tasks: List[Task] = []
    deliverables: List[Deliverable] = []
    milestones: List[Milestone] = []
    gate_reviews: List[PhaseGateReview] = []
    newton_insights: Dict[str, Any] = {}
    assessment_id: Optional[str] = None
    stakeholders: List[Dict[str, Any]] = []
    risks: List[Dict[str, Any]] = []
    issues: List[Dict[str, Any]] = []
    last_update: Optional[datetime] = None
    next_milestone: Optional[str] = None
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
