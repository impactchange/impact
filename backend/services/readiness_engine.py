from typing import Dict, Any, List
from data.constants import ASSESSMENT_TYPES, IMPACT_PHASES
from datetime import datetime, timedelta
# Assuming ChangeReadinessAssessment schema is imported or defined elsewhere for calculate_newton_laws_analysis
# For now, I'll comment out the type hint to avoid import errors if not strictly necessary for this file.
# from schemas.assessment import ChangeReadinessAssessment

def calculate_universal_readiness_analysis(assessment_data: dict, assessment_type: str) -> Dict[str, Any]:
    scores = []
    dimension_scores = {}
    type_config = ASSESSMENT_TYPES.get(assessment_type, ASSESSMENT_TYPES["general_readiness"])

    for dimension in type_config["dimensions"]:
        dim_id = dimension["id"]
        if dim_id in assessment_data and "score" in assessment_data[dim_id]:
            score = assessment_data[dim_id]["score"]
            scores.append(score)
            dimension_scores[dim_id] = score

    avg_score = sum(scores) / len(scores) if scores else 0
    base_inertia = (5 - avg_score) * 20
    type_multiplier = {
        "software_implementation": 1.1,
        "business_process": 1.0,
        "manufacturing_operations": 1.2,
        "general_readiness": 1.0
    }.get(assessment_type, 1.0)

    organizational_inertia = base_inertia * type_multiplier
    base_force = 100 - (avg_score * 15)
    force_required = base_force * type_multiplier
    resistance_magnitude = organizational_inertia * 0.8

    return {
        "inertia": {
            "value": round(organizational_inertia, 1),
            "interpretation": "Low" if organizational_inertia < 48 else "Medium" if organizational_inertia < 84 else "High",
            "description": f"Organization shows {'low' if organizational_inertia < 48 else 'medium' if organizational_inertia < 84 else 'high'} resistance to {assessment_type.replace('_', ' ')} changes"
        },
        "force": {
            "required": round(force_required, 1),
            "type_factor": round(type_multiplier, 1),
            "description": f"{'Low' if force_required < 60 else 'Medium' if force_required < 90 else 'High'} effort required for successful {assessment_type.replace('_', ' ')} transformation"
        },
        "reaction": {
            "resistance": round(resistance_magnitude, 1),
            "description": f"Expect {'minimal' if resistance_magnitude < 36 else 'moderate' if resistance_magnitude < 72 else 'significant'} organizational pushback"
        }
    }

def generate_typed_ai_analysis(assessment_data: dict, assessment_type: str, overall_score: float, readiness_level: str, analysis_data: dict) -> str:
    type_names = {
        "general_readiness": "Change Management",
        "software_implementation": "Software Implementation",
        "business_process": "Business Process Improvement",
        "manufacturing_operations": "Manufacturing Operations"
    }
    type_name = type_names.get(assessment_type, "Change Management")
    return f"""# {type_name} Readiness Analysis

## Executive Summary
Your organization shows an overall readiness score of {overall_score:.1f}/5 for {type_name.lower()} projects.
Readiness Level: **{readiness_level}**

## Newton's Laws Application
- **Organizational Inertia**: {analysis_data['inertia']['value']} - {analysis_data['inertia']['interpretation']}
- **Required Force**: {analysis_data['force']['required']} units
- **Expected Resistance**: {analysis_data['reaction']['resistance']} units

## Strategic Recommendations
1. Focus on strengthening lowest-scoring dimensions
2. Build comprehensive stakeholder engagement strategy
3. Develop targeted training and communication programs
4. Establish clear success metrics and monitoring systems
5. Create change champion network for peer support
"""

