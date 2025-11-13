# backend/routers/assessments.py (CLEANED ROUTER)

import uuid
from fastapi import APIRouter, HTTPException, Depends, status
from db.mongo import db
from schemas.user import User
from data.constants import ASSESSMENT_TYPES
from core.security import get_current_user
from typing import Dict, Any

# --- SERVICE LAYER IMPORTS ---
#from services.readiness_service import get_assessment_types_data, get_assessment_type_config_data
from services.readiness_engine import create_new_assessment_analysis
from services.assessment_utils import get_assessment_document, get_all_user_assessments_data
from services.llm_service import generate_customized_playbook


router = APIRouter(prefix="/api/assessments", tags=["Assessments"])

# --- CORE CRUD ENDPOINTS ---

@router.get("/types")
async def get_assessment_types():
    """Get all available assessment types"""
    return {"assessment_types": ASSESSMENT_TYPES}

@router.get("/types/{assessment_type}")
async def get_assessment_type_config(assessment_type: str):
    """Get specific assessment type configuration"""
    if assessment_type not in ASSESSMENT_TYPES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment type not found")
    return ASSESSMENT_TYPES[assessment_type]


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_assessment_typed(
    assessment_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Create a new assessment with type support and comprehensive analysis (Delegated to engine)"""
    try:
        # Delegation of all validation, analysis, and DB insertion logic
        return await create_new_assessment_analysis(assessment_data, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create assessment: {str(e)}")


@router.get("/")
async def get_all_user_assessments(current_user: User = Depends(get_current_user)):
    """Get all assessments for the current user (Delegated to utility)"""
    try:
        return await get_all_user_assessments_data(current_user.id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve assessments")


@router.get("/{assessment_id}")
async def get_single_assessment(assessment_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific assessment by ID for the current user (Delegated to utility)"""
    try:
        return await get_assessment_document(assessment_id, current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve assessment")


# --- INTELLIGENCE ENDPOINTS ---

@router.post("/{assessment_id}/customized-playbook")
async def generate_customized_playbook_endpoint(assessment_id: str, current_user: User = Depends(get_current_user)):
    """Generate customized change management playbook (Delegated to LLM Service)"""
    try:
        assessment = await get_assessment_document(assessment_id, current_user.id)
        playbook = await generate_customized_playbook(assessment)
        return playbook
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate playbook: {str(e)}")


@router.post("/{assessment_id}/implementation-plan")
async def generate_implementation_plan_endpoint(assessment_id: str, current_user: User = Depends(get_current_user)):
    """Generate customized week-by-week implementation plan (Placeholder for engine call)"""
    try:
        assessment = await get_assessment_document(assessment_id, current_user.id)
        # NOTE: Logic should be delegated to readiness_engine.py here
        return {"message": "Implementation plan generated successfully", "plan": {}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate implementation plan: {str(e)}")


@router.post("/{assessment_id}/predictive-analytics")
async def generate_predictive_analytics_endpoint(assessment_id: str, current_user: User = Depends(get_current_user)):
    """Generate comprehensive predictive analytics (Placeholder for predictive_analytics service call)"""
    try:
        assessment = await get_assessment_document(assessment_id, current_user.id)
        # NOTE: Logic should be delegated to predictive_analytics service here
        return {"message": "Predictive analytics generated successfully", "analytics": {}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate predictive analytics: {str(e)}")
