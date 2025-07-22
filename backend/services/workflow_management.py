# backend/services/workflow_management.py
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
# Assuming IMPACT_PHASES is imported from data.constants
from data.constants import IMPACT_PHASES

def generate_phase_based_intelligence(phase_name: str, assessment_data: dict, project_data: dict, completed_phases: List[dict] = None) -> dict:
    """Generate intelligent recommendations for each IMPACT phase based on assessment data and project context"""

    # Phase name mapping from short names to full names
    phase_name_mapping = {
        "investigate": "Investigate & Assess",
        "mobilize": "Mobilize & Prepare",
        "pilot": "Pilot & Adapt",
        "activate": "Activate & Deploy",
        "cement": "Cement & Transfer",
        "track": "Track & Optimize"
    }

    # Map short phase name to full name
    full_phase_name = phase_name_mapping.get(phase_name, phase_name)

    if full_phase_name not in IMPACT_PHASES:
        return {"error": f"Unknown phase: {phase_name}"}

    phase_info = IMPACT_PHASES[full_phase_name]

    # Calculate phase-specific recommendations based on assessment data
    phase_recommendations = generate_phase_recommendations(full_phase_name, assessment_data, project_data, phase_info)

    # Generate budget recommendations
    budget_recommendations = generate_phase_budget_recommendations(full_phase_name, assessment_data, project_data, phase_info)

    # Generate scope recommendations
    scope_recommendations = generate_phase_scope_recommendations(full_phase_name, assessment_data, project_data, phase_info)

    # Generate success probability for this phase
    phase_success_probability = calculate_phase_success_probability(full_phase_name, assessment_data, project_data, phase_info)

    # Generate risks and mitigation strategies
    phase_risks = identify_phase_risks(full_phase_name, assessment_data, project_data, phase_info)

    # Generate lessons learned from previous phases
    lessons_from_previous = extract_lessons_from_previous_phases(completed_phases) if completed_phases else []

    return {
        "phase_name": phase_name,  # Return original short name
        "full_phase_name": full_phase_name,  # Also return full name
        "phase_number": phase_info["phase_number"],
        "phase_intelligence": {
            "key_activities": phase_info["key_activities"],
            "critical_success_factors": phase_info["critical_success_factors"],
            "typical_duration_weeks": phase_info["typical_duration_weeks"],
            "budget_percentage": phase_info["budget_percentage"],
            "success_probability": phase_success_probability,
            "recommendations": phase_recommendations,
            "budget_recommendations": budget_recommendations,
            "scope_recommendations": scope_recommendations,
            "risks_and_mitigations": phase_risks,
            "lessons_from_previous": lessons_from_previous
        },
        "generated_at": datetime.utcnow()
    }

def generate_phase_recommendations(phase_name: str, assessment_data: dict, project_data: dict, phase_info: dict) -> List[str]:
    """Generate specific recommendations for each phase"""
    recommendations = []

    # Base recommendations for each phase
    base_recommendations = {
        "Investigate & Assess": [
            "Conduct comprehensive stakeholder mapping and engagement planning",
            "Establish baseline performance metrics and current state documentation",
            "Identify and prioritize key change management challenges",
            "Develop detailed communication strategy for all stakeholder groups"
        ],
        "Mobilize & Prepare": [
            "Form cross-functional project team with clear roles and responsibilities",
            "Develop comprehensive change management plan with timeline and milestones",
            "Create training program design tailored to different user groups",
            "Establish governance structure and decision-making processes"
        ],
        "Pilot & Adapt": [
            "Select representative pilot group that reflects broader organization",
            "Implement comprehensive testing and validation protocols",
            "Establish feedback collection mechanisms and rapid response processes",
            "Document lessons learned and adapt strategies based on pilot results"
        ],
        "Activate & Deploy": [
            "Execute full-scale deployment with comprehensive support systems",
            "Deliver role-based training to all affected users",
            "Implement performance monitoring and issue resolution processes",
            "Maintain intensive support during initial deployment period"
        ],
        "Cement & Transfer": [
            "Transfer knowledge and ownership to internal teams",
            "Document all processes and establish sustainable practices",
            "Develop internal change management capabilities",
            "Create sustainability plan for long-term success"
        ],
        "Track & Optimize": [
            "Implement continuous performance monitoring and measurement",
            "Identify and capture best practices for sharing",
            "Develop continuous improvement processes",
            "Plan for future enhancements and scaling opportunities"
        ]
    }

    recommendations.extend(base_recommendations.get(phase_name, []))

    # Add assessment-specific recommendations
    overall_score = assessment_data.get("overall_score", 3.0)

    for factor in phase_info["critical_success_factors"]:
        factor_score = assessment_data.get(factor, 3.0)
        if factor_score < 3.0:
            recommendations.append(generate_factor_specific_recommendation(factor, phase_name))

    # Add project-specific recommendations based on budget and scope
    total_budget = project_data.get("total_budget", 100000)
    if total_budget < 50000:
        recommendations.append(f"Given limited budget, focus on highest-impact activities for {phase_name}")
    elif total_budget > 200000:
        recommendations.append(f"Leverage substantial budget to implement comprehensive {phase_name} activities")

    return recommendations[:6]  # Limit to 6 recommendations