def generate_typed_recommendations(assessment_type: str, dimension_scores: dict, overall_score: float) -> List[str]:
    """Generate recommendations based on assessment type"""

    base_recommendations = [
        "Focus on strengthening lowest-scoring assessment dimensions",
        "Develop comprehensive change champion network",
        "Create clear communication strategy for all stakeholders",
        "Establish baseline performance metrics",
        "Design training programs for affected teams",
        "Build resistance management plan addressing organizational culture"
    ]

    type_specific = {
        "software_implementation": [
            "Ensure technical infrastructure readiness",
            "Plan comprehensive user training and support",
            "Develop data migration and integration strategy",
            "Create system performance monitoring protocols"
        ],
        "business_process": [
            "Document current process workflows and dependencies",
            "Establish process performance baselines",
            "Design cross-functional collaboration frameworks",
            "Create process improvement measurement systems"
        ],
        "manufacturing_operations": [
            "Address shift work coordination challenges",
            "Leverage safety culture for change adoption",
            "Ensure maintenance-operations alignment",
            "Plan for operational constraint management"
        ]
    }

    recommendations = base_recommendations.copy()
    if assessment_type in type_specific:
        recommendations.extend(type_specific[assessment_type])

    return recommendations

def generate_week_by_week_plan(assessment_data: dict, assessment_type: str, overall_score: float) -> dict:
    """Generate tailored week-by-week implementation plan based on assessment results"""

    # Base 10-week implementation structure
    base_weeks = {
        1: {
            "week": 1,
            "phase": "Plan",
            "task_id": "task_1",
            "title": "Kick-off Week",
            "description": "Create Project Charter, detailed project plan, and establish core team members",
            "base_activities": [
                "Project Charter creation",
                "Detailed project planning",
                "Core team establishment",
                "Stakeholder identification"
            ],
            "deliverables": ["Project Charter", "Project Plan", "Team Charter"],
            "duration_hours": 40,
            "base_budget": 8000
        },
        2: {
            "week": 2,
            "phase": "Plan",
            "task_id": "task_2",
            "title": "Core Team Training",
            "description": "Hands-on training where participants experience full capabilities and limitations",
            "base_activities": [
                "Core team training delivery",
                "Hands-on system exploration",
                "Capability assessment",
                "Limitation identification"
            ],
            "deliverables": ["Training Materials", "Capability Assessment", "Team Readiness Report"],
            "duration_hours": 40,
            "base_budget": 6000
        },
        3: {
            "week": 3,
            "phase": "Plan",
            "task_id": "task_3",
            "title": "Business Process Review",
            "description": "Determine configuration regarding user groups, menus, permissions, and authorizations",
            "base_activities": [
                "Business process analysis",
                "User group definition",
                "Permission mapping",
                "Authorization framework"
            ],
            "deliverables": ["Business Process Document", "User Group Matrix", "Permission Framework"],
            "duration_hours": 40,
            "base_budget": 7000
        },
        4: {
            "week": 4,
            "phase": "Configure/Develop/Implement",
            "task_id": "task_4",
            "title": "Configuration & Data Preparation",
            "description": "Set installation parameters, build user groups, prepare data migration",
            "base_activities": [
                "System configuration",
                "User group creation",
                "Data extraction and mapping",
                "Migration preparation"
            ],
            "deliverables": ["Configuration Document", "Data Mapping", "Migration Plan"],
            "duration_hours": 45,
            "base_budget": 9000
        },
        5: {
            "week": 5,
            "phase": "Configure/Develop/Implement",
            "task_id": "task_5",
            "title": "Configuration Completion & Data Loading",
            "description": "Complete configuration and load data into training environment",
            "base_activities": [
                "Configuration finalization",
                "Data validation",
                "Training environment setup",
                "Data loading execution"
            ],
            "deliverables": ["Final Configuration", "Data Validation Report", "Training Environment"],
            "duration_hours": 45,
            "base_budget": 8500
        },
        6: {
            "week": 6,
            "phase": "User Acceptance Testing",
            "task_id": "task_6",
            "title": "Pilot Testing",
            "description": "Pilot testing of functions in training environment by user groups",
            "base_activities": [
                "Pilot user selection",
                "Testing execution",
                "Issue identification",
                "Feedback collection"
            ],
            "deliverables": ["Pilot Test Results", "Issue Log", "User Feedback Report"],
            "duration_hours": 40,
            "base_budget": 6000
        },
        7: {
            "week": 7,
            "phase": "User Acceptance Testing",
            "task_id": "task_7",
            "title": "Configuration Modifications",
            "description": "Modify configuration based on pilot testing and prepare production",
            "base_activities": [
                "Configuration adjustments",
                "User experience optimization",
                "Production preparation",
                "Environment copying"
            ],
            "deliverables": ["Modified Configuration", "Production Environment", "Deployment Plan"],
            "duration_hours": 45,
            "base_budget": 7500
        },
        8: {
            "week": 8,
            "phase": "User Acceptance Testing",
            "task_id": "task_8",
            "title": "Production Setup & Training",
            "description": "Configure production environment and deliver end-user training",
            "base_activities": [
                "Production configuration",
                "Data loading production",
                "End-user training",
                "Role-based instruction"
            ],
            "deliverables": ["Production System", "Training Records", "User Competency Matrix"],
            "duration_hours": 50,
            "base_budget": 10000
        },
        9: {
            "week": 9,
            "phase": "Production Deployment",
            "task_id": "task_9",
            "title": "Go Live - Week 1",
            "description": "Initial go-live with intensive support and monitoring",
            "base_activities": [
                "Go-live execution",
                "Intensive support",
                "Issue resolution",
                "Performance monitoring"
            ],
            "deliverables": ["Go-Live Report", "Issue Resolution Log", "Performance Metrics"],
            "duration_hours": 60,
            "base_budget": 12000
        },
        10: {
            "week": 10,
            "phase": "Production Deployment",
            "task_id": "task_10",
            "title": "Go Live - Week 2",
            "description": "Continued go-live support and stabilization",
            "base_activities": [
                "Ongoing support",
                "System stabilization",
                "User assistance",
                "Success validation"
            ],
            "deliverables": ["Stabilization Report", "User Success Metrics", "Project Closure"],
            "duration_hours": 50,
            "base_budget": 8000
        }
    }

    # Apply assessment-based customizations
    customized_weeks = {}

    for week_num, week_data in base_weeks.items():
        customized_week = week_data.copy()

        # Apply readiness-based modifications
        if overall_score < 3.0:  # Low readiness
            customized_week["risk_level"] = "High"
            customized_week["duration_hours"] = int(week_data["duration_hours"] * 1.3)
            customized_week["base_budget"] = int(week_data["base_budget"] * 1.25)
            customized_week["additional_activities"] = get_low_readiness_activities(week_num, assessment_data)
        elif overall_score < 4.0:  # Medium readiness
            customized_week["risk_level"] = "Medium"
            customized_week["duration_hours"] = int(week_data["duration_hours"] * 1.1)
            customized_week["base_budget"] = int(week_data["base_budget"] * 1.1)
            customized_week["additional_activities"] = get_medium_readiness_activities(week_num, assessment_data)
        else:  # High readiness
            customized_week["risk_level"] = "Low"
            customized_week["duration_hours"] = week_data["duration_hours"]
            customized_week["base_budget"] = week_data["base_budget"]
            customized_week["additional_activities"] = get_high_readiness_activities(week_num, assessment_data)

        # Apply assessment type-specific modifications
        customized_week["type_specific_activities"] = get_type_specific_activities(week_num, assessment_type)

        # Add IMPACT phase alignment
        customized_week["impact_phase_alignment"] = get_impact_alignment(week_num, assessment_data)

        # Calculate final budget with contingency
        risk_multiplier = {"High": 1.2, "Medium": 1.1, "Low": 1.0}[customized_week["risk_level"]]
        customized_week["final_budget"] = int(customized_week["base_budget"] * risk_multiplier)

        customized_weeks[week_num] = customized_week

    # Generate summary metrics
    total_budget = sum(week["final_budget"] for week in customized_weeks.values())
    total_hours = sum(week["duration_hours"] for week in customized_weeks.values())

    return {
        "weeks": customized_weeks,
        "summary": {
            "total_weeks": 10,
            "total_budget": total_budget,
            "total_hours": total_hours,
            "overall_risk_level": "High" if overall_score < 3.0 else "Medium" if overall_score < 4.0 else "Low",
            "success_probability": calculate_success_probability(overall_score, assessment_data),
            "key_risk_factors": identify_key_risks(assessment_data),
            "critical_success_factors": identify_critical_success_factors(assessment_data)
        }
    }

