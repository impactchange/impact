from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

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
    category: str = "core"
    improvement_actions: List[str] = []
    priority: str = "medium"
    impact_on_operations: Optional[float] = None
    current_state_description: Optional[str] = None
    target_state_description: Optional[str] = None
    responsible_stakeholders: List[str] = []
    dependencies: List[str] = []
    implementation_complexity: str = "medium"
    resource_requirements: Dict[str, Any] = {}
    success_criteria: List[str] = []
    risks: List[Dict[str, Any]] = []
    timeline_estimate: Optional[int] = None
    cost_estimate: Optional[float] = None
    roi_estimate: Optional[float] = None
    kpis: List[str] = []
    assessment_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    status: str = "pending"
    completion_percentage: float = 0.0
    actual_impact: Optional[float] = None
    lessons_learned: List[str] = []
    related_dimensions: List[str] = []