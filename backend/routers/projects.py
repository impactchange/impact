# backend/routers/projects.py (CLEANED ROUTER)

import uuid
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any
from datetime import datetime

# --- DATABASE & CORE IMPORTS ---
from db.mongo import db
from schemas.project import Project, ProjectUpdate, PhaseProgressUpdate, PhaseTransition, PhaseGateReview, ProjectFromAssessment, ProjectCreate
from schemas.user import User
from data.constants import IMPACT_PHASES

# --- SERVICE LAYER IMPORTS ---
from services.admin_services import get_project_document, create_new_project_service, create_project_from_assessment_service, update_project_details
from services.workflow_management import update_project_task, update_project_deliverable, perform_phase_transition, calculate_phase_progress, generate_phase_based_intelligence, generate_phase_completion_analysis
from services.budget_tracking import generate_detailed_budget_tracking
from services.project_forecasting import generate_advanced_project_forecasting, generate_stakeholder_communications, calculate_manufacturing_excellence_correlation
from services.predictive_analytics import generate_predictive_risk_trending, generate_real_time_recommendations


router = APIRouter(prefix="/api/projects", tags=["Projects"])

# --- CORE CRUD ENDPOINTS ---

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Project)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new project using the dedicated admin service."""
    try:
        return await create_new_project_service(project_data, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create project: {str(e)}")


@router.post("/from-assessment", status_code=status.HTTP_201_CREATED, response_model=Project)
async def create_project_from_assessment(
    project_data_from_assessment: ProjectFromAssessment,
    current_user: User = Depends(get_current_user)
):
    """Create project based on assessment recommendations using the service layer."""
    try:
        assessment = await db.assessments.find_one({"id": project_data_from_assessment.assessment_id, "user_id": current_user.id})
        if not assessment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
        
        return await create_project_from_assessment_service(
            project_data_from_assessment,
            current_user,
            assessment
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Project creation from assessment failed: {str(e)}")


@router.get("/")
async def get_user_projects(current_user: User = Depends(get_current_user)):
    """Get all projects belonging to the current user's organization."""
    try:
        projects_cursor = db.projects.find({"organization": current_user.organization})
        projects = await projects_cursor.to_list(100)
        for project in projects:
            project.pop("_id", None)
        return projects
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve projects: {str(e)}")