def get_low_readiness_activities(week_num: int, assessment_data: dict) -> List[str]:
    """Additional activities for low readiness organizations"""
    activities_by_week = {
        1: ["Additional stakeholder alignment sessions", "Change resistance assessment", "Communication strategy enhancement"],
        2: ["Extended training sessions", "Change champion identification", "Readiness gap analysis"],
        3: ["Cultural assessment integration", "Additional process documentation", "Resistance point mapping"],
        4: ["Enhanced testing protocols", "Additional quality checks", "Risk mitigation planning"],
        5: ["Extended validation cycles", "Additional user feedback sessions", "Performance optimization"],
        6: ["Expanded pilot group", "Additional testing scenarios", "Enhanced support protocols"],
        7: ["Extended modification cycles", "Additional validation steps", "Risk assessment updates"],
        8: ["Enhanced training delivery", "Additional practice sessions", "Confidence building activities"],
        9: ["Intensive support protocols", "Additional monitoring systems", "Rapid response procedures"],
        10: ["Extended support period", "Additional stabilization activities", "Success reinforcement"]
    }
    return activities_by_week.get(week_num, [])

def get_medium_readiness_activities(week_num: int, assessment_data: dict) -> List[str]:
    """Additional activities for medium readiness organizations"""
    activities_by_week = {
        1: ["Stakeholder engagement optimization", "Communication plan refinement"],
        2: ["Training effectiveness measurement", "Change champion training"],
        3: ["Process optimization workshops", "Best practice integration"],
        4: ["Quality assurance protocols", "Performance baseline establishment"],
        5: ["User experience optimization", "Efficiency improvements"],
        6: ["Pilot success validation", "Feedback integration"],
        7: ["Configuration optimization", "User experience refinement"],
        8: ["Training reinforcement", "Competency validation"],
        9: ["Performance monitoring enhancement", "Success metric tracking"],
        10: ["Best practice documentation", "Continuous improvement planning"]
    }
    return activities_by_week.get(week_num, [])

