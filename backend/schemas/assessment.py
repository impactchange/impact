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
