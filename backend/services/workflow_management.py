# backend/services/workflow_management.py

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status

from db.mongo import db
from schemas.project import ProjectPhase, PhaseTransition
from data.constants import IMPACT_PHASES, ASSESSMENT_TYPES

# NOTE: Imports the project retrieval service to avoid direct 'db' access here
# from services.admin_services import get_project_document 


# --- Existing Functions (User's definitions kept, assumed to contain core logic) ---

def generate_comprehensive_tasks_for_phase(phase_name: str, project_id: str) -> List[Dict]:
    """Generate a list of tasks for a given phase based on IMPACT_PHASES."""
    tasks = []
    phase_info = IMPACT_PHASES.get(phase_name, {})
    key_activities = phase_info.get("key_activities", [])

    for activity in key_activities:
        task_id = str(uuid.uuid4())
        tasks.append({
            "id": task_id,
            "project_id": project_id,
            "title": activity,
            "description": f"Complete the key activity: {activity}",
            "phase": phase_name,
            "category": "key_activity",
            "status": "pending"
        })
    return tasks

def generate_deliverables_for_phase(phase_name: str, project_id: str) -> List[Dict]:
    """Generate a list of deliverables for a given phase."""
    deliverables = []
    phase_info = IMPACT_PHASES.get(phase_name, {})
    phase_deliverables = phase_info.get("deliverables", [])

    for deliverable in phase_deliverables:
        deliverable_id = str(uuid.uuid4())
        deliverables.append({
            "id": deliverable_id,
            "project_id": project_id,
            "name": deliverable["name"],
            "type": deliverable["type"],
            "required": deliverable["required"],
            "status": "pending"
        })
    return deliverables

def generate_milestones_for_phase(phase_name: str, project_id: str, start_date: datetime) -> List[Dict]:
    """Generate milestones for a given phase."""
    milestones = []
    phase_info = IMPACT_PHASES.get(phase_name, {})
    milestone_id = str(uuid.uuid4())
    milestones.append({
        "id": milestone_id,
        "project_id": project_id,
        "title": f"Complete {phase_info.get('name', phase_name)} Phase",
        "description": f"All tasks and deliverables for the {phase_info.get('name', phase_name)} phase completed.",
        "phase": phase_name,
        "target_date": start_date + timedelta(weeks=(phase_info.get("order", 1) * 4))
    })
    return milestones

def generate_implementation_plan(assessment_data: dict, assessment_type: str, overall_score: float) -> dict:
    """Generate tailored week-by-week implementation plan based on assessment results"""
    return {"weeks": {}, "summary": {}} # Simplified return for brevity

def generate_phase_based_intelligence(phase_name: str, assessment_data: dict, project_data: dict, completed_phases: List[dict] = None) -> dict:
    """Generate intelligent recommendations for each IMPACT phase"""
    return {}

def calculate_project_progress(project_data: Dict) -> float:
    """Calculate overall project progress (Logic needs to be completed in implementation)"""
    tasks = project_data.get("tasks", [])
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.get("status") == "completed"])
    return round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0, 1)

def calculate_phase_progress(project_data: Dict, phase: str) -> float:
    """Calculate progress for a specific phase (Logic needs to be completed in implementation)"""
    tasks = project_data.get("tasks", [])
    phase_tasks = [t for t in tasks if t.get("phase") == phase]
    total_phase_tasks = len(phase_tasks)
    completed_phase_tasks = len([t for t in phase_tasks if t.get("status") == "completed"])
    return round((completed_phase_tasks / total_phase_tasks * 100) if total_phase_tasks > 0 else 0.0, 1)

def generate_phase_completion_analysis(phase_data: dict, assessment_data: dict, project_data: dict) -> dict:
    """Generate comprehensive analysis when a phase is completed (Logic needs to be completed in implementation)"""
    return {}

# --- NEW REFACTORED SERVICE FUNCTIONS ---

async def recalculate_and_save_progress(project_id: str, project_doc: Dict[str, Any]):
    """Calculates overall progress and all phase progress percentages and saves them to DB."""
    new_overall_progress = calculate_project_progress(project_doc)

    new_phase_progress = {}
    for phase_name in IMPACT_PHASES.keys():
        new_phase_progress[phase_name] = calculate_phase_progress(project_doc, phase_name)

    await db.projects.update_one(
        {"id": project_id},
        {"$set": {
            "progress_percentage": new_overall_progress,
            "phase_progress": new_phase_progress,
            "updated_at": datetime.utcnow(),
            "last_update": datetime.utcnow()
        }}
    )