def generate_phase_budget_recommendations(phase_name: str, assessment_data: dict, project_data: dict, phase_info: dict) -> dict:
    """Generate budget recommendations for each phase"""
    total_budget = project_data.get("total_budget", 100000)
    phase_budget = total_budget * (phase_info["budget_percentage"] / 100)

    # Adjust based on assessment readiness
    overall_score = assessment_data.get("overall_score", 3.0)

    if overall_score < 2.5:
        budget_multiplier = 1.3  # Need more budget for low readiness
        risk_level = "High"
    elif overall_score < 3.5:
        budget_multiplier = 1.1  # Slight increase for medium readiness
        risk_level = "Medium"
    else:
        budget_multiplier = 1.0  # Standard budget for high readiness
        risk_level = "Low"

    recommended_budget = phase_budget * budget_multiplier

    return {
        "recommended_budget": round(recommended_budget, 2),
        "budget_percentage": phase_info["budget_percentage"],
        "risk_level": risk_level,
        "budget_multiplier": budget_multiplier,
        "budget_breakdown": generate_budget_breakdown(phase_name, recommended_budget),
        "contingency_percentage": 20 if risk_level == "High" else 15 if risk_level == "Medium" else 10
    }

def generate_phase_scope_recommendations(phase_name: str, assessment_data: dict, project_data: dict, phase_info: dict) -> List[str]:
    """Generate scope recommendations for each phase"""
    scope_recommendations = []

    # Base scope guidance
    scope_recommendations.append(f"Focus on core {phase_name} activities: {', '.join(phase_info['key_activities'][:2])}")

    # Assessment-based scope adjustments
    overall_score = assessment_data.get("overall_score", 3.0)

    if overall_score < 2.5:
        scope_recommendations.append("Consider reducing scope complexity due to organizational readiness challenges")
        scope_recommendations.append("Implement additional change management activities to address readiness gaps")
    elif overall_score > 4.0:
        scope_recommendations.append("Organization readiness allows for accelerated scope delivery")
        scope_recommendations.append("Consider adding value-enhancement activities within phase budget")

    return scope_recommendations

def calculate_phase_success_probability(phase_name: str, assessment_data: dict, project_data: dict, phase_info: dict) -> float:
    """Calculate success probability for specific phase"""
    base_probability = 75  # Base 75% success rate

    # Adjust based on critical success factors
    for factor in phase_info["critical_success_factors"]:
        factor_score = assessment_data.get(factor, 3.0)
        if factor_score >= 4:
            base_probability += 5
        elif factor_score < 3:
            base_probability -= 10

    # Adjust based on overall readiness
    overall_score = assessment_data.get("overall_score", 3.0)
    readiness_adjustment = (overall_score - 3.0) * 10

    final_probability = base_probability + readiness_adjustment
    return max(20, min(95, final_probability))

