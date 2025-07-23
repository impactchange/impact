# backend/services/workflow_management.py
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from data.constants import IMPACT_PHASES, ASSESSMENT_TYPES

# --- Functions to generate project structure ---

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
    # This is a placeholder for more complex milestone generation logic
    # For now, creating one milestone per phase as an example
    phase_info = IMPACT_PHASES.get(phase_name, {})
    milestone_id = str(uuid.uuid4())
    milestones.append({
        "id": milestone_id,
        "project_id": project_id,
        "title": f"Complete {phase_info.get('name', phase_name)} Phase",
        "description": f"All tasks and deliverables for the {phase_info.get('name', phase_name)} phase completed.",
        "phase": phase_name,
        "target_date": start_date + timedelta(weeks=(phase_info.get("order", 1) * 4)) # Simplified target date
    })
    return milestones

def generate_implementation_plan(assessment_data: dict, assessment_type: str, overall_score: float) -> dict:
    """Generate tailored week-by-week implementation plan based on assessment results"""
    # This function was moved from readiness_engine to consolidate workflow logic
    base_weeks = {
        # ... (omitted for brevity - this is the large base_weeks dictionary)
    }
    # ... (omitted for brevity - the rest of the implementation plan logic)
    return {"weeks": {}, "summary": {}} # Simplified return for brevity

# --- Existing functions from your file ---

def generate_phase_based_intelligence(phase_name: str, assessment_data: dict, project_data: dict, completed_phases: List[dict] = None) -> dict:
    """Generate intelligent recommendations for each IMPACT phase"""
    # ... (rest of the function)
    return {}

def calculate_project_progress(project_data: Dict) -> float:
    """Calculate overall project progress"""
    # ... (rest of the function)
    return 0.0

def calculate_phase_progress(project_data: Dict, phase: str) -> float:
    """Calculate progress for a specific phase"""
    # ... (rest of the function)
    return 0.0

def generate_phase_completion_analysis(phase_data: dict, assessment_data: dict, project_data: dict) -> dict:
    """Generate comprehensive analysis when a phase is completed"""
    # ... (rest of the function)
    return {}
