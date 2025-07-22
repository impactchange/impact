# backend/schemas/project.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Define nested models first
class ProjectPhase(BaseModel):
    phase_name: str
    phase_display_name: str
    phase_number: int
    status: str = "not_started"  # not_started, in_progress, completed, failed
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    completion_percentage: float = 0.0
    budget_spent: float = 0.0
    success_status: Optional[str] = None  # successful, failed, partially_successful
    success_reason: Optional[str] = None
    failure_reason: Optional[str] = None
    lessons_learned: Optional[str] = None
    scope_changes: List[str] = []
    tasks_completed: List[str] = [] # List of task IDs that are completed in this phase
    deliverables_completed: List[str] = [] # List of deliverable IDs that are completed/approved in this phase
    risks_identified: List[str] = []
    mitigation_actions: List[str] = []
    recommendations: List[str] = []
    next_phase_suggestions: List[str] = []
    completion_analysis: Optional[Dict[str, Any]] = None # To store generated analysis upon phase completion
    analysis_generated_at: Optional[datetime] = None


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
    deliverables: List[str] = [] # List of deliverable IDs associated with this milestone
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
    deliverables_status: Dict[str, str] # {deliverable_id: status}
    success_criteria_met: List[str]
    issues_identified: List[str]
    recommendations: List[str]
    next_phase_readiness: str  # ready, not_ready, conditional
    notes: Optional[str] = None

# Main Project Models
class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    description: Optional[str] = None
    client_organization: Optional[str] = None
    objectives: Optional[List[str]] = None
    scope: Optional[str] = None
    total_budget: Optional[float] = None
    estimated_end_date: Optional[str] = None # Keep as str for incoming
    current_phase: Optional[str] = None
    health_status: Optional[str] = None
    spent_budget: Optional[float] = None
    phases: Optional[List[ProjectPhase]] = None
    team_members: Optional[List[str]] = None
    stakeholders: Optional[List[Dict[str, Any]]] = None # Changed to Dict[str, Any] as it's typically more flexible
    key_milestones: Optional[List[dict]] = None # Changed to dict for flexibility


class Project(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    organization: str
    owner_id: str # Renamed from user_id to owner_id to be more specific for project owner
    current_phase: str = "investigate" # Default starting phase
    status: str = "active"  # active, on_hold, completed, cancelled
    team_members: List[str] = [] # List of user IDs
    assigned_users: List[Dict[str, Any]] = [] # Detailed assignments: user_id, role, permissions, etc.
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    budget: Optional[float] = None # total_budget
    spent_budget: float = 0.0 # spent_budget
    budget_alerts_enabled: bool = True # Flag for budget alerts
    progress_percentage: float = 0.0 # overall_progress
    phase_progress: Dict[str, float] = {} # phase_progress mapping phase_name to percentage
    phases: List[ProjectPhase] = [] # Detailed phase objects
    phase_start_dates: Dict[str, datetime] = {} # Track phase start dates
    phase_end_dates: Dict[str, datetime] = {} # Track phase end dates
    tasks: List[Task] = []
    deliverables: List[Deliverable] = []
    milestones: List[Milestone] = []
    gate_reviews: List[PhaseGateReview] = []
    newton_insights: Dict[str, Any] = {} # From readiness assessment
    assessment_id: Optional[str] = None # Link to the assessment
    stakeholders: List[Dict[str, Any]] = [] # Full stakeholder details
    risks: List[Dict[str, Any]] = [] # Project-level risks
    issues: List[Dict[str, Any]] = [] # Project-level issues
    last_update: Optional[datetime] = None # Last update timestamp
    next_milestone: Optional[str] = None # ID of the next upcoming milestone
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