def get_high_readiness_activities(week_num: int, assessment_data: dict) -> List[str]:
    """Additional activities for high readiness organizations"""
    activities_by_week = {
        1: ["Accelerated planning protocols", "Innovation opportunities identification"],
        2: ["Advanced capability exploration", "Best practice development"],
        3: ["Process excellence initiatives", "Innovation integration"],
        4: ["Advanced configuration options", "Optimization opportunities"],
        5: ["Performance enhancement features", "Advanced functionality"],
        6: ["Innovation pilot testing", "Advanced use case validation"],
        7: ["Advanced feature implementation", "Innovation integration"],
        8: ["Leadership development", "Advanced user empowerment"],
        9: ["Excellence achievement validation", "Success amplification"],
        10: ["Innovation showcase", "Excellence model development"]
    }
    return activities_by_week.get(week_num, [])

def get_type_specific_activities(week_num: int, assessment_type: str) -> List[str]:
    """Get activities specific to assessment type"""
    if assessment_type == "manufacturing_operations":
        return {
            1: ["Maintenance-operations alignment assessment", "Shift work coordination planning"],
            2: ["Manufacturing excellence training", "Operational impact education"],
            3: ["Maintenance process optimization", "Operations integration planning"],
            4: ["Manufacturing-specific configuration", "Operational workflow integration"],
            5: ["Production impact validation", "Operational efficiency testing"],
            6: ["Shift-based pilot testing", "Operations team validation"],
            7: ["Manufacturing optimization", "Operational workflow refinement"],
            8: ["Shift-based training delivery", "Operations team empowerment"],
            9: ["Manufacturing performance monitoring", "Operational excellence tracking"],
            10: ["Maintenance excellence validation", "Manufacturing performance optimization"]
        }.get(week_num, [])

    return []

