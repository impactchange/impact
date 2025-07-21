from fastapi import APIRouter, HTTPException
from db.mongo import db
from schemas.assessment import ChangeReadinessAssessment
from services.readiness_engine import calculate_universal_readiness_analysis, generate_typed_ai_analysis
from datetime import datetime

router = APIRouter()

@router.post("/submit", status_code=201)
async def submit_assessment(assessment: ChangeReadinessAssessment):
    if not assessment.assessment_type:
        assessment.assessment_type = "general_readiness"
    score_components = [
        assessment.change_management_maturity,
        assessment.communication_effectiveness,
        assessment.leadership_support,
        assessment.workforce_adaptability,
        assessment.resource_adequacy
    ]
    total_score = sum([d.score for d in score_components])
    overall_score = round(total_score / len(score_components), 2)
    level = "High" if overall_score >= 4.0 else "Moderate" if overall_score >= 3.0 else "Low"
    analysis = calculate_universal_readiness_analysis(assessment.dict(), assessment.assessment_type)
    narrative = generate_typed_ai_analysis(assessment.dict(), assessment.assessment_type, overall_score, level, analysis)
    doc = assessment.dict()
    doc.update({
        "overall_score": overall_score,
        "ai_analysis": narrative,
        "newton_analysis": analysis,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    result = await db.assessments.insert_one(doc)
    return {"message": "Assessment submitted successfully", "id": str(result.inserted_id)}

@router.get("/all")
async def list_assessments():
    assessments = await db.assessments.find().to_list(100)
    return assessments
