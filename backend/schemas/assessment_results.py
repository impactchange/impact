# schema/assessment_result_schema.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class AssessmentInput(BaseModel):
    user_id: str
    organization: str
    project_name: str
    dimensions: Dict[str, int]  # e.g., {"leadership_support": 4, "communication_effectiveness": 3}
    notes: Optional[Dict[str, str]] = None  # e.g., {"leadership_support": "Strong buy-in from exec team"}


class AssessmentResult(BaseModel):
    id: str
    user_id: str
    organization: str
    project_name: str
    overall_score: float
    success_probability: float
    recommendations: List[str]
    risk_factors: List[str]
    phase_recommendations: Optional[Dict[str, str]] = None
    created_at: datetime


class AssessmentSummary(BaseModel):
    assessment_id: str
    project_name: str
    user: str
    score: float
    success_probability: float
    created_at: datetime
    status: str = "completed"