def get_impact_alignment(week_num: int, assessment_data: dict) -> str:
    """Map weeks to IMPACT phases"""
    impact_mapping = {
        1: "Investigate & Assess",
        2: "Investigate & Assess",
        3: "Mobilize & Prepare",
        4: "Mobilize & Prepare",
        5: "Pilot & Adapt",
        6: "Pilot & Adapt",
        7: "Activate & Deploy",
        8: "Activate & Deploy",
        9: "Cement & Transfer",
        10: "Track & Optimize"
    }
    return impact_mapping.get(week_num, "Unknown")

def calculate_success_probability(overall_score: float, assessment_data: dict) -> float:
    """Calculate implementation success probability"""
    base_probability = min(95, max(15, overall_score * 18))

    # Apply bonus factors based on specific strengths
    if assessment_data.get("leadership_support", 0) >= 4:
        base_probability += 5
    if assessment_data.get("resource_availability", 0) >= 4:
        base_probability += 5
    if assessment_data.get("change_management_maturity", 0) >= 4:
        base_probability += 5

    return min(95, base_probability)

def identify_key_risks(assessment_data: dict) -> List[str]:
    """Identify key risk factors based on assessment scores"""
    risks = []

    if assessment_data.get("leadership_support", 5) < 3:
        risks.append("Limited leadership engagement and support")
    if assessment_data.get("resource_availability", 5) < 3:
        risks.append("Insufficient resource allocation")
    if assessment_data.get("change_management_maturity", 5) < 3:
        risks.append("Low organizational change maturity")
    if assessment_data.get("communication_effectiveness", 5) < 3:
        risks.append("Inadequate communication infrastructure")
    if assessment_data.get("workforce_adaptability", 5) < 3:
        risks.append("Workforce resistance to change")

    return risks

def identify_critical_success_factors(assessment_data: dict) -> List[str]:
    """Identify critical success factors based on assessment"""
    factors = []

    if assessment_data.get("leadership_support", 0) >= 4:
        factors.append("Strong leadership commitment")
    if assessment_data.get("resource_availability", 0) >= 4:
        factors.append("Adequate resource allocation")
    if assessment_data.get("change_management_maturity", 0) >= 4:
        factors.append("High organizational change maturity")
    if assessment_data.get("communication_effectiveness", 0) >= 4:
        factors.append("Effective communication capabilities")
    if assessment_data.get("workforce_adaptability", 0) >= 4:
        factors.append("Adaptable workforce")

    return factors

def get_type_specific_bonus(assessment_type: str, dimension_scores: dict) -> float:
    """Calculate type-specific success probability bonus"""

    bonus = 0.0

    if assessment_type == "software_implementation":
        if dimension_scores.get("technical_infrastructure", 3) >= 4:
            bonus += 5
        if dimension_scores.get("user_adoption_readiness", 3) >= 4:
            bonus += 5
    elif assessment_type == "business_process":
        if dimension_scores.get("process_maturity", 3) >= 4:
            bonus += 5
        if dimension_scores.get("cross_functional_collaboration", 3) >= 4:
            bonus += 5
    elif assessment_type == "manufacturing_operations":
        if dimension_scores.get("maintenance_operations_alignment", 3) >= 4:
            bonus += 5
        if dimension_scores.get("safety_compliance", 3) >= 4:
            bonus += 5

    return bonus

def get_type_specific_risks(assessment_type: str, dimension_scores: dict) -> List[str]:
    """Get risks specific to assessment type"""

    base_risks = ["Organizational resistance to change", "Resource constraints"]

    type_risks = {
        "software_implementation": [
            "Technical infrastructure limitations",
            "User adoption challenges",
            "Data migration complexity",
            "System integration issues"
        ],
        "business_process": [
            "Process complexity and dependencies",
            "Cross-functional coordination challenges",
            "Performance measurement gaps",
            "Change fatigue from process modifications"
        ],
        "manufacturing_operations": [
            "Operational constraint management",
            "Shift work coordination challenges",
            "Safety and compliance requirements",
            "Maintenance-operations alignment issues"
        ]
    }

    risks = base_risks.copy()
    if assessment_type in type_risks:
        risks.extend(type_risks[assessment_type])

    return risks

