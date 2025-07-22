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
from emergentintegrations.llm.chat import LlmChat, UserMessage
from datetime import datetime
# ... (rest of the router code)

router = APIRouter(prefix="/assessments", tags=["Assessments"]) # Added prefix and tags

@router.get("/types")
async def get_assessment_types():
    """Get all available assessment types"""
    return {"assessment_types": ASSESSMENT_TYPES}

@router.get("/types/{assessment_type}")
async def get_assessment_type_config(assessment_type: str): # Renamed to avoid conflict with imported ASSESSMENT_TYPES
    """Get specific assessment type configuration"""
    if assessment_type not in ASSESSMENT_TYPES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment type not found")
    return ASSESSMENT_TYPES[assessment_type]

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_assessment_typed(
    assessment_data: Dict[str, Any], # Use Dict[str, Any] for raw data, then validate/process
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

        # Collect scores based on the specific dimensions for the assessment type
        for dimension in type_config["dimensions"]:
            dim_id = dimension["id"]
            # Check if the dimension exists and has a 'score'
            if dim_id in assessment_data and "score" in assessment_data[dim_id]:
                score = assessment_data[dim_id]["score"]
                all_scores.append(score)
                dimension_scores[dim_id] = score
            elif dim_id in assessment_data and isinstance(assessment_data[dim_id], dict) and "score" not in assessment_data[dim_id]:
                 # Handle cases where dimension data is provided but score is missing, e.g., for notes only
                 pass
            else:
                # If a required dimension score is missing, you might want to raise an error
                # For now, we'll just skip it.
                pass

        overall_score = sum(all_scores) / len(all_scores) if all_scores else 0

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

        # Calculate Newton's Laws analysis based on assessment type
        if assessment_type == "manufacturing_operations":
            analysis_data = calculate_manufacturing_readiness_analysis(assessment_data)
        else:
            # For non-manufacturing, we'd ideally pass a ChangeReadinessAssessment instance if validation is needed
            # For simplicity, assuming the structure is compatible with calculate_newton_laws_analysis
            # If ChangeReadinessAssessment object is required, assessment_data needs to be parsed into it.
            # Example: assessment_object = ChangeReadinessAssessment(**assessment_data)
            # For now, passing assessment_data dict directly, might need adjustments based on schema
            mock_assessment_obj = type('obj', (object,), {dim: type('dim_obj', (object,), {'score': score})() for dim, score in dimension_scores.items()})
            analysis_data = calculate_newton_laws_analysis(mock_assessment_obj)


        # Generate AI analysis based on type
        # Note: The original server.py had custom AI analysis strings for manufacturing.
        # Here we'll rely on generate_typed_ai_analysis, which has its own logic based on type_names.
        # If the manufacturing-specific AI narrative from server.py is critical, it needs special handling.
        ai_analysis = generate_typed_ai_analysis(assessment_data, assessment_type, overall_score, readiness_level, analysis_data)

        # Generate recommendations based on type
        recommendations = generate_typed_recommendations(assessment_type, dimension_scores, overall_score)

        # Calculate success probability
        base_probability = (overall_score / 5) * 100
        type_bonus = get_type_specific_bonus(assessment_type, dimension_scores)
        success_probability = min(95, base_probability + type_bonus)

        # Create assessment document
        assessment_doc = {
            "id": assessment_id,
            "user_id": current_user.id,
            "organization": current_user.organization,
            "assessment_type": assessment_type,
            "project_name": assessment_data.get("project_name", ""),
            "project_type": type_config["name"],
            "assessment_version": "3.0", # Or "2.0" for manufacturing if separate versioning is needed
            **assessment_data,  # Include all dimension data as received
            "overall_score": round(overall_score, 2),
            "readiness_level": readiness_level,
            "ai_analysis": ai_analysis,
            "recommendations": recommendations,
            "success_probability": round(success_probability, 1),
            "newton_analysis": analysis_data,
            "risk_factors": get_type_specific_risks(assessment_type, dimension_scores),
            "phase_recommendations": get_phase_recommendations_for_type(assessment_type),
            "implementation_plan": generate_implementation_plan(assessment_type, overall_score),
            "guarantee_eligibility": overall_score >= 3.0,
            "created_at": now,
            "updated_at": now
        }

        result = await db.assessments.insert_one(assessment_doc)
        assessment_doc["_id"] = str(result.inserted_id) # Ensure _id is converted for JSON serialization

        return assessment_doc

    except HTTPException:
        raise # Re-raise FastAPI HTTPExceptions
    except Exception as e:
        print(f"Assessment Creation Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create assessment: {str(e)}")


@router.get("/")
async def get_all_user_assessments(current_user: User = Depends(get_current_user)):
    """Get all assessments for the current user"""
    try:
        assessments = await db.assessments.find({"user_id": current_user.id}).to_list(100)
        # Convert ObjectId to string and remove _id field if present
        for assessment in assessments:
            assessment["id"] = str(assessment.get("id")) # Ensure 'id' field is string
            if "_id" in assessment:
                del assessment["_id"]
        return assessments
    except Exception as e:
        print(f"Get Assessments Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve assessments: {str(e)}")

@router.get("/{assessment_id}")
async def get_single_assessment(assessment_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific assessment by ID for the current user"""
    try:
        assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
        if not assessment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
        if "_id" in assessment:
            del assessment["_id"]
        return assessment
    except HTTPException:
        raise # Re-raise FastAPI HTTPExceptions
    except Exception as e:
        print(f"Get Assessment Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve assessment: {str(e)}")


@router.post("/{assessment_id}/implementation-plan")
async def generate_implementation_plan_endpoint(
    assessment_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate customized week-by-week implementation plan based on assessment results"""
    try:
        assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
        if not assessment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

        assessment_data = {
            "leadership_support": assessment.get("leadership_support", {}).get("score", 3),
            "resource_availability": assessment.get("resource_availability", {}).get("score", 3),
            "change_management_maturity": assessment.get("change_management_maturity", {}).get("score", 3),
            "communication_effectiveness": assessment.get("communication_effectiveness", {}).get("score", 3),
            "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3)
        }

        assessment_type = assessment.get("assessment_type", "general_readiness")
        overall_score = assessment.get("overall_score", 3.0)

        implementation_plan_result = generate_implementation_plan(assessment_data, assessment_type, overall_score)

        implementation_plan_result["metadata"] = {
            "assessment_id": assessment_id,
            "project_name": assessment.get("project_name", ""),
            "organization": assessment.get("organization", ""),
            "assessment_type": assessment_type,
            "overall_readiness_score": overall_score,
            "readiness_level": assessment.get("readiness_level", ""),
            "generated_at": datetime.utcnow(),
            "generated_by": current_user.full_name
        }

        return implementation_plan_result

    except HTTPException:
        raise
    except Exception as e:
        print(f"Implementation Plan Generation Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate implementation plan: {str(e)}")


@router.post("/{assessment_id}/customized-playbook")
async def generate_customized_playbook_endpoint(
    assessment_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate customized change management playbook based on assessment results"""
    try:
        assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
        if not assessment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

        chat = LlmChat(
            api_key=ANTHROPIC_API_KEY,
            session_id=f"playbook_generation_{assessment_id}",
            system_message="""You are an expert change management consultant specializing in the IMPACT Methodology and DigitalThinker's proven approach to manufacturing excellence.

            Generate a comprehensive, customized change management playbook based on the assessment results. The playbook should be tailored to the specific organization's readiness level, strengths, and challenges.

            Structure the playbook with:
            1. Executive Summary
            2. Assessment-Based Recommendations
            3. Phase-by-Phase Implementation Guide
            4. Risk Mitigation Strategies
            5. Success Metrics and Monitoring
            6. Stakeholder Engagement Strategy
            7. Communication Plan
            8. Training and Development Plan
            9. Resistance Management Approach
            10. Guarantee-Backed Success Framework

            Focus on practical, actionable guidance that consultants can implement immediately."""
        ).with_model("anthropic", "claude-sonnet-4-20250514")

        assessment_data_for_llm = {
            "leadership_support": assessment.get("leadership_support", {}).get("score", 3),
            "resource_availability": assessment.get("resource_availability", {}).get("score", 3),
            "change_management_maturity": assessment.get("change_management_maturity", {}).get("score", 3),
            "communication_effectiveness": assessment.get("communication_effectiveness", {}).get("score", 3),
            "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3)
        }

        prompt = f"""
        Generate a comprehensive, customized change management playbook for the following organization:

        PROJECT DETAILS:
        • Project Name: {assessment.get("project_name", "")}
        • Organization: {assessment.get("organization", "")}
        • Assessment Type: {assessment.get("assessment_type", "")}
        • Overall Readiness Score: {assessment.get("overall_score", 0)}/5
        • Readiness Level: {assessment.get("readiness_level", "")}

        ASSESSMENT SCORES (1-5 scale):
        • Leadership Support: {assessment_data_for_llm["leadership_support"]}/5
        • Resource Availability: {assessment_data_for_llm["resource_availability"]}/5
        • Change Management Maturity: {assessment_data_for_llm["change_management_maturity"]}/5
        • Communication Effectiveness: {assessment_data_for_llm["communication_effectiveness"]}/5
        • Workforce Adaptability: {assessment_data_for_llm["workforce_adaptability"]}/5

        EXISTING RECOMMENDATIONS:
        {'; '.join(assessment.get("recommendations", []))}

        RISK FACTORS:
        {'; '.join(assessment.get("risk_factors", []))}

        SUCCESS PROBABILITY: {assessment.get("success_probability", 0)}%

        Please generate a detailed, actionable playbook that addresses the specific strengths and challenges identified in this assessment. Focus on practical implementation guidance that will ensure project success.

        The playbook should be approximately 2000-3000 words and include specific tactics, tools, and strategies tailored to this organization's unique profile.
        """

        response = await asyncio.wait_for(chat.send_message(UserMessage(prompt)), timeout=60.0) # Added timeout
        playbook_content = response if isinstance(response, str) else response.text

        playbook = {
            "assessment_id": assessment_id,
            "project_name": assessment.get("project_name", ""),
            "organization": assessment.get("organization", ""),
            "assessment_type": assessment.get("assessment_type", ""),
            "overall_readiness_score": assessment.get("overall_score", 0),
            "readiness_level": assessment.get("readiness_level", ""),
            "success_probability": assessment.get("success_probability", 0),
            "content": playbook_content,
            "generated_at": datetime.utcnow(),
            "generated_by": current_user.full_name,
            "version": "1.0",
            "customization_factors": assessment_data_for_llm
        }

        return playbook

    except asyncio.TimeoutError:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="AI playbook generation timed out.")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Customized Playbook Generation Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate customized playbook: {str(e)}")


@router.post("/{assessment_id}/predictive-analytics")
async def generate_predictive_analytics_endpoint(
    assessment_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate comprehensive predictive analytics based on assessment results"""
    try:
        assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
        if not assessment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

        assessment_data = {
            "leadership_support": assessment.get("leadership_support", {}).get("score", 3),
            "resource_availability": assessment.get("resource_availability", {}).get("score", 3),
            "change_management_maturity": assessment.get("change_management_maturity", {}).get("score", 3),
            "communication_effectiveness": assessment.get("communication_effectiveness", {}).get("score", 3),
            "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3),
            "technical_readiness": assessment.get("technical_readiness", {}).get("score", 3),
            "stakeholder_engagement": assessment.get("stakeholder_engagement", {}).get("score", 3)
        }

        assessment_type = assessment.get("assessment_type", "general_readiness")
        overall_score = assessment.get("overall_score", 3.0)

        # Generate task-specific success predictions
        task_predictions = []
        for task_num in range(1, 11): # Assuming 10 generic tasks for now
            task_id = f"task_{task_num}"
            prediction = predict_task_success_probability(task_id, assessment_data, overall_score)
            task_predictions.append(prediction)

        # Estimate total budget from implementation plan (default if not available)
        # In a real app, this should come from project data or actual implementation plan
        total_budget = assessment.get("implementation_plan", {}).get("summary", {}).get("total_budget", 90000)


        # Generate predictive analytics from the predictive_analytics service
        budget_risk = predict_budget_overrun_risk(assessment_data, overall_score, total_budget)
        scope_creep_risk = predict_scope_creep_risk(assessment_data, assessment_type)
        timeline_optimization = predict_timeline_optimization(assessment_data, overall_score)
        risk_trending = generate_predictive_risk_trending(assessment_data, overall_score)

        # Compile comprehensive analytics
        predictive_analytics_result = {
            "assessment_id": assessment_id,
            "project_name": assessment.get("project_name", ""),
            "organization": assessment.get("organization", ""),
            "assessment_type": assessment_type,
            "overall_readiness_score": overall_score,
            "generated_at": datetime.utcnow(),
            "generated_by": current_user.full_name,

            "task_success_predictions": task_predictions,
            "highest_risk_tasks": sorted(task_predictions, key=lambda x: x["success_probability"])[:3],
            "lowest_risk_tasks": sorted(task_predictions, key=lambda x: x["success_probability"], reverse=True)[:3],

            "budget_risk_analysis": budget_risk,
            "scope_creep_analysis": scope_creep_risk,
            "timeline_optimization": timeline_optimization,
            "risk_trending": risk_trending,

            "project_outlook": {
                "overall_risk_level": "High" if overall_score < 2.5 else "Medium" if overall_score < 3.5 else "Low",
                "success_probability": round(min(95, max(15, overall_score * 18)), 1),
                "recommended_actions": generate_recommended_actions(task_predictions, budget_risk, scope_creep_risk),
                "critical_success_factors": assessment.get("critical_success_factors", []), # Use actual assessment field
                "key_monitoring_points": risk_trending["critical_monitoring_weeks"]
            }
        }

        return predictive_analytics_result

    except HTTPException:
        raise
    except Exception as e:
        print(f"Predictive Analytics Generation Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate predictive analytics: {str(e)}")