async def update_project_task(project_id: str, task_id: str, updates: Dict[str, Any], user_id: str):
    """Updates a nested task array and triggers progress recalculation."""
    from services.admin_services import get_project_document # <-- ADD THIS LINE
    await get_project_document(project_id, user_id)
    
    # 1. Update the nested array using MongoDB positional operator (more efficient)
    update_set = {"updated_at": datetime.utcnow(), "last_update": datetime.utcnow()}
    
    for key, value in updates.items():
        update_set[f"tasks.$.{key}"] = value

    if updates.get("status") == "completed":
        update_set["tasks.$.completed_date"] = datetime.utcnow()

    result = await db.projects.update_one(
        {"id": project_id, "tasks.id": task_id},
        {"$set": update_set}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found in project or you are not the owner")

    # 2. Recalculate progress for the entire project
    updated_project_doc = await db.projects.find_one({"id": project_id})
    await recalculate_and_save_progress(project_id, updated_project_doc)


async def update_project_deliverable(project_id: str, deliverable_id: str, updates: Dict[str, Any], user_id: str):
    """Updates a nested deliverable array and triggers progress recalculation."""
    from services.admin_services import get_project_document # <-- ADD THIS LINE
    await get_project_document(project_id, user_id)
    
    # 1. Update the nested array using MongoDB positional operator
    update_set = {"updated_at": datetime.utcnow(), "last_update": datetime.utcnow()}
    
    for key, value in updates.items():
        update_set[f"deliverables.$.{key}"] = value

    if updates.get("status") in ["completed", "approved"]:
        update_set["deliverables.$.completed_date"] = datetime.utcnow()

    result = await db.projects.update_one(
        {"id": project_id, "deliverables.id": deliverable_id},
        {"$set": update_set}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deliverable not found in project or you are not the owner")

    # 2. Recalculate progress for the entire project
    updated_project_doc = await db.projects.find_one({"id": project_id})
    await recalculate_and_save_progress(project_id, updated_project_doc)

async def perform_phase_transition(project_id: str, transition: PhaseTransition, user_id: str) -> Dict[str, Any]:
    """Performs validation, updates the project document, and generates content for the next phase."""
    from services.admin_services import get_project_document # <-- ADD THIS LINE
    project = await get_project_document(project_id, user_id)
    
    # 1. Validation Logic
    current_phase_order = IMPACT_PHASES.get(transition.from_phase, {}).get("order", 0)
    next_phase_order = IMPACT_PHASES.get(transition.to_phase, {}).get("order", 0)

    if next_phase_order != current_phase_order + 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid phase transition - phases must be completed sequentially")

    current_phase_in_project = next((p for p in project.get("phases", []) if p["phase_name"] == transition.from_phase), None)
    if not current_phase_in_project or current_phase_in_project.get("completion_percentage", 0) < 80:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Current phase ({transition.from_phase}) is not sufficiently complete (min 80% required for transition).")

    # 2. Update Phases and Project Fields (Using MongoDB $set with positional arrays)
    # Update the old phase status
    await db.projects.update_one(
        {"id": project_id, "phases.phase_name": transition.from_phase},
        {"$set": {
            "phases.$.status": "completed",
            "phases.$.completion_date": transition.transition_date,
            "phases.$.success_status": "successful", 
            "phases.$.lessons_learned": transition.lessons_learned,
            "phase_end_dates": {transition.from_phase: transition.transition_date}
        }}
    )

    # Update the new phase status
    await db.projects.update_one(
        {"id": project_id, "phases.phase_name": transition.to_phase},
        {"$set": {
            "current_phase": transition.to_phase,
            "phases.$.status": "in_progress",
            "phases.$.start_date": transition.transition_date,
            "phase_start_dates": {transition.to_phase: transition.transition_date},
            "updated_at": datetime.utcnow(),
            "last_update": datetime.utcnow()
        }}
    )

    # 3. Generate New Content for Next Phase
    existing_phase_tasks = [t for t in project.get("tasks", []) if t.get("phase") == transition.to_phase]
    if not existing_phase_tasks:
        new_tasks_raw = generate_comprehensive_tasks_for_phase(transition.to_phase, project_id)
        new_deliverables_raw = generate_deliverables_for_phase(transition.to_phase, project_id)
        new_milestones_raw = generate_milestones_for_phase(transition.to_phase, project_id, transition.transition_date)
        
        await db.projects.update_one(
            {"id": project_id},
            {"$push": {"tasks": {"$each": new_tasks_raw}, "deliverables": {"$each": new_deliverables_raw}, "milestones": {"$each": new_milestones_raw}}}
        )
    
    # 4. Re-fetch project to return the most up-to-date state
    return await get_project_document(project_id, user_id)