def identify_phase_risks(full_phase_name: str, assessment_data: dict, project_data: dict, phase_info: dict) -> List[dict]:
    """Identify risks and mitigation strategies for each phase"""
    risks = []

    # Phase-specific risks
    phase_risks = {
        "Investigate & Assess": [
            {"risk": "Incomplete stakeholder identification", "mitigation": "Conduct comprehensive stakeholder mapping exercise"},
            {"risk": "Resistance to current state assessment", "mitigation": "Emphasize improvement focus rather than criticism"},
            {"risk": "Inadequate baseline data", "mitigation": "Implement systematic data collection protocols"}
        ],
        "Mobilize & Prepare": [
            {"risk": "Insufficient resource allocation", "mitigation": "Secure executive commitment for dedicated resources"},
            {"risk": "Competing priorities", "mitigation": "Establish clear project governance and priority framework"},
            {"risk": "Team skill gaps", "mitigation": "Provide targeted training and external expertise"}
        ],
        "Pilot & Adapt": [
            {"risk": "Pilot group not representative", "mitigation": "Carefully select diverse, representative pilot participants"},
            {"risk": "Limited pilot feedback", "mitigation": "Implement multiple feedback channels and regular check-ins"},
            {"risk": "Resistance to changes", "mitigation": "Emphasize pilot nature and incorporate participant input"}
        ],
        "Activate & Deploy": [
            {"risk": "System performance issues", "mitigation": "Conduct thorough performance testing and optimization"},
            {"risk": "Training effectiveness", "mitigation": "Implement role-based training with competency validation"},
            {"risk": "Support system overload", "mitigation": "Scale support resources and implement tiered support model"}
        ],
        "Cement & Transfer": [
            {"risk": "Knowledge transfer gaps", "mitigation": "Implement systematic knowledge transfer protocols"},
            {"risk": "Sustainability challenges", "mitigation": "Develop comprehensive sustainability plan and internal capabilities"},
            {"risk": "Loss of momentum", "mitigation": "Maintain engagement through continuous improvement activities"}
        ],
        "Track & Optimize": [
            {"risk": "Measurement system gaps", "mitigation": "Implement comprehensive performance measurement framework"},
            {"risk": "Continuous improvement fatigue", "mitigation": "Balance improvement activities with operational stability"},
            {"risk": "Benefits realization delays", "mitigation": "Establish clear benefits tracking and reporting mechanisms"}
        ]
    }

    risks.extend(phase_risks.get(full_phase_name, []))

    # Add assessment-specific risks
    for factor in phase_info["critical_success_factors"]:
        factor_score = assessment_data.get(factor, 3.0)
        if factor_score < 3.0:
            risks.append({
                "risk": f"Low {factor.replace('_', ' ')} may impact {full_phase_name} success",
                "mitigation": generate_factor_mitigation(factor, full_phase_name)
            })

    return risks[:5]  # Limit to 5 key risks

def generate_factor_specific_recommendation(factor: str, phase_name: str) -> str:
    """Generate specific recommendations for assessment factors"""
    recommendations = {
        "leadership_support": f"Secure stronger leadership engagement for {phase_name} through executive briefings and governance participation",
        "resource_availability": f"Ensure adequate resource allocation for {phase_name} activities through detailed resource planning",
        "change_management_maturity": f"Enhance change management capabilities through training and methodology adoption for {phase_name}",
        "communication_effectiveness": f"Improve communication strategies and channels for {phase_name} stakeholder engagement",
        "workforce_adaptability": f"Develop workforce readiness for {phase_name} through targeted training and support",
        "technical_readiness": f"Strengthen technical capabilities and infrastructure for {phase_name} requirements",
        "stakeholder_engagement": f"Increase stakeholder participation and buy-in for {phase_name} activities"
    }

    return recommendations.get(factor, f"Address {factor.replace('_', ' ')} challenges for {phase_name} success")

