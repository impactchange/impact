from typing import Dict, Any, List
from data.constants import ASSESSMENT_TYPES
from readiness_engine import (
    calculate_universal_readiness_analysis,
    generate_typed_ai_analysis,
    calculate_success_probability,
    identify_key_risks,
    identify_critical_success_factors
)
from datetime import datetime # Added import for datetime

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
    
    customized_weeks = {}
    
    for week_num, week_data in base_weeks.items():
        customized_week = week_data.copy()
        
        if overall_score < 3.0:
            customized_week["risk_level"] = "High"
            customized_week["duration_hours"] = int(week_data["duration_hours"] * 1.3)
            customized_week["base_budget"] = int(week_data["base_budget"] * 1.25)
            customized_week["additional_activities"] = get_low_readiness_activities(week_num, assessment_data)
        elif overall_score < 4.0:
            customized_week["risk_level"] = "Medium"
            customized_week["duration_hours"] = int(week_data["duration_hours"] * 1.1)
            customized_week["base_budget"] = int(week_data["base_budget"] * 1.1)
            customized_week["additional_activities"] = get_medium_readiness_activities(week_num, assessment_data)
        else:
            customized_week["risk_level"] = "Low"
            customized_week["duration_hours"] = week_data["duration_hours"]
            customized_week["base_budget"] = week_data["base_budget"]
            customized_week["additional_activities"] = get_high_readiness_activities(week_num, assessment_data)
        
        customized_week["type_specific_activities"] = get_type_specific_activities(week_num, assessment_type)
        
        customized_week["impact_phase_alignment"] = get_impact_alignment(week_num, assessment_data)
        
        risk_multiplier = {"High": 1.2, "Medium": 1.1, "Low": 1.0}[customized_week["risk_level"]]
        customized_week["final_budget"] = int(customized_week["base_budget"] * risk_multiplier)
        
        customized_weeks[str(week_num)] = customized_week
    
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
        },
        "metadata": {
            "assessment_id": assessment_data.get("id"),
            "project_name": assessment_data.get("project_name"),
            "assessment_type": assessment_type,
            "overall_readiness_score": overall_score,
            "generated_at": str(datetime.utcnow()),
            "generated_by": "AI Assistant"
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