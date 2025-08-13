# backend/routers/projects.py
import uuid
from fastapi import APIRouter, HTTPException, Depends, status
from db.mongo import db
from schemas.project import (
    Project, ProjectUpdate, PhaseProgressUpdate, PhaseTransition, PhaseGateReview,
    ProjectFromAssessment, Task, Deliverable, Milestone, ProjectPhase # Import all necessary schemas
)
from schemas.user import User # To get current_user details
from core.security import get_current_user # Dependency for authenticated routes
from data.constants import IMPACT_PHASES # To use phase configurations
from services.workflow_management import (
    generate_comprehensive_tasks_for_phase,
    generate_deliverables_for_phase,
    generate_milestones_for_phase,
    calculate_project_progress,
    calculate_phase_progress,
    generate_phase_based_intelligence,
    generate_phase_completion_analysis
)
from services.budget_tracking import generate_detailed_budget_tracking # For detailed budget tracking endpoint
from services.project_forecasting import (
    generate_advanced_project_forecasting,
    generate_stakeholder_communications,
    calculate_manufacturing_excellence_correlation # Specific for manufacturing excellence
)
# Assuming some helper functions for real-time risk recommendations might be here or from predictive_analytics
# As per our plan, generate_recommended_actions and generate_real_time_recommendations should be in predictive_analytics.py or a new common_utils
from services.predictive_analytics import (
    generate_recommended_actions, # Used by predictive analytics insight
    generate_predictive_risk_trending, # Used by real-time risk monitoring
    predict_task_success_probability, # Needed for generating comprehensive predictive analytics
    predict_budget_overrun_risk, # Needed for generating comprehensive predictive analytics
    predict_scope_creep_risk, # Needed for generating comprehensive predictive analytics
    predict_timeline_optimization # Needed for generating comprehensive predictive analytics
)
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

router = APIRouter(prefix="/api/projects", tags=["Projects"])

@router.post("/", status_code=status.HTTP_201_CREATED) # Changed from /create to /
async def create_project(
    project_data: Project, # Using the Project Pydantic model for input validation
    current_user: User = Depends(get_current_user)
):
    """Create a new project"""
    try:
        project_id = str(uuid.uuid4())
        now = datetime.utcnow()

        # Check for existing project name within the user's organization
        existing_project = await db.projects.find_one({
            "name": project_data.name,
            "organization": current_user.organization
        })
        if existing_project:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project with this name already exists in your organization.")

        # Set project metadata
        project_data.id = project_id
        project_data.owner_id = current_user.id
        project_data.organization = current_user.organization
        project_data.current_phase = "investigate" # Default starting phase
        project_data.start_date = now
        project_data.created_at = now
        project_data.updated_at = now
        project_data.last_update = now # Ensure last_update is set on creation

        # Initialize phases list with detailed phase objects
        project_data.phases = [
            ProjectPhase(
                phase_name=phase_key,
                phase_display_name=phase_info["name"],
                phase_number=phase_info["order"]
            )
            for phase_key, phase_info in IMPACT_PHASES.items()
        ]

        # Initialize phase progress dictionary
        project_data.phase_progress = {phase: 0.0 for phase in IMPACT_PHASES.keys()}

        # Generate comprehensive tasks, deliverables, and milestones for the initial phase (Investigate & Assess)
        # Assuming tasks/deliverables/milestones are nested within the Project model for simplicity
        initial_tasks_raw = generate_comprehensive_tasks_for_phase("investigate", project_id)
        initial_deliverables_raw = generate_deliverables_for_phase("investigate", project_id)
        initial_milestones_raw = generate_milestones_for_phase("investigate", project_id, now)

        project_data.tasks = [Task(**task) for task in initial_tasks_raw]
        project_data.deliverables = [Deliverable(**deliv) for deliv in initial_deliverables_raw]
        project_data.milestones = [Milestone(**milestone) for milestone in initial_milestones_raw]

        # Calculate initial progress
        project_data.progress_percentage = calculate_project_progress(project_data.dict())
        project_data.phases[0].completion_percentage = calculate_phase_progress(project_data.dict(), "investigate")


        # Save to database
        project_doc = project_data.model_dump(by_alias=False) # Use model_dump for Pydantic v2 or dict() for v1
        # Remove _id if it somehow got generated by Pydantic before MongoDB adds it
        project_doc.pop("_id", None)
        await db.projects.insert_one(project_doc)

        # Return the created project (ensure it's serializable)
        project_doc["_id"] = str(project_doc.get("_id", project_id)) # Use existing _id or fallback to project_id string
        return Project(**project_doc)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Project Creation Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create project: {str(e)}")