def get_phase_recommendations_for_type(assessment_type: str) -> Dict[str, str]:
    """Get IMPACT phase recommendations specific to assessment type"""

    base_recommendations = {
        "investigate": "Comprehensive current state analysis and stakeholder mapping",
        "mobilize": "Build strong foundation and prepare all resources",
        "pilot": "Test approach with representative group",
        "activate": "Execute with comprehensive support and monitoring",
        "cement": "Institutionalize changes and transfer ownership",
        "track": "Monitor success and drive continuous improvement"
    }

    type_specific = {
        "software_implementation": {
            "investigate": "Assess technical infrastructure and user readiness",
            "mobilize": "Prepare training programs and technical environment",
            "pilot": "Test system functionality and user experience",
            "activate": "Deploy with technical support and user training",
            "cement": "Establish ongoing support and maintenance procedures",
            "track": "Monitor system performance and user adoption"
        },
        "business_process": {
            "investigate": "Map current processes and identify improvement opportunities",
            "mobilize": "Design new processes and prepare training materials",
            "pilot": "Test new processes with key stakeholder groups",
            "activate": "Implement across all affected departments",
            "cement": "Standardize processes and embed in operations",
            "track": "Monitor process performance and continuous improvement"
        },
        "manufacturing_operations": {
            "investigate": "Assess operational constraints and stakeholder alignment",
            "mobilize": "Build cross-shift communication and training programs",
            "pilot": "Test improvements in controlled operational environment",
            "activate": "Implement with minimal operational disruption",
            "cement": "Embed in operational procedures and culture",
            "track": "Monitor operational performance improvements"
        }
    }

    return type_specific.get(assessment_type, base_recommendations)

def generate_implementation_plan(assessment_type: str, overall_score: float) -> Dict[str, Any]:
    """Generate implementation plan based on type and readiness"""

    # Base timeline calculation
    base_weeks = 16
    if overall_score < 2.5:
        base_weeks = 24  # More time needed for low readiness
    elif overall_score > 4.0:
        base_weeks = 12  # Less time needed for high readiness

    type_adjustments = {
        "software_implementation": 1.2,  # Tech projects take longer
        "business_process": 1.0,  # Standard timeline
        "manufacturing_operations": 1.3,  # Manufacturing takes longer
        "general_readiness": 1.0
    }

    adjusted_weeks = int(base_weeks * type_adjustments.get(assessment_type, 1.0))

    return {
        "suggested_duration_weeks": adjusted_weeks,
        "critical_success_factors": [
            "Strong leadership engagement",
            "Comprehensive stakeholder communication",
            "Adequate resource allocation",
            "Effective training and support"
        ],
        "resource_priorities": [
            "Change management expertise",
            "Training and communication resources",
            "Technical support and infrastructure",
            "Stakeholder engagement systems"
        ],
        "key_milestones": [
            {"phase": "investigate", "milestone": "Readiness assessment complete", "week": 2},
            {"phase": "mobilize", "milestone": "Implementation plan approved", "week": 4},
            {"phase": "pilot", "milestone": "Pilot success validated", "week": 8},
            {"phase": "activate", "milestone": "Full deployment complete", "week": adjusted_weeks - 4},
            {"phase": "cement", "milestone": "Knowledge transfer complete", "week": adjusted_weeks - 2},
            {"phase": "track", "milestone": "Success metrics achieved", "week": adjusted_weeks}
        ]
    }