def generate_factor_mitigation(factor: str, phase_name: str) -> str:
    """Generate mitigation strategies for assessment factors"""
    mitigations = {
        "leadership_support": f"Implement executive engagement plan with regular updates and decision points",
        "resource_availability": f"Develop resource sharing agreements and contingency resource plans",
        "change_management_maturity": f"Provide change management training and establish change champion network",
        "communication_effectiveness": f"Implement multi-channel communication strategy with feedback loops",
        "workforce_adaptability": f"Create comprehensive training program with ongoing support",
        "technical_readiness": f"Conduct technical readiness assessment and capability development",
        "stakeholder_engagement": f"Establish stakeholder engagement plan with regular touchpoints"
    }

    return mitigations.get(factor, f"Develop targeted improvement plan for {factor.replace('_', ' ')}")

def generate_budget_breakdown(phase_name: str, total_budget: float) -> dict:
    """Generate detailed budget breakdown for each phase"""
    breakdowns = {
        "Investigate & Assess": {
            "stakeholder_analysis": 0.25,
            "current_state_assessment": 0.30,
            "gap_analysis": 0.20,
            "documentation": 0.15,
            "risk_assessment": 0.10
        },
        "Mobilize & Prepare": {
            "team_formation": 0.20,
            "change_management_planning": 0.25,
            "communication_strategy": 0.20,
            "training_design": 0.25,
            "governance_setup": 0.10
        },
        "Pilot & Adapt": {
            "pilot_implementation": 0.40,
            "testing_validation": 0.25,
            "feedback_collection": 0.15,
            "strategy_refinement": 0.20
        },
        "Activate & Deploy": {
            "full_deployment": 0.35,
            "training_delivery": 0.30,
            "support_systems": 0.25,
            "performance_monitoring": 0.10
        },
        "Cement & Transfer": {
            "knowledge_transfer": 0.40,
            "process_documentation": 0.25,
            "sustainability_planning": 0.20,
            "ownership_transition": 0.15
        },
        "Track & Optimize": {
            "performance_monitoring": 0.30,
            "continuous_improvement": 0.25,
            "best_practice_sharing": 0.20,
            "strategic_planning": 0.25
        }
    }

    breakdown = breakdowns.get(phase_name, {"general_activities": 1.0})
    return {activity: round(total_budget * percentage, 2) for activity, percentage in breakdown.items()}

def extract_lessons_from_previous_phases(completed_phases: List[dict]) -> List[str]:
    """Extract lessons learned from previously completed phases"""
    lessons = []

    for phase in completed_phases:
        if phase.get("lessons_learned"):
            lessons.append(f"From {phase['phase_name']}: {phase['lessons_learned']}")

        if phase.get("success_status") == "failed" and phase.get("failure_reason"):
            lessons.append(f"Avoid: {phase['failure_reason']} (from {phase['phase_name']})")

        if phase.get("scope_changes"):
            lessons.append(f"Scope management: Monitor {', '.join(phase['scope_changes'])} (from {phase['phase_name']})")

    return lessons[:3]  # Limit to 3 key lessons

def generate_phase_completion_analysis(phase_data: dict, assessment_data: dict, project_data: dict) -> dict:
    """Generate comprehensive analysis when a phase is completed"""

    phase_name = phase_data.get("phase_name", "")
    completion_percentage = phase_data.get("completion_percentage", 0)
    success_status = phase_data.get("success_status", "")
    budget_spent = phase_data.get("budget_spent", 0)

    # Analyze completion effectiveness
    completion_analysis = {
        "completion_score": calculate_completion_score(phase_data),
        "budget_performance": analyze_budget_performance(phase_data, project_data),
        "timeline_performance": analyze_timeline_performance(phase_data),
        "success_factors": identify_success_factors(phase_data, assessment_data),
        "improvement_areas": identify_improvement_areas(phase_data, assessment_data),
        "next_phase_readiness": assess_next_phase_readiness(phase_data, assessment_data),
        "recommendations_for_next_phase": generate_next_phase_recommendations(phase_data, assessment_data, project_data)
    }

    return completion_analysis

def calculate_completion_score(phase_data: dict) -> float:
    """Calculate overall completion score for a phase"""
    completion_percentage = phase_data.get("completion_percentage", 0)
    success_status = phase_data.get("success_status", "")

    base_score = completion_percentage

    if success_status == "successful":
        base_score += 10
    elif success_status == "partially_successful":
        base_score += 5
    elif success_status == "failed":
        base_score -= 20

    return max(0, min(100, base_score))