@router.post("/from-assessment", status_code=status.HTTP_201_CREATED)
async def create_project_from_assessment(
    project_data_from_assessment: ProjectFromAssessment,
    current_user: User = Depends(get_current_user)
):
    """Create project based on assessment recommendations"""
    try:
        assessment = await db.assessments.find_one({"id": project_data_from_assessment.assessment_id, "user_id": current_user.id})
        if not assessment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

        project_id = str(uuid.uuid4())
        now = datetime.utcnow()

        recommended_project_config = assessment.get("recommended_project", {})
        suggested_duration_weeks = recommended_project_config.get("suggested_duration_weeks", 16)
        target_completion = project_data_from_assessment.target_completion_date or (now + timedelta(weeks=suggested_duration_weeks))

        # Create base project instance
        new_project = Project(
            id=project_id,
            name=project_data_from_assessment.project_name,
            description=project_data_from_assessment.description,
            organization=current_user.organization,
            owner_id=current_user.id,
            current_phase="investigate",
            status="active",
            start_date=now,
            target_completion_date=target_completion,
            budget=project_data_from_assessment.budget,
            assessment_id=project_data_from_assessment.assessment_id,
            newton_insights=assessment.get("newton_analysis", {}),
            created_at=now,
            updated_at=now,
            last_update=now,
            # Initialize phases list with detailed phase objects
            phases=[
                ProjectPhase(
                    phase_name=phase_key,
                    phase_display_name=phase_info["name"],
                    phase_number=phase_info["order"]
                )
                for phase_key, phase_info in IMPACT_PHASES.items()
            ],
            phase_progress = {phase: 0.0 for phase in IMPACT_PHASES.keys()}
        )

        all_tasks_raw = []
        all_deliverables_raw = []
        all_milestones_raw = []

        # Generate comprehensive project structure for all phases based on assessment
        for phase_name_short in IMPACT_PHASES.keys():
            phase_tasks = generate_comprehensive_tasks_for_phase(phase_name_short, project_id)
            phase_deliverables = generate_deliverables_for_phase(phase_name_short, project_id)
            # Pass new_project.start_date for milestone generation to ensure consistent date logic
            phase_milestones = generate_milestones_for_phase(phase_name_short, project_id, new_project.start_date)

            all_tasks_raw.extend(phase_tasks)
            all_deliverables_raw.extend(phase_deliverables)
            all_milestones_raw.extend(phase_milestones)

        new_project.tasks = [Task(**task) for task in all_tasks_raw]
        new_project.deliverables = [Deliverable(**deliv) for deliv in all_deliverables_raw]
        new_project.milestones = [Milestone(**milestone) for milestone in all_milestones_raw]

        # Calculate initial progress for the entire project and per phase
        new_project.progress_percentage = calculate_project_progress(new_project.dict())
        for phase_name_short in IMPACT_PHASES.keys():
            new_project.phase_progress[phase_name_short] = calculate_phase_progress(new_project.dict(), phase_name_short)

        # Save to database
        project_doc = new_project.model_dump(by_alias=False) # Use model_dump for Pydantic v2
        project_doc.pop("_id", None)
        await db.projects.insert_one(project_doc)

        return Project(**project_doc)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Project creation from assessment failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Project creation from assessment failed: {str(e)}")


@router.get("/")
async def get_user_projects(current_user: User = Depends(get_current_user)):
    """Get projects belonging to the current user's organization"""
    try:
        projects = await db.projects.find({"organization": current_user.organization}).to_list(100)
        for project in projects:
            project["id"] = str(project.get("id")) # Ensure 'id' field is string
            if "_id" in project:
                del project["_id"]
        return projects
    except Exception as e:
        print(f"Get Projects Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve projects: {str(e)}")

@router.get("/{project_id}")
async def get_single_project(project_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific project by ID for the current user's organization"""
    try:
        project = await db.projects.find_one({"id": project_id, "organization": current_user.organization})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or you do not have access")
        if "_id" in project:
            del project["_id"]
        return project
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get Project Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve project: {str(e)}")


@router.put("/{project_id}") # Changed endpoint from /update to just /
async def update_project(
    project_id: str,
    update_data: ProjectUpdate, # Use ProjectUpdate Pydantic model for input validation
    current_user: User = Depends(get_current_user)
):
    """Update project details"""
    try:
        existing_project = await db.projects.find_one({"id": project_id, "owner_id": current_user.id}) # Filter by owner_id
        if not existing_project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or you are not the owner")

        update_dict = update_data.model_dump(exclude_unset=True) # Use model_dump for Pydantic v2
        
        # Handle datetime fields if they are passed as strings (e.g., fromisoformat)
        if "estimated_end_date" in update_dict and update_dict["estimated_end_date"]:
            if isinstance(update_dict["estimated_end_date"], str):
                try:
                    update_dict["estimated_end_date"] = datetime.fromisoformat(update_dict["estimated_end_date"])
                except ValueError:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format for estimated_end_date")
        
        update_dict["updated_at"] = datetime.utcnow()
        update_dict["last_update"] = datetime.utcnow() # Also update last_update

        result = await db.projects.update_one(
            {"id": project_id, "owner_id": current_user.id},
            {"$set": update_dict}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or no changes made")
        
        # Recalculate overall project progress and phase progress if tasks/deliverables were modified
        updated_project_doc = await db.projects.find_one({"id": project_id})
        if updated_project_doc:
            updated_project_doc["progress_percentage"] = calculate_project_progress(updated_project_doc)
            for phase_key in IMPACT_PHASES.keys():
                updated_project_doc["phase_progress"][phase_key] = calculate_phase_progress(updated_project_doc, phase_key)
            
            await db.projects.update_one(
                {"id": project_id},
                {"$set": {
                    "progress_percentage": updated_project_doc["progress_percentage"],
                    "phase_progress": updated_project_doc["phase_progress"],
                    "updated_at": datetime.utcnow()
                }}
            )
            if "_id" in updated_project_doc:
                del updated_project_doc["_id"]
            return Project(**updated_project_doc) # Return the updated project model
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Updated project not found after update operation.")


    except HTTPException:
        raise
    except Exception as e:
        print(f"Update Project Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update project: {str(e)}")


@router.put("/{project_id}/phase")
async def transition_project_phase_endpoint( # Renamed from original to avoid conflict if needed
    project_id: str,
    transition: PhaseTransition,
    current_user: User = Depends(get_current_user)
):
    """Transition project to the next phase"""
    try:
        project = await db.projects.find_one({"id": project_id, "owner_id": current_user.id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or you are not the owner")

        current_phase_order = IMPACT_PHASES.get(transition.from_phase, {}).get("order", 0)
        next_phase_order = IMPACT_PHASES.get(transition.to_phase, {}).get("order", 0)

        if next_phase_order != current_phase_order + 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid phase transition - phases must be completed sequentially")

        # Validate current phase completion for transition
        current_phase_in_project = next((p for p in project.get("phases", []) if p["phase_name"] == transition.from_phase), None)
        if not current_phase_in_project or current_phase_in_project.get("completion_percentage", 0) < 80:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Current phase ({transition.from_phase}) is not sufficiently complete (min 80% required for transition).")

        # Update project's current phase
        update_fields = {
            "current_phase": transition.to_phase,
            "updated_at": datetime.utcnow(),
            "last_update": datetime.utcnow()
        }

        # Update the 'status' and 'completion_date' of the 'from_phase' in the 'phases' array
        # And set 'start_date' for the 'to_phase' if not already set
        phases_list = project.get("phases", [])
        for p_idx, p in enumerate(phases_list):
            if p["phase_name"] == transition.from_phase:
                phases_list[p_idx]["status"] = "completed"
                phases_list[p_idx]["completion_date"] = transition.transition_date # Use provided transition date
                phases_list[p_idx]["success_status"] = "successful" # Assuming successful completion for transition
                phases_list[p_idx]["lessons_learned"] = transition.lessons_learned
                phases_list[p_idx]["recommendations"] = [] # Clear or add specific recommendations based on phase completion
                # Update main project's phase_end_dates
                update_fields[f"phase_end_dates.{transition.from_phase}"] = transition.transition_date

            if p["phase_name"] == transition.to_phase:
                phases_list[p_idx]["status"] = "in_progress"
                if not phases_list[p_idx].get("start_date"):
                    phases_list[p_idx]["start_date"] = transition.transition_date # Set start date for new phase
                    # Update main project's phase_start_dates
                    update_fields[f"phase_start_dates.{transition.to_phase}"] = transition.transition_date

        update_fields["phases"] = phases_list

        await db.projects.update_one(
            {"id": project_id},
            {"$set": update_fields}
        )

        # Generate tasks and deliverables for new phase if not already exists (check Project document's tasks/deliverables)
        # We need to query the project again to get its current state including tasks/deliverables
        updated_project_after_phase_update = await db.projects.find_one({"id": project_id})
        
        existing_phase_tasks = [
            t for t in updated_project_after_phase_update.get("tasks", []) if t.get("phase") == transition.to_phase
        ]
        if not existing_phase_tasks: # Only generate if tasks for this phase don't exist
            new_tasks_raw = generate_comprehensive_tasks_for_phase(transition.to_phase, project_id)
            new_deliverables_raw = generate_deliverables_for_phase(transition.to_phase, project_id)
            new_milestones_raw = generate_milestones_for_phase(transition.to_phase, project_id, transition.transition_date) # Use transition date as start date for milestones

            # Convert raw dicts to Pydantic models for proper nesting
            new_tasks = [Task(**t) for t in new_tasks_raw]
            new_deliverables = [Deliverable(**d) for d in new_deliverables_raw]
            new_milestones = [Milestone(**m) for m in new_milestones_raw]


            await db.projects.update_one(
                {"id": project_id},
                {
                    "$push": {
                        "tasks": {"$each": [t.model_dump() for t in new_tasks]}, # Use model_dump
                        "deliverables": {"$each": [d.model_dump() for d in new_deliverables]}, # Use model_dump
                        "milestones": {"$each": [m.model_dump() for m in new_milestones]} # Use model_dump
                    }
                }
            )

        # Log phase transition
        transition_log = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "from_phase": transition.from_phase,
            "to_phase": transition.to_phase,
            "transition_date": transition.transition_date,
            "completion_notes": transition.completion_notes,
            "lessons_learned": transition.lessons_learned,
            "user_id": current_user.id,
            "created_at": datetime.utcnow()
        }
        await db.phase_transitions.insert_one(transition_log) # Assuming a new collection for phase_transitions

        # Re-fetch project to return the most up-to-date state
        updated_project = await db.projects.find_one({"id": project_id, "owner_id": current_user.id})
        if updated_project and "_id" in updated_project:
            del updated_project["_id"]
        return {"message": f"Project successfully transitioned from {transition.from_phase} to {transition.to_phase} phase", "project": updated_project}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Phase transition failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Phase transition failed: {str(e)}")


@router.put("/{project_id}/tasks/{task_id}")
async def update_task_endpoint( # Renamed to avoid conflict if needed
    project_id: str,
    task_id: str,
    task_update: Dict[str, Any], # Use Dict[str, Any] for partial updates
    current_user: User = Depends(get_current_user)
):
    """Update task details within a project"""
    try:
        # Fetch the project first to ensure user ownership/access
        project = await db.projects.find_one({"id": project_id, "owner_id": current_user.id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or you are not the owner")

        # Find the task within the project's tasks list
        task_found = False
        updated_tasks = []
        for task_doc in project.get("tasks", []):
            if task_doc.get("id") == task_id:
                # Apply updates from task_update
                task_doc.update(task_update)
                if task_update.get("status") == "completed":
                    task_doc["completed_date"] = datetime.utcnow()
                task_found = True
            updated_tasks.append(task_doc)

        if not task_found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found in project")

        # Update the tasks array in the database
        await db.projects.update_one(
            {"id": project_id, "owner_id": current_user.id},
            {"$set": {
                "tasks": updated_tasks,
                "updated_at": datetime.utcnow(),
                "last_update": datetime.utcnow()
            }}
        )

        # Recalculate project and phase progress after task update
        updated_project_doc = await db.projects.find_one({"id": project_id})
        if updated_project_doc:
            new_overall_progress = calculate_project_progress(updated_project_doc)
            new_phase_progress = {
                phase_key: calculate_phase_progress(updated_project_doc, phase_key)
                for phase_key in IMPACT_PHASES.keys()
            }
            await db.projects.update_one(
                {"id": project_id},
                {"$set": {
                    "progress_percentage": new_overall_progress,
                    "phase_progress": new_phase_progress,
                    "updated_at": datetime.utcnow(),
                    "last_update": datetime.utcnow()
                }}
            )
        
        return {"message": "Task updated successfully", "task_id": task_id}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Task update failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Task update failed: {str(e)}")


@router.put("/{project_id}/deliverables/{deliverable_id}")
async def update_deliverable_endpoint( # Renamed to avoid conflict if needed
    project_id: str,
    deliverable_id: str,
    deliverable_update: Dict[str, Any], # Use Dict[str, Any] for partial updates
    current_user: User = Depends(get_current_user)
):
    """Update deliverable details within a project"""
    try:
        project = await db.projects.find_one({"id": project_id, "owner_id": current_user.id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or you are not the owner")

        deliverable_found = False
        updated_deliverables = []
        for deliv_doc in project.get("deliverables", []):
            if deliv_doc.get("id") == deliverable_id:
                deliv_doc.update(deliverable_update)
                if deliv_doc.get("status") in ["completed", "approved"]:
                    deliv_doc["completed_date"] = datetime.utcnow()
                deliverable_found = True
            updated_deliverables.append(deliv_doc)

        if not deliverable_found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deliverable not found in project")

        await db.projects.update_one(
            {"id": project_id, "owner_id": current_user.id},
            {"$set": {
                "deliverables": updated_deliverables,
                "updated_at": datetime.utcnow(),
                "last_update": datetime.utcnow()
            }}
        )

        # Recalculate project and phase progress after deliverable update
        updated_project_doc = await db.projects.find_one({"id": project_id})
        if updated_project_doc:
            new_overall_progress = calculate_project_progress(updated_project_doc)
            new_phase_progress = {
                phase_key: calculate_phase_progress(updated_project_doc, phase_key)
                for phase_key in IMPACT_PHASES.keys()
            }
            await db.projects.update_one(
                {"id": project_id},
                {"$set": {
                    "progress_percentage": new_overall_progress,
                    "phase_progress": new_phase_progress,
                    "updated_at": datetime.utcnow(),
                    "last_update": datetime.utcnow()
                }}
            )
        return {"message": "Deliverable updated successfully", "deliverable_id": deliverable_id}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Deliverable update failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Deliverable update failed: {str(e)}")


@router.post("/{project_id}/gate-review", status_code=status.HTTP_201_CREATED)
async def create_gate_review_endpoint( # Renamed to avoid conflict if needed
    project_id: str,
    gate_review_data: PhaseGateReview, # Use Pydantic model for input validation
    current_user: User = Depends(get_current_user)
):
    """Create a new phase gate review for a project"""
    try:
        project = await db.projects.find_one({"id": project_id, "owner_id": current_user.id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or you are not the owner")

        gate_review_data.id = str(uuid.uuid4())
        gate_review_data.project_id = project_id
        gate_review_data.reviewer_id = current_user.id
        gate_review_data.review_date = datetime.utcnow()

        gate_review_data.completion_percentage = calculate_phase_progress(project, gate_review_data.phase)
        
        await db.projects.update_one(
            {"id": project_id},
            {
                "$push": {"gate_reviews": gate_review_data.model_dump()}, # Use model_dump
                "$set": {"updated_at": datetime.utcnow(), "last_update": datetime.utcnow()}
            }
        )
        
        return gate_review_data

    except HTTPException:
        raise
    except Exception as e:
        print(f"Gate review creation failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Gate review creation failed: {str(e)}")


@router.post("/{project_id}/risk-monitoring")
async def generate_real_time_risk_monitoring_endpoint( # Renamed to avoid conflict if needed
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate real-time risk monitoring dashboard for active projects"""
    try:
        project = await db.projects.find_one({"id": project_id, "owner_id": current_user.id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or you are not the owner")

        assessment_id = project.get("assessment_id")
        assessment_data = {}
        if assessment_id:
            assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id}) # Filter by user_id
            if assessment:
                assessment_data = {
                    "leadership_support": assessment.get("leadership_support", {}).get("score", 3),
                    "resource_availability": assessment.get("resource_availability", {}).get("score", 3),
                    "change_management_maturity": assessment.get("change_management_maturity", {}).get("score", 3),
                    "communication_effectiveness": assessment.get("communication_effectiveness", {}).get("score", 3),
                    "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3),
                    "technical_readiness": assessment.get("technical_readiness", {}).get("score", 3) # Added for risk trending
                }
        
        # Calculate current project metrics
        overall_progress = calculate_project_progress(project)
        spent_budget = project.get("spent_budget", 0)
        total_budget = project.get("budget", 0) # Use 'budget' field from Project schema
        budget_utilization = (spent_budget / total_budget * 100) if total_budget > 0 else 0

        # Generate risk alerts (this logic might be extracted to a service if complex)
        risk_alerts = []
        if budget_utilization > 80:
            risk_alerts.append({
                "type": "Budget",
                "severity": "High",
                "message": f"Budget utilization at {budget_utilization:.1f}% - immediate attention required",
                "recommended_action": "Review remaining activities and implement cost controls"
            })
        elif budget_utilization > 60:
            risk_alerts.append({
                "type": "Budget",
                "severity": "Medium",
                "message": f"Budget utilization at {budget_utilization:.1f}% - monitor closely",
                "recommended_action": "Review upcoming expenses and optimize resource allocation"
            })
        if overall_progress < 60 and budget_utilization > 70:
            risk_alerts.append({
                "type": "Schedule",
                "severity": "High",
                "message": "Project behind schedule with high budget utilization",
                "recommended_action": "Accelerate critical path activities and review scope"
            })
        
        # Generate trending analysis from predictive_analytics service
        # Requires overall_score from assessment, assuming it can be derived or passed
        overall_assessment_score = assessment.get("overall_score", 3.0) if assessment else 3.0
        risk_trending_data = generate_predictive_risk_trending(assessment_data, overall_assessment_score)

        risk_monitoring_result = {
            "project_id": project_id,
            "project_name": project.get("name", ""), # Use 'name' from Project schema
            "current_status": {
                "overall_progress": round(overall_progress, 1),
                "current_week": min(10, max(1, int(overall_progress / 10) + 1)), # Simplified current week calculation
                "budget_utilization": round(budget_utilization, 1),
                "health_status": project.get("health_status", "green")
            },
            "risk_alerts": risk_alerts,
            "trend_analysis": {
                "budget_trend": "On Track" if budget_utilization <= overall_progress else "Over Budget",
                "schedule_trend": "On Track" if overall_progress >= (min(10, max(1, int(overall_progress / 10) + 1)) * 10) else "Behind Schedule",
                "scope_trend": "Stable" if len(risk_alerts) == 0 else "At Risk",
                "predictive_trending_data": risk_trending_data # Include full trending data
            },
            "predictive_insights": {
                "completion_probability": risk_trending_data["project_outlook"]["success_probability"] if "project_outlook" in risk_trending_data else min(95, max(30, 100 - len(risk_alerts) * 20)),
                "budget_overrun_risk": risk_trending_data["budget_risk_analysis"]["risk_level"] if "budget_risk_analysis" in risk_trending_data else "Low" if budget_utilization < 80 else "High",
                "timeline_risk": risk_trending_data["timeline_optimization"]["timeline_outlook"] if "timeline_optimization" in risk_trending_data else "Low" if overall_progress >= (min(10, max(1, int(overall_progress / 10) + 1)) * 8) else "High"
            },
            "recommendations": generate_real_time_recommendations(risk_alerts, overall_progress, budget_utilization), # Helper from predictive_analytics or common_utils
            "generated_at": datetime.utcnow()
        }
        
        return risk_monitoring_result

    except HTTPException:
        raise
    except Exception as e:
        print(f"Risk Monitoring Generation Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate risk monitoring: {str(e)}")


# Helper for risk monitoring endpoint
def generate_real_time_recommendations(risk_alerts: List[dict], progress: float, budget_utilization: float) -> List[str]:
    """Generate real-time recommendations for project management"""
    recommendations = []
    if len(risk_alerts) > 2:
        recommendations.append("Implement immediate risk mitigation measures")
    if budget_utilization > progress + 10:
        recommendations.append("Review and optimize resource allocation")
    if progress < 50:
        recommendations.append("Accelerate critical path activities")
    return recommendations


@router.post("/{project_id}/detailed-budget-tracking")
async def generate_detailed_budget_tracking_endpoint(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate detailed task-level and phase-level budget tracking"""
    try:
        project = await db.projects.find_one({"id": project_id, "owner_id": current_user.id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or you are not the owner")

        assessment_id = project.get("assessment_id")
        assessment_data = {}
        implementation_plan = {}

        if assessment_id:
            assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
            if assessment:
                assessment_data = {
                    "leadership_support": assessment.get("leadership_support", {}).get("score", 3),
                    "resource_availability": assessment.get("resource_availability", {}).get("score", 3),
                    "change_management_maturity": assessment.get("change_management_maturity", {}).get("score", 3),
                    "communication_effectiveness": assessment.get("communication_effectiveness", {}).get("score", 3),
                    "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3),
                    "technical_readiness": assessment.get("technical_readiness", {}).get("score", 3),
                    "stakeholder_engagement": assessment.get("stakeholder_engagement", {}).get("score", 3)
                }

                # Generate implementation plan for budget tracking using readiness_engine service
                overall_score = assessment.get("overall_score", 3.0)
                assessment_type = assessment.get("assessment_type", "general_readiness")
                implementation_plan = generate_implementation_plan(assessment_data, assessment_type, overall_score)

        # Generate detailed budget tracking using budget_tracking service
        budget_tracking_result = generate_detailed_budget_tracking(project, assessment_data, implementation_plan)

        return budget_tracking_result

    except HTTPException:
        raise
    except Exception as e:
        print(f"Detailed Budget Tracking Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate detailed budget tracking: {str(e)}")


@router.post("/{project_id}/advanced-forecasting")
async def generate_advanced_project_forecasting_endpoint(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate advanced project outcome forecasting"""
    try:
        project = await db.projects.find_one({"id": project_id, "owner_id": current_user.id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or you are not the owner")

        assessment_id = project.get("assessment_id")
        assessment_data = {}
        predictive_analytics_mock = {} # Predictive analytics from a previous call (simulate or fetch)
        budget_tracking_mock = {} # Budget tracking from a previous call (simulate or fetch)


        if assessment_id:
            assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
            if assessment:
                assessment_data = {
                    "overall_score": assessment.get("overall_score", 3.0),
                    "leadership_support": assessment.get("leadership_support", {}).get("score", 3),
                    "resource_availability": assessment.get("resource_availability", {}).get("score", 3),
                    "change_management_maturity": assessment.get("change_management_maturity", {}).get("score", 3),
                    "communication_effectiveness": assessment.get("communication_effectiveness", {}).get("score", 3),
                    "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3),
                    "technical_readiness": assessment.get("technical_readiness", {}).get("score", 3),
                    "stakeholder_engagement": assessment.get("stakeholder_engagement", {}).get("score", 3),
                    "maintenance_operations_alignment": assessment.get("maintenance_operations_alignment", {}).get("score", 3)
                }
                
                # Simulate predictive analytics data needed for forecasting
                overall_score_for_pred = assessment.get("overall_score", 3.0)
                assessment_type_for_pred = assessment.get("assessment_type", "general_readiness")

                # Simplified prediction generation for forecasting
                # In a real app, you might fetch previously generated predictive analytics
                task_predictions_mock = []
                for task_num in range(1, 11):
                    task_id = f"task_{task_num}"
                    prediction = predict_task_success_probability(task_id, assessment_data, overall_score_for_pred)
                    task_predictions_mock.append(prediction)

                total_budget_for_pred = assessment.get("implementation_plan", {}).get("summary", {}).get("total_budget", 90000)
                budget_risk_mock = predict_budget_overrun_risk(assessment_data, overall_score_for_pred, total_budget_for_pred)
                scope_creep_risk_mock = predict_scope_creep_risk(assessment_data, assessment_type_for_pred)
                timeline_optimization_mock = predict_timeline_optimization(assessment_data, overall_score_for_pred)
                risk_trending_mock = generate_predictive_risk_trending(assessment_data, overall_score_for_pred)


                predictive_analytics_mock = {
                    "project_outlook": {
                        "success_probability": round(min(95, max(15, overall_score_for_pred * 18)), 1)
                    },
                    "budget_risk_analysis": budget_risk_mock,
                    "scope_creep_analysis": scope_creep_risk_mock,
                    "timeline_optimization": timeline_optimization_mock,
                    "risk_trending": risk_trending_mock
                }
                
                # Simulate budget tracking data needed for forecasting
                implementation_plan_for_budget = generate_implementation_plan(assessment_data, assessment_type_for_pred, overall_score_for_pred)
                budget_tracking_mock = generate_detailed_budget_tracking(project, assessment_data, implementation_plan_for_budget)


        # Generate advanced forecasting using project_forecasting service
        forecasting_result = generate_advanced_project_forecasting(project, assessment_data, predictive_analytics_mock, budget_tracking_mock)

        return forecasting_result

    except HTTPException:
        raise
    except Exception as e:
        print(f"Advanced Forecasting Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate advanced forecasting: {str(e)}")


@router.post("/{project_id}/stakeholder-communications")
async def generate_stakeholder_communications_endpoint(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate automated stakeholder communication content"""
    try:
        project = await db.projects.find_one({"id": project_id, "owner_id": current_user.id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or you are not the owner")

        assessment_id = project.get("assessment_id")
        assessment_data = {}
        budget_tracking_mock = {}
        project_forecasting_mock = {}

        if assessment_id:
            assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
            if assessment:
                assessment_data = {
                    "overall_score": assessment.get("overall_score", 3.0),
                    "leadership_support": assessment.get("leadership_support", {}).get("score", 3),
                    "resource_availability": assessment.get("resource_availability", {}).get("score", 3),
                    "change_management_maturity": assessment.get("change_management_maturity", {}).get("score", 3),
                    "communication_effectiveness": assessment.get("communication_effectiveness", {}).get("score", 3),
                    "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3),
                    "technical_readiness": assessment.get("technical_readiness", {}).get("score", 3),
                    "stakeholder_engagement": assessment.get("stakeholder_engagement", {}).get("score", 3)
                }

                # Generate supporting data that generate_stakeholder_communications expects
                overall_score_for_comms = assessment.get("overall_score", 3.0)
                assessment_type_for_comms = assessment.get("assessment_type", "general_readiness")

                implementation_plan_for_comms = generate_implementation_plan(assessment_data, assessment_type_for_comms, overall_score_for_comms)
                budget_tracking_mock = generate_detailed_budget_tracking(project, assessment_data, implementation_plan_for_comms)

                predictive_analytics_mock_for_comms = {
                    "project_outlook": {
                        "success_probability": min(95, max(15, overall_score_for_comms * 18))
                    }
                }
                project_forecasting_mock = generate_advanced_project_forecasting(project, assessment_data, predictive_analytics_mock_for_comms, budget_tracking_mock)

        # Generate stakeholder communications using project_forecasting service
        communications_result = generate_stakeholder_communications(project, budget_tracking_mock, project_forecasting_mock, assessment_data)

        return communications_result

    except HTTPException:
        raise
    except Exception as e:
        print(f"Stakeholder Communications Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate stakeholder communications: {str(e)}")


@router.post("/{project_id}/manufacturing-excellence-tracking")
async def generate_manufacturing_excellence_tracking_endpoint( # Renamed to avoid conflict if needed
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate manufacturing excellence correlation tracking"""
    try:
        project = await db.projects.find_one({"id": project_id, "owner_id": current_user.id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or you are not the owner")

        assessment_id = project.get("assessment_id")
        assessment_data = {}

        if assessment_id:
            assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
            if assessment:
                assessment_data = {
                    "maintenance_operations_alignment": assessment.get("maintenance_operations_alignment", {}).get("score", 3),
                    "technical_readiness": assessment.get("technical_readiness", {}).get("score", 3),
                    "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3),
                    "safety_compliance": assessment.get("safety_compliance", {}).get("score", 3),
                    "shift_work_considerations": assessment.get("shift_work_considerations", {}).get("score", 3)
                }
        
        # Call the manufacturing excellence correlation function from project_forecasting service
        # It expects an outcomes dictionary, which would come from advanced forecasting
        # For this specific endpoint, we might mock or derive simple outcomes if not full forecasting is run
        mock_outcomes = {
            "quality_achievement_probability": 80, # Example mock value
            "scope_completion_probability": 90 # Example mock value
        }
        
        excellence_tracking_result = calculate_manufacturing_excellence_correlation(assessment_data, mock_outcomes)

        # Manufacturing performance predictions
        maintenance_excellence_score = assessment_data.get("maintenance_operations_alignment", 3.0)
        operational_efficiency_potential = (
            assessment_data.get("technical_readiness", 3.0) +
            assessment_data.get("workforce_adaptability", 3.0) +
            assessment_data.get("safety_compliance", 3.0)
        ) / 3

        performance_improvements = {
            "unplanned_downtime_reduction": min(60, max(10, maintenance_excellence_score * 12)),
            "overall_equipment_effectiveness": min(35, max(5, maintenance_excellence_score * 7)),
            "maintenance_cost_reduction": min(30, max(5, maintenance_excellence_score * 6)),
            "safety_performance_improvement": min(25, max(5, assessment_data.get("safety_compliance", 3.0) * 5)),
            "operational_efficiency_gain": min(40, max(5, operational_efficiency_potential * 8))
        }

        # ROI calculations
        estimated_annual_savings = sum(performance_improvements.values()) * 1000  # Simplified
        implementation_cost = project.get("budget", 90000) # Use 'budget' from Project
        roi_percentage = ((estimated_annual_savings - implementation_cost) / implementation_cost * 100) if implementation_cost > 0 else 0

        # Constructing the full response as per original server.py
        full_excellence_tracking_response = {
            "project_id": project_id,
            "project_name": project.get("name", ""),
            "maintenance_excellence": {
                "current_score": round(maintenance_excellence_score, 1),
                "potential_score": min(5.0, maintenance_excellence_score + 1.5),
                "improvement_pathway": excellence_tracking_result.get("excellence_pathway", []),
                "critical_success_factors": [
                    "Maintenance-operations alignment",
                    "Technical readiness and adoption",
                    "Workforce adaptability and training",
                    "Safety and compliance integration"
                ]
            },
            "performance_predictions": {
                "unplanned_downtime_reduction": f"{performance_improvements['unplanned_downtime_reduction']:.1f}%",
                "oee_improvement": f"{performance_improvements['overall_equipment_effectiveness']:.1f}%",
                "maintenance_cost_reduction": f"{performance_improvements['maintenance_cost_reduction']:.1f}%",
                "safety_improvement": f"{performance_improvements['safety_performance_improvement']:.1f}%",
                "operational_efficiency": f"{performance_improvements['operational_efficiency_gain']:.1f}%"
            },
            "roi_analysis": {
                "estimated_annual_savings": round(estimated_annual_savings, 0),
                "implementation_investment": implementation_cost,
                "roi_percentage": round(roi_percentage, 1),
                "payback_period_months": max(6, min(36, 12 / (roi_percentage / 100))) if roi_percentage > 0 else 36,
                "business_case_strength": "Strong" if roi_percentage > 50 else "Moderate" if roi_percentage > 20 else "Developing"
            },
            "correlation_metrics": {
                "maintenance_operations_correlation": excellence_tracking_result.get("correlation_strength", 0.0), # Re-using calculated correlation
                "technology_adoption_correlation": round(assessment_data.get("technical_readiness", 3.0) / 5.0, 2),
                "workforce_readiness_correlation": round(assessment_data.get("workforce_adaptability", 3.0) / 5.0, 2)
            },
            "manufacturing_kpis": {
                "equipment_reliability": f"{60 + maintenance_excellence_score * 8:.1f}%",
                "planned_maintenance_ratio": f"{40 + maintenance_excellence_score * 12:.1f}%",
                "mean_time_to_repair": f"{24 - maintenance_excellence_score * 4:.1f} hours",
                "maintenance_productivity": f"{70 + operational_efficiency_potential * 6:.1f}%"
            },
            "generated_at": datetime.utcnow()
        }

        return full_excellence_tracking_response

    except HTTPException:
        raise
    except Exception as e:
        print(f"Manufacturing Excellence Tracking Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate manufacturing excellence tracking: {str(e)}")


@router.post("/{project_id}/phases/{phase_name}/intelligence")
async def generate_phase_intelligence_endpoint( # Renamed to avoid conflict if needed
    project_id: str,
    phase_name: str,
    current_user: User = Depends(get_current_user)
):
    """Generate phase-based intelligence and recommendations"""
    try:
        project = await db.projects.find_one({"id": project_id, "owner_id": current_user.id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or you are not the owner")

        assessment_data = {}
        assessment_id = project.get("assessment_id")
        if assessment_id:
            assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
            if assessment:
                assessment_data = {
                    "overall_score": assessment.get("overall_score", 3.0),
                    "leadership_support": assessment.get("leadership_support", {}).get("score", 3),
                    "resource_availability": assessment.get("resource_availability", {}).get("score", 3),
                    "change_management_maturity": assessment.get("change_management_maturity", {}).get("score", 3),
                    "communication_effectiveness": assessment.get("communication_effectiveness", {}).get("score", 3),
                    "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3),
                    "technical_readiness": assessment.get("technical_readiness", {}).get("score", 3),
                    "stakeholder_engagement": assessment.get("stakeholder_engagement", {}).get("score", 3)
                }

        # Get completed phases for lessons learned from the project's phases array
        completed_phases = [p for p in project.get("phases", []) if p.get("status") == "completed"]
        
        # Generate phase-based intelligence using workflow_management service
        phase_intelligence_result = generate_phase_based_intelligence(phase_name, assessment_data, project, completed_phases)

        return phase_intelligence_result

    except HTTPException:
        raise
    except Exception as e:
        print(f"Phase Intelligence Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate phase intelligence: {str(e)}")


@router.put("/{project_id}/phases/{phase_name}/progress")
async def update_phase_progress_endpoint( # Renamed to avoid conflict if needed
    project_id: str,
    phase_name: str,
    progress_data: PhaseProgressUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update progress for a specific phase"""
    try:
        project = await db.projects.find_one({"id": project_id, "owner_id": current_user.id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or you are not the owner")

        phases = project.get("phases", [])
        phase_found = False

        for i, phase in enumerate(phases):
            if phase.get("phase_name") == phase_name:
                # Update phase with new progress data
                phases[i].update(progress_data.model_dump(exclude_unset=True)) # Use model_dump
                phases[i]["updated_at"] = datetime.utcnow()

                if progress_data.status == "completed":
                    phases[i]["completion_date"] = datetime.utcnow()
                
                phase_found = True
                break

        if not phase_found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phase not found in project")

        # Update project in database
        result = await db.projects.update_one(
            {"id": project_id, "owner_id": current_user.id},
            {"$set": {"phases": phases, "updated_at": datetime.utcnow(), "last_update": datetime.utcnow()}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update phase progress in DB or no changes made")

        # Recalculate overall project progress and phase progress
        updated_project_doc = await db.projects.find_one({"id": project_id})
        if updated_project_doc:
            new_overall_progress = calculate_project_progress(updated_project_doc)
            new_phase_progress = {
                p["phase_name"]: calculate_phase_progress(updated_project_doc, p["phase_name"])
                for p in updated_project_doc.get("phases", [])
            }
            await db.projects.update_one(
                {"id": project_id},
                {"$set": {
                    "progress_percentage": new_overall_progress,
                    "phase_progress": new_phase_progress,
                    "updated_at": datetime.utcnow(),
                    "last_update": datetime.utcnow()
                }}
            )

            updated_project_doc["_id"] = str(updated_project_doc.get("_id"))
            return Project(**updated_project_doc)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Updated project not found after update operation.")


    except HTTPException:
        raise
    except Exception as e:
        print(f"Phase Progress Update Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update phase progress: {str(e)}")


@router.post("/{project_id}/phases/{phase_name}/complete", status_code=status.HTTP_200_OK)
async def complete_phase_with_analysis_endpoint( # Renamed to avoid conflict if needed
    project_id: str,
    phase_name: str,
    completion_data: PhaseProgressUpdate,
    current_user: User = Depends(get_current_user)
):
    """Complete a phase and generate comprehensive analysis"""
    try:
        # First, update the phase progress (using the existing endpoint's logic or a direct service call)
        # For simplicity, we'll re-implement the necessary update part here for direct service call
        # In a very large app, you might refactor update_phase_progress_endpoint itself to call a service function
        project = await db.projects.find_one({"id": project_id, "owner_id": current_user.id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or you are not the owner")

        phases = project.get("phases", [])
        completed_phase_in_project_list = None
        for i, phase in enumerate(phases):
            if phase.get("phase_name") == phase_name:
                phases[i].update(completion_data.model_dump(exclude_unset=True))
                phases[i]["updated_at"] = datetime.utcnow()
                if completion_data.status == "completed":
                    phases[i]["completion_date"] = datetime.utcnow()
                completed_phase_in_project_list = phases[i] # Keep reference to the updated phase dict
                break
        
        if not completed_phase_in_project_list:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phase not found in project or already completed")

        # Update project phases array in DB first
        await db.projects.update_one(
            {"id": project_id, "owner_id": current_user.id},
            {"$set": {"phases": phases, "updated_at": datetime.utcnow(), "last_update": datetime.utcnow()}}
        )

        # Get updated project document for the analysis
        updated_project_doc = await db.projects.find_one({"id": project_id})
        if not updated_project_doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found after phase update for analysis.")

        assessment_data = {}
        assessment_id = updated_project_doc.get("assessment_id")
        if assessment_id:
            assessment = await db.assessments.find_one({"id": assessment_id, "user_id": current_user.id})
            if assessment:
                assessment_data = {
                    "overall_score": assessment.get("overall_score", 3.0),
                    "leadership_support": assessment.get("leadership_support", {}).get("score", 3),
                    "resource_availability": assessment.get("resource_availability", {}).get("score", 3),
                    "change_management_maturity": assessment.get("change_management_maturity", {}).get("score", 3),
                    "communication_effectiveness": assessment.get("communication_effectiveness", {}).get("score", 3),
                    "workforce_adaptability": assessment.get("workforce_adaptability", {}).get("score", 3),
                    "technical_readiness": assessment.get("technical_readiness", {}).get("score", 3),
                    "stakeholder_engagement": assessment.get("stakeholder_engagement", {}).get("score", 3)
                }
        
        # Generate comprehensive completion analysis using workflow_management service
        completion_analysis_result = generate_phase_completion_analysis(completed_phase_in_project_list, assessment_data, updated_project_doc)

        # Update the phase with analysis results within the project document
        for i, phase in enumerate(phases):
            if phase.get("phase_name") == phase_name:
                phases[i]["completion_analysis"] = completion_analysis_result
                phases[i]["analysis_generated_at"] = datetime.utcnow()
                break
        
        await db.projects.update_one(
            {"id": project_id, "owner_id": current_user.id},
            {"$set": {"phases": phases, "updated_at": datetime.utcnow(), "last_update": datetime.utcnow()}}
        )

        # Recalculate overall project progress and phase progress after analysis update
        # This part is similar to update_phase_progress_endpoint
        new_overall_progress = calculate_project_progress(updated_project_doc)
        new_phase_progress = {
            p["phase_name"]: calculate_phase_progress(updated_project_doc, p["phase_name"])
            for p in updated_project_doc.get("phases", [])
        }
        await db.projects.update_one(
            {"id": project_id},
            {"$set": {
                "progress_percentage": new_overall_progress,
                "phase_progress": new_phase_progress,
                "updated_at": datetime.utcnow(),
                "last_update": datetime.utcnow()
            }}
        )

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
        print(f"Phase Completion Analysis Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to complete phase with analysis: {str(e)}")


@router.get("/{project_id}/workflow-status")
async def get_project_workflow_status_endpoint( # Renamed to avoid conflict if needed
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive workflow status for a project"""
    try:
        project = await db.projects.find_one({"id": project_id, "owner_id": current_user.id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or you are not the owner")

        phases = project.get("phases", [])
        
        phase_summary = {
            "total_phases": len(phases),
            "completed_phases": len([p for p in phases if p.get("status") == "completed"]),
            "in_progress_phases": len([p for p in phases if p.get("status") == "in_progress"]),
            "not_started_phases": len([p for p in phases if p.get("status") == "not_started"]),
            "failed_phases": len([p for p in phases if p.get("status") == "failed"])
        }
        
        overall_progress = project.get("progress_percentage", 0.0) # Use the stored overall_progress

        total_budget_spent = sum(p.get("budget_spent", 0) for p in phases)
        total_budget = project.get("budget", 0) # Use 'budget' from Project schema
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
                "phases_detail": [p.model_dump() if isinstance(p, ProjectPhase) else p for p in phases] # Ensure phases are dicts
            },
            "generated_at": datetime.utcnow()
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Workflow Status Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get workflow status: {str(e)}")