@router.get("/{project_id}")
async def get_single_project(project_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific project by ID using the admin service for authorization."""
    try:
        project_doc = await get_project_document(project_id, current_user.id)
        return project_doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve project: {str(e)}")


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    update_data: ProjectUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update project non-nested details using the dedicated admin service."""
    try:
        updated_project = await update_project_details(
            project_id,
            update_data.model_dump(exclude_unset=True),
            current_user.id
        )
        return updated_project

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update project: {str(e)}")


# --- WORKFLOW ENDPOINTS ---

@router.put("/{project_id}/phase")
async def transition_project_phase_endpoint(
    project_id: str,
    transition: PhaseTransition,
    current_user: User = Depends(get_current_user)
):
    """Transition project to the next phase using the dedicated workflow management service."""
    try:
        updated_project = await perform_phase_transition(project_id, transition, current_user.id)
        return {"message": f"Project successfully transitioned to {transition.to_phase} phase", "project": updated_project}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Phase transition failed: {str(e)}")


@router.put("/{project_id}/tasks/{task_id}")
async def update_task_endpoint(
    project_id: str,
    task_id: str,
    task_update: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Update task details using the workflow management service."""
    try:
        await update_project_task(
            project_id,
            task_id,
            task_update,
            current_user.id
        )
        return {"message": "Task updated successfully", "task_id": task_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Task update failed: {str(e)}")


@router.put("/{project_id}/deliverables/{deliverable_id}")
async def update_deliverable_endpoint(
    project_id: str,
    deliverable_id: str,
    deliverable_update: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Update deliverable details using the workflow management service."""
    try:
        await update_project_deliverable(
            project_id,
            deliverable_id,
            deliverable_update,
            current_user.id
        )
        return {"message": "Deliverable updated successfully", "deliverable_id": deliverable_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Deliverable update failed: {str(e)}")


@router.post("/{project_id}/gate-review", status_code=status.HTTP_201_CREATED)
async def create_gate_review_endpoint(
    project_id: str,
    gate_review_data: PhaseGateReview,
    current_user: User = Depends(get_current_user)
):
    """Create a new phase gate review."""
    try:
        project = await get_project_document(project_id, current_user.id)

        gate_review_data.id = str(uuid.uuid4())
        gate_review_data.project_id = project_id
        gate_review_data.reviewer_id = current_user.id
        gate_review_data.review_date = datetime.utcnow()

        # Recalculate progress for the specific phase being reviewed
        gate_review_data.completion_percentage = calculate_phase_progress(project, gate_review_data.phase)

        await db.projects.update_one(
            {"id": project_id},
            {
                "$push": {"gate_reviews": gate_review_data.model_dump()},
                "$set": {"updated_at": datetime.utcnow(), "last_update": datetime.utcnow()}
            }
        )

        return gate_review_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Gate review creation failed: {str(e)}")


# --- AI/ANALYTICS ENDPOINTS ---

@router.post("/{project_id}/phases/{phase_name}/intelligence")
async def generate_phase_intelligence_endpoint(
    project_id: str,
    phase_name: str,
    current_user: User = Depends(get_current_user)
):
    """Generate phase-based intelligence using the workflow management service."""
    try:
        project = await get_project_document(project_id, current_user.id)
        
        assessment = await db.assessments.find_one({"id": project.get("assessment_id"), "user_id": current_user.id})
        assessment_data = assessment if assessment else {}

        completed_phases = [p for p in project.get("phases", []) if p.get("status") == "completed"]

        phase_intelligence_result = generate_phase_based_intelligence(phase_name, assessment_data, project, completed_phases)

        return phase_intelligence_result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Phase Intelligence Error: {str(e)}")


@router.post("/{project_id}/phases/{phase_name}/complete", status_code=status.HTTP_200_OK)
async def complete_phase_with_analysis_endpoint(
    project_id: str,
    phase_name: str,
    completion_data: PhaseProgressUpdate,
    current_user: User = Depends(get_current_user)
):
    """Complete a phase, generate analysis, and update the project document."""
    try:
        project = await get_project_document(project_id, current_user.id)

        completed_phase_in_project_list = None
        phases = project.get("phases", [])
        for i, phase in enumerate(phases):
            if phase.get("phase_name") == phase_name:
                phases[i].update(completion_data.model_dump(exclude_unset=True))
                phases[i]["updated_at"] = datetime.utcnow()
                if completion_data.status == "completed":
                    phases[i]["completion_date"] = datetime.utcnow()
                completed_phase_in_project_list = phases[i]
                break

        if not completed_phase_in_project_list:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phase not found in project or already completed")

        await db.projects.update_one(
            {"id": project_id, "owner_id": current_user.id},
            {"$set": {"phases": phases, "updated_at": datetime.utcnow(), "last_update": datetime.utcnow()}}
        )

        updated_project_doc = await db.projects.find_one({"id": project_id})
        assessment = await db.assessments.find_one({"id": updated_project_doc.get("assessment_id"), "user_id": current_user.id})
        assessment_data = assessment if assessment else {}

        completion_analysis_result = generate_phase_completion_analysis(
            completed_phase_in_project_list, 
            assessment_data, 
            updated_project_doc
        )

        for i, phase in enumerate(phases):
            if phase.get("phase_name") == phase_name:
                phases[i]["completion_analysis"] = completion_analysis_result
                phases[i]["analysis_generated_at"] = datetime.utcnow()
                break

        await db.projects.update_one(
            {"id": project_id, "owner_id": current_user.id},
            {"$set": {"phases": phases, "updated_at": datetime.utcnow(), "last_update": datetime.utcnow()}}
        )

        # Final progress recalculation (Call the imported service function)
        await update_project_task(project_id, str(uuid.uuid4()), {}, current_user.id)

        return {
            "phase_name": phase_name,
            "completion_status": "completed",
            "completion_analysis": completion_analysis_result,
            "next_phase_recommendations": completion_analysis_result.get("recommendations_for_next_phase", []),
            "generated_at": datetime.utcnow()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to complete phase with analysis: {str(e)}")


@router.get("/{project_id}/workflow-status")
async def get_project_workflow_status_endpoint(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive workflow status for a project."""
    try:
        project = await get_project_document(project_id, current_user.id)
        
        phases = project.get("phases", [])

        phase_summary = {
            "total_phases": len(phases),
            "completed_phases": len([p for p in phases if p.get("status") == "completed"]),
            "in_progress_phases": len([p for p in phases if p.get("status") == "in_progress"]),
            "not_started_phases": len([p for p in phases if p.get("status") == "not_started"]),
            "failed_phases": len([p for p in phases if p.get("status") == "failed"]) 
        }

        overall_progress = project.get("progress_percentage", 0.0)
        total_budget_spent = sum(p.get("budget_spent", 0) for p in project.get("phases", []))
        total_budget = project.get("budget", 0)
        budget_utilization = (total_budget_spent / total_budget * 100) if total_budget > 0 else 0

        current_phase = next((p for p in phases if p.get("status") == "in_progress"), None)
        if not current_phase:
            current_phase = next((p for p in phases if p.get("status") == "not_started"), None)

        successful_phases = [p for p in phases if p.get("success_status") == "successful"]
        success_rate = (len(successful_phases) / len(phases) * 100) if phases else 0

        return {
            "project_id": project_id,
            "project_name": project.get("name", ""),
            "workflow_status": {
                "overall_progress": round(overall_progress, 1),
                "current_phase": current_phase.get("phase_name") if current_phase else None,
                "phase_summary": phase_summary,
                "budget_utilization": round(budget_utilization, 1),
                "total_budget_spent": total_budget_spent,
                "success_rate": round(success_rate, 1),
                "phases_detail": phases
            },
            "generated_at": datetime.utcnow()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get workflow status: {str(e)}")


@router.post("/{project_id}/risk-monitoring")
async def generate_real_time_risk_monitoring_endpoint(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate real-time risk monitoring dashboard for active projects."""
    try:
        project = await get_project_document(project_id, current_user.id)
        
        assessment = await db.assessments.find_one({"id": project.get("assessment_id"), "user_id": current_user.id})
        assessment_data = assessment if assessment else {}
        
        overall_progress = project.get("progress_percentage", 0)
        spent_budget = sum(p.get("budget_spent", 0) for p in project.get("phases", []))
        total_budget = project.get("budget", 0)
        budget_utilization = (spent_budget / total_budget * 100) if total_budget > 0 else 0
        
        risk_trending_data = generate_predictive_risk_trending(assessment_data, assessment_data.get("overall_score", 3.0))

        risk_alerts = []
        if budget_utilization > 80:
             risk_alerts.append({"type": "Budget", "severity": "High", "message": f"Budget utilization at {budget_utilization:.1f}% - immediate attention required", "recommended_action": "Review remaining activities and implement cost controls"})
        if overall_progress < 60 and budget_utilization > 70:
             risk_alerts.append({"type": "Schedule", "severity": "High", "message": "Project behind schedule with high budget utilization", "recommended_action": "Accelerate critical path activities and review scope"})

        risk_monitoring_result = {
            "project_id": project_id,
            "project_name": project.get("name", ""),
            "current_status": {
                "overall_progress": overall_progress,
                "health_status": project.get("health_status", "green"),
                "budget_utilization": budget_utilization
            },
            "risk_alerts": risk_alerts,
            "trend_analysis": { "predictive_trending_data": risk_trending_data },
            "predictive_insights": {
                "completion_probability": risk_trending_data["project_outlook"]["success_probability"] if "project_outlook" in risk_trending_data else 0,
                "budget_overrun_risk": risk_trending_data["budget_risk_analysis"]["risk_level"] if "budget_risk_analysis" in risk_trending_data else "Low",
            },
            "recommendations": generate_real_time_recommendations(risk_alerts, overall_progress, budget_utilization),
            "generated_at": datetime.utcnow()
        }

        return risk_monitoring_result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate risk monitoring: {str(e)}")


@router.post("/{project_id}/detailed-budget-tracking")
async def generate_detailed_budget_tracking_endpoint(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate detailed task-level and phase-level budget tracking using the dedicated service."""
    try:
        project = await get_project_document(project_id, current_user.id)
        
        assessment = await db.assessments.find_one({"id": project.get("assessment_id"), "user_id": current_user.id})
        assessment_data = assessment if assessment else {}

        budget_tracking_result = generate_detailed_budget_tracking(project, assessment_data, None)

        return budget_tracking_result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate detailed budget tracking: {str(e)}")


@router.post("/{project_id}/advanced-forecasting")
async def generate_advanced_project_forecasting_endpoint(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate advanced project outcome forecasting using the dedicated service."""
    try:
        project = await get_project_document(project_id, current_user.id)
        
        assessment = await db.assessments.find_one({"id": project.get("assessment_id"), "user_id": current_user.id})
        assessment_data = assessment if assessment else {}
        
        predictive_analytics_mock = generate_predictive_risk_trending(assessment_data, assessment_data.get("overall_score", 3.0))
        budget_tracking_mock = generate_detailed_budget_tracking(project, assessment_data, None)

        return generate_advanced_project_forecasting(project, assessment_data, predictive_analytics_mock, budget_tracking_mock)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate advanced forecasting: {str(e)}")


@router.post("/{project_id}/stakeholder-communications")
async def generate_stakeholder_communications_endpoint(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate automated stakeholder communication content using the dedicated service."""
    try:
        project = await get_project_document(project_id, current_user.id)
        
        assessment = await db.assessments.find_one({"id": project.get("assessment_id"), "user_id": current_user.id})
        assessment_data = assessment if assessment else {}
        
        budget_tracking_mock = generate_detailed_budget_tracking(project, assessment_data, None)
        predictive_analytics_mock = generate_predictive_risk_trending(assessment_data, assessment_data.get("overall_score", 3.0))
        project_forecasting_mock = generate_advanced_project_forecasting(project, assessment_data, predictive_analytics_mock, budget_tracking_mock)

        return generate_stakeholder_communications(project, budget_tracking_mock, project_forecasting_mock, assessment_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate stakeholder communications: {str(e)}")


@router.post("/{project_id}/manufacturing-excellence-tracking")
async def generate_manufacturing_excellence_tracking_endpoint(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate manufacturing excellence correlation tracking using the dedicated service."""
    try:
        project = await get_project_document(project_id, current_user.id)
        
        assessment = await db.assessments.find_one({"id": project.get("assessment_id"), "user_id": current_user.id})
        assessment_data = assessment if assessment else {}

        mock_outcomes = { "quality_achievement_probability": 80, "scope_completion_probability": 90 }
        
        excellence_tracking_result = calculate_manufacturing_excellence_correlation(assessment_data, mock_outcomes)

        maintenance_excellence_score = assessment_data.get("maintenance_operations_alignment", 3.0)
        
        performance_improvements = {
            "unplanned_downtime_reduction": min(60, max(10, maintenance_excellence_score * 12)),
            "overall_equipment_effectiveness": min(35, max(5, maintenance_excellence_score * 7)),
            "maintenance_cost_reduction": min(30, max(5, maintenance_excellence_score * 6)),
        }
        estimated_annual_savings = sum(performance_improvements.values()) * 1000
        implementation_cost = project.get("budget", 90000)
        roi_percentage = ((estimated_annual_savings - implementation_cost) / implementation_cost * 100) if implementation_cost > 0 else 0

        full_excellence_tracking_response = {
            "project_id": project_id,
            "project_name": project.get("name", ""),
            "maintenance_excellence": {
                "current_score": round(maintenance_excellence_score, 1),
                "potential_score": min(5.0, maintenance_excellence_score + 1.5),
                "improvement_pathway": excellence_tracking_result.get("excellence_pathway", []),
            },
            "performance_predictions": {
                "unplanned_downtime_reduction": f"{performance_improvements['unplanned_downtime_reduction']:.1f}%",
            },
            "roi_analysis": {
                "estimated_annual_savings": round(estimated_annual_savings, 0),
                "implementation_investment": implementation_cost,
                "roi_percentage": round(roi_percentage, 1),
                "business_case_strength": "Strong" if roi_percentage > 50 else "Moderate"
            },
            "correlation_metrics": {
                "maintenance_operations_correlation": excellence_tracking_result.get("correlation_strength", 0.0),
            },
            "generated_at": datetime.utcnow()
        }

        return full_excellence_tracking_response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate manufacturing excellence tracking: {str(e)}")