def analyze_budget_performance(phase_data: dict, project_data: dict) -> dict:
    """Analyze budget performance for completed phase"""
    budget_spent = phase_data.get("budget_spent", 0)
    # Calculate expected budget based on phase and project data
    # This is a simplified calculation - in practice, would use phase budget allocation
    total_budget = project_data.get("total_budget", 100000)
    expected_budget = total_budget * 0.15  # Simplified - would vary by phase

    variance = budget_spent - expected_budget
    variance_percentage = (variance / expected_budget * 100) if expected_budget > 0 else 0

    if variance_percentage <= 5:
        performance = "Excellent"
    elif variance_percentage <= 15:
        performance = "Good"
    elif variance_percentage <= 25:
        performance = "Acceptable"
    else:
        performance = "Concerning"

    return {
        "budget_spent": budget_spent,
        "expected_budget": expected_budget,
        "variance": variance,
        "variance_percentage": variance_percentage,
        "performance": performance
    }

def analyze_timeline_performance(phase_data: dict) -> dict:
    """Analyze timeline performance for completed phase"""
    start_date = phase_data.get("start_date")
    completion_date = phase_data.get("completion_date")

    if not start_date or not completion_date:
        return {"performance": "Unable to assess"}

    # Calculate actual duration (simplified)
    actual_duration = "N/A"  # Would calculate based on dates
    expected_duration = "N/A"  # Would be based on phase expectations

    return {
        "actual_duration": actual_duration,
        "expected_duration": expected_duration,
        "performance": "On Schedule"  # Would be calculated
    }

def identify_success_factors(phase_data: dict, assessment_data: dict) -> List[str]:
    """Identify what contributed to phase success"""
    success_factors = []

    if phase_data.get("success_status") == "successful":
        success_factors.append("Strong execution of planned activities")
        success_factors.append("Effective stakeholder engagement")
        success_factors.append("Adequate resource allocation")

    # Add assessment-based success factors
    for factor, score in assessment_data.items():
        if isinstance(score, (int, float)) and score >= 4:
            success_factors.append(f"High {factor.replace('_', ' ')} contributed to success")

    return success_factors[:5]

def identify_improvement_areas(phase_data: dict, assessment_data: dict) -> List[str]:
    """Identify areas for improvement in future phases"""
    improvement_areas = []

    if phase_data.get("failure_reason"):
        improvement_areas.append(f"Address: {phase_data['failure_reason']}")

    if phase_data.get("scope_changes"):
        improvement_areas.append("Improve scope management and change control")

    # Add assessment-based improvement areas
    for factor, score in assessment_data.items():
        if isinstance(score, (int, float)) and score < 3:
            improvement_areas.append(f"Strengthen {factor.replace('_', ' ')} for future phases")

    return improvement_areas[:5]

def assess_next_phase_readiness(phase_data: dict, assessment_data: dict) -> dict:
    """Assess readiness for next phase"""
    completion_percentage = phase_data.get("completion_percentage", 0)
    success_status = phase_data.get("success_status", "")

    if completion_percentage >= 90 and success_status == "successful":
        readiness_level = "High"
        readiness_score = 85
    elif completion_percentage >= 75 and success_status in ["successful", "partially_successful"]:
        readiness_level = "Medium"
        readiness_score = 70
    else:
        readiness_level = "Low"
        readiness_score = 50

    return {
        "readiness_level": readiness_level,
        "readiness_score": readiness_score,
        "prerequisites_met": completion_percentage >= 75,
        "recommendations": generate_readiness_recommendations(readiness_level)
    }

def generate_readiness_recommendations(readiness_level: str) -> List[str]:
    """Generate recommendations based on readiness level"""
    recommendations = {
        "High": [
            "Proceed to next phase with standard approach",
            "Leverage momentum from current phase success",
            "Consider accelerated timeline if resources permit"
        ],
        "Medium": [
            "Address any remaining gaps before proceeding",
            "Implement additional monitoring for next phase",
            "Consider additional resources for next phase"
        ],
        "Low": [
            "Complete current phase activities before proceeding",
            "Conduct readiness assessment for next phase",
            "Consider extended timeline or additional resources"
        ]
    }

    return recommendations.get(readiness_level, [])

