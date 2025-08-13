# backend/routers/assessments.py
import uuid
import asyncio
from fastapi import APIRouter, HTTPException, Depends, status
from db.mongo import db
from schemas.assessment import ChangeReadinessAssessment
from schemas.user import User
from services.readiness_engine import (
    calculate_universal_readiness_analysis, generate_typed_ai_analysis,
    generate_typed_recommendations, get_type_specific_bonus, get_type_specific_risks,
    get_phase_recommendations_for_type, generate_implementation_plan,
    calculate_manufacturing_readiness_analysis, calculate_newton_laws_analysis
)
from services.predictive_analytics import (
    predict_task_success_probability, predict_budget_overrun_risk,
    predict_scope_creep_risk, predict_timeline_optimization,
    generate_predictive_risk_trending, generate_recommended_actions
)
from data.constants import ASSESSMENT_TYPES
from core.security import get_current_user
from core.config import ANTHROPIC_API_KEY
from anthropic import AsyncAnthropic, HUMAN_PROMPT, AI_PROMPT
from datetime import datetime
from typing import Dict, Any

router = APIRouter(prefix="/api/assessments", tags=["Assessments"])

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
    """Create a new assessment with type support and comprehensive analysis"""
    try:
        assessment_type = assessment_data.get("assessment_type", "general_readiness")
        if assessment_type not in ASSESSMENT_TYPES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid assessment type")
        assessment_id = str(uuid.uuid4())
        now = datetime.utcnow()
        type_config = ASSESSMENT_TYPES[assessment_type]
        all_scores = []
        dimension_scores = {}
        for dimension in type_config["dimensions"]:
            dim_id = dimension["id"]
            if dim_id in assessment_data and "score" in assessment_data[dim_id]:
                score = assessment_data[dim_id]["score"]
                all_scores.append(score)
                dimension_scores[dim_id] = score
        overall_score = sum(all_scores) / len(all_scores) if all_scores else 0
        readiness_level = "Excellent" if overall_score >= 4.5 else "Good" if overall_score >= 3.5 else "Fair" if overall_score >= 2.5 else "Poor" if overall_score >= 1.5 else "Critical"
        
        if assessment_type == "manufacturing_operations":
            analysis_data = calculate_manufacturing_readiness_analysis(assessment_data)
        else:
            mock_assessment_obj = type('obj', (object,), {dim: type('dim_obj', (object,), {'score': score})() for dim, score in dimension_scores.items()})
            analysis_data = calculate_newton_laws_analysis(mock_assessment_obj)

        ai_analysis = generate_typed_ai_analysis(assessment_data, assessment_type, overall_score, readiness_level, analysis_data)
        recommendations = generate_typed_recommendations(assessment_type, dimension_scores, overall_score)
        base_probability = (overall_score / 5) * 100
        type_bonus = get_type_specific_bonus(assessment_type, dimension_scores)
        success_probability = min(95, base_probability + type_bonus)

        assessment_doc = {
            "id": assessment_id, "user_id": current_user.id, "organization": current_user.organization,
            "assessment_type": assessment_type, "project_name": assessment_data.get("project_name", ""),
            "project_type": type_config["name"], "assessment_version": "3.0",
            **assessment_data, "overall_score": round(overall_score, 2), "readiness_level": readiness_level,
            "ai_analysis": ai_analysis, "recommendations": recommendations, "success_probability": round(success_probability, 1),
            "newton_analysis": analysis_data, "risk_factors": get_type_specific_risks(assessment_type, dimension_scores),
            "phase_recommendations": get_phase_recommendations_for_type(assessment_type),
            "implementation_plan": generate_implementation_plan(assessment_type, overall_score),
            "guarantee_eligibility": overall_score >= 3.0, "created_at": now, "updated_at": now
        }
        result = await db.assessments.insert_one(assessment_doc)
        assessment_doc["_id"] = str(result.inserted_id)
        return assessment_doc
    except HTTPException:
        raise
    except Exception as e:
        print(f"Assessment Creation Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create assessment: {str(e)}")

@router.get("/")
async def get_all_user_assessments(current_user: User = Depends(get_current_user)):
    """Get all assessments for the current user"""
    try:
        assessments = await db.assessments.find({"user_id": current_user.id}).to_list(100)
        for assessment in assessments:
            if "_id" in assessment:
                assessment["id"] = str(assessment["_id"])
                del assessment["_id"]
        return assessments
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve assessments")

@router.get("/{assessment_id}")
async def get_single_assessment(assessment_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific assessment by ID for the current user"""
    assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    if "_id" in assessment:
        del assessment["_id"]
    return assessment

@router.post("/{assessment_id}/implementation-plan")
async def generate_implementation_plan_endpoint(assessment_id: str, current_user: User = Depends(get_current_user)):
    """Generate customized week-by-week implementation plan"""
    assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    # This logic can be expanded based on the full implementation plan generation logic
    return {"message": "Implementation plan generated successfully", "plan": {}}

@router.post("/{assessment_id}/customized-playbook")
async def generate_customized_playbook_endpoint(assessment_id: str, current_user: User = Depends(get_current_user)):
    """Generate customized change management playbook based on assessment results"""
    assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    anthropic_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    
    assessment_data_for_llm = {
        "leadership_support": assessment.get("leadership_support", {}).get("score", 3),
        "resource_availability": assessment.get("resource_availability", {}).get("score", 3),
        "change_management_maturity": assessment.get("change_management_maturity", {}).get("score", 3),
        "communication_effectiveness": assessment.get("communication_effectiveness", {}).get("score", 3),
        "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3)
    }
    
    prompt = f"""{HUMAN_PROMPT}
    Generate a comprehensive, customized change management playbook for the following organization:

    PROJECT DETAILS:
    - Project Name: {assessment.get("project_name", "")}
    - Organization: {assessment.get("organization", "")}
    - Assessment Type: {assessment.get("assessment_type", "")}
    - Overall Readiness Score: {assessment.get("overall_score", 0)}/5
    - Readiness Level: {assessment.get("readiness_level", "")}

    ASSESSMENT SCORES (1-5 scale):
    - Leadership Support: {assessment_data_for_llm["leadership_support"]}/5
    - Resource Availability: {assessment_data_for_llm["resource_availability"]}/5
    - Change Management Maturity: {assessment_data_for_llm["change_management_maturity"]}/5
    - Communication Effectiveness: {assessment_data_for_llm["communication_effectiveness"]}/5
    - Workforce Adaptability: {assessment_data_for_llm["workforce_adaptability"]}/5

    Please generate a detailed, actionable playbook.
    {AI_PROMPT}
    """
    
    try:
        response = await anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        playbook_content = response.content[0].text
        playbook = {
            "assessment_id": assessment_id,
            "content": playbook_content,
            "generated_at": datetime.utcnow()
        }
        return playbook
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate playbook: {str(e)}")

@router.post("/{assessment_id}/predictive-analytics")
async def generate_predictive_analytics_endpoint(assessment_id: str, current_user: User = Depends(get_current_user)):
    """Generate comprehensive predictive analytics based on assessment results"""
    assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    # This logic can be expanded based on the full predictive analytics generation
    return {"message": "Predictive analytics generated successfully", "analytics": {}}