def calculate_manufacturing_readiness_analysis(assessment_data: dict) -> Dict[str, Any]:
    """Calculate manufacturing-specific readiness analysis using Newton's laws"""
    # Extract scores from assessment data
    scores = []
    dimension_scores = {}

    # Core dimensions
    core_dimensions = [
        'leadership_commitment', 'organizational_culture', 'resource_availability',
        'stakeholder_engagement', 'training_capability'
    ]

    # Manufacturing-specific dimensions
    manufacturing_dimensions = [
        'manufacturing_constraints', 'maintenance_operations_alignment',
        'shift_work_considerations', 'technical_readiness', 'safety_compliance'
    ]

    all_dimensions = core_dimensions + manufacturing_dimensions

    for dim in all_dimensions:
        if dim in assessment_data and 'score' in assessment_data[dim]:
            score = assessment_data[dim]['score']
            scores.append(score)
            dimension_scores[dim] = score

    avg_score = sum(scores) / len(scores) if scores else 0

    # Calculate manufacturing-specific inertia
    manufacturing_weight = 1.2  # Higher weight for manufacturing environment
    organizational_inertia = (5 - avg_score) * 20 * manufacturing_weight

    # Calculate required force considering manufacturing constraints
    base_force = 100 - (avg_score * 15)
    maintenance_alignment_score = dimension_scores.get('maintenance_operations_alignment', 3)
    force_required = base_force * (1 + (5 - maintenance_alignment_score) * 0.2)

    # Calculate resistance considering shift work
    shift_work_score = dimension_scores.get('shift_work_considerations', 3)
    resistance_magnitude = organizational_inertia * (1 + (5 - shift_work_score) * 0.15)

    return {
        "inertia": {
            "value": round(organizational_inertia, 1),
            "interpretation": "Low" if organizational_inertia < 48 else "Medium" if organizational_inertia < 84 else "High",
            "description": f"Manufacturing organization shows {'low' if organizational_inertia < 48 else 'medium' if organizational_inertia < 84 else 'high'} resistance to change"
        },
        "force": {
            "required": round(force_required, 1),
            "maintenance_factor": round(maintenance_alignment_score, 1),
            "description": f"{'Low' if force_required < 60 else 'Medium' if force_required < 90 else 'High'} effort required for successful manufacturing change"
        },
        "reaction": {
            "resistance": round(resistance_magnitude, 1),
            "shift_impact": round(shift_work_score, 1),
            "description": f"Expect {'minimal' if resistance_magnitude < 36 else 'moderate' if resistance_magnitude < 72 else 'significant'} organizational pushback"
        }
    }

# This function might need ChangeReadinessAssessment schema from schemas/assessment.py
# If that's the case, add the import and ensure the schema is available.
def calculate_newton_laws_analysis(assessment: Any) -> Dict[str, Any]: # Changed type hint from ChangeReadinessAssessment
    """Calculate Newton's laws analysis for organizational change"""
    scores = [
        assessment.change_management_maturity.score,
        assessment.communication_effectiveness.score,
        assessment.leadership_support.score,
        assessment.workforce_adaptability.score,
        assessment.resource_adequacy.score
    ]
    avg_score = sum(scores) / len(scores)

    # First Law (Inertia) - resistance to change
    organizational_inertia = (5 - avg_score) * 20  # Higher score = lower inertia

    # Second Law (Force) - effort required
    force_required = 100 - (avg_score * 15)  # Higher readiness = less force needed
    acceleration_potential = avg_score * 20  # How fast change can happen

    # Third Law (Action-Reaction) - expected resistance
    resistance_magnitude = organizational_inertia * 0.8

    return {
        "inertia": {
            "value": round(organizational_inertia, 1),
            "interpretation": "Low" if organizational_inertia < 40 else "Medium" if organizational_inertia < 70 else "High",
            "description": f"Organization shows {'low' if organizational_inertia < 40 else 'medium' if organizational_inertia < 70 else 'high'} resistance to change"
        },
        "force": {
            "required": round(force_required, 1),
            "acceleration": round(acceleration_potential, 1),
            "description": f"{'Low' if force_required < 50 else 'Medium' if force_required < 75 else 'High'} effort required for successful change"
        },
        "reaction": {
            "resistance": round(resistance_magnitude, 1),
            "description": f"Expect {'minimal' if resistance_magnitude < 30 else 'moderate' if resistance_magnitude < 60 else 'significant'} organizational pushback"
        }
    }