def generate_next_phase_recommendations(phase_data: dict, assessment_data: dict, project_data: dict) -> List[str]:
    """Generate specific recommendations for the next phase"""
    recommendations = []

    current_phase = phase_data.get("phase_name", "")

    # Map to next phase
    phase_sequence = [
        "Investigate & Assess",
        "Mobilize & Prepare",
        "Pilot & Adapt",
        "Activate & Deploy",
        "Cement & Transfer",
        "Track & Optimize"
    ]

    try:
        current_index = phase_sequence.index(current_phase)
        if current_index < len(phase_sequence) - 1:
            next_phase = phase_sequence[current_index + 1]

            # Generate next phase intelligence
            # This would ideally call a function from workflow_management itself or a specialized sub-module.
            # For now, placeholder or direct re-implementation for demonstration purposes.
            # In a real scenario, to avoid circular dependencies, these parts might need
            # careful restructuring or passing of pre-calculated data.
            # For simplicity in refactoring, assuming it calls back into this service if needed.
            # next_phase_intelligence = generate_phase_based_intelligence(next_phase, assessment_data, project_data)
            # recommendations.extend(next_phase_intelligence["phase_intelligence"]["recommendations"][:3])
            recommendations.append(f"Generate intelligence for {next_phase} using relevant data.")

            # Add transition-specific recommendations
            recommendations.append(f"Prepare for {next_phase} by building on current phase successes")

            if phase_data.get("lessons_learned"):
                recommendations.append(f"Apply lessons learned: {phase_data['lessons_learned']}")

    except ValueError:
        recommendations.append("Review phase sequence and plan next steps")

    return recommendations[:5]

def calculate_project_progress(project_data: Dict) -> float:
    """Calculate overall project progress based on completed tasks, deliverables, and milestones"""
    total_items = 0
    completed_items = 0

    # Count tasks
    if project_data.get("tasks"):
        total_items += len(project_data["tasks"])
        completed_items += len([task for task in project_data["tasks"] if task.get("status") == "completed"])

    # Count deliverables
    if project_data.get("deliverables"):
        total_items += len(project_data["deliverables"])
        completed_items += len([deliv for deliv in project_data["deliverables"] if deliv.get("status") in ["completed", "approved"]])

    # Count milestones
    if project_data.get("milestones"):
        total_items += len(project_data["milestones"])
        completed_items += len([milestone for milestone in project_data["milestones"] if milestone.get("status") == "completed"])

    if total_items == 0:
        return 0.0

    return (completed_items / total_items) * 100

def calculate_phase_progress(project_data: Dict, phase: str) -> float:
    """Calculate progress for a specific phase"""
    phase_items = 0
    completed_phase_items = 0

    # Count phase-specific tasks
    if project_data.get("tasks"):
        phase_tasks = [task for task in project_data["tasks"] if task.get("phase") == phase]
        phase_items += len(phase_tasks)
        completed_phase_items += len([task for task in phase_tasks if task.get("status") == "completed"])

    # Count phase-specific deliverables
    if project_data.get("deliverables"):
        # Deliverables are associated with phases through the IMPACT_PHASES configuration
        phase_config = IMPACT_PHASES.get(phase, {})
        phase_deliverable_names = [d["name"] for d in phase_config.get("deliverables", [])]
        phase_deliverables = [d for d in project_data["deliverables"] if d.get("name") in phase_deliverable_names]
        phase_items += len(phase_deliverables)
        completed_phase_items += len([d for d in phase_deliverables if d.get("status") in ["completed", "approved"]])

    # Count phase-specific milestones
    if project_data.get("milestones"):
        phase_milestones = [m for m in project_data["milestones"] if m.get("phase") == phase]
        phase_items += len(phase_milestones)
        completed_phase_items += len([m for m in phase_milestones if m.get("status") == "completed"])

    if phase_items == 0:
        return 0.0

    return (completed_phase_items / phase_items) * 100