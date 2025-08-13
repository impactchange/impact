# backend/services/project_forecasting.py
from typing import Dict, Any, List
from datetime import datetime, timedelta

def generate_advanced_project_forecasting(project_data: dict, assessment_data: dict, predictive_analytics: dict, budget_tracking: dict) -> dict:
    """Generate advanced project outcome forecasting"""

    # Extract key metrics
    overall_score = assessment_data.get("overall_score", 3.0)
    success_probability = predictive_analytics.get("project_outlook", {}).get("success_probability", 70)
    budget_health = budget_tracking.get("budget_tracking", {}).get("overall_metrics", {}).get("budget_health", "Good")

    # Calculate delivery confidence
    delivery_factors = {
        "technical_readiness": assessment_data.get("technical_readiness", 3.0),
        "resource_availability": assessment_data.get("resource_availability", 3.0),
        "stakeholder_engagement": assessment_data.get("stakeholder_engagement", 3.0),
        "change_management_maturity": assessment_data.get("change_management_maturity", 3.0)
    }

    delivery_confidence = sum(delivery_factors.values()) / len(delivery_factors) * 20  # Convert to percentage
    delivery_confidence = max(20, min(95, delivery_confidence))

    # Predict final delivery outcomes
    outcomes = {
        "on_time_probability": calculate_timeline_probability(assessment_data, budget_health),
        "on_budget_probability": calculate_budget_probability(assessment_data, budget_health),
        "scope_completion_probability": calculate_scope_probability(assessment_data),
        "quality_achievement_probability": calculate_quality_probability(assessment_data),
        "stakeholder_satisfaction_probability": calculate_satisfaction_probability(assessment_data)
    }

    # Calculate overall project success score
    overall_success_score = (
        outcomes["on_time_probability"] * 0.25 +
        outcomes["on_budget_probability"] * 0.25 +
        outcomes["scope_completion_probability"] * 0.20 +
        outcomes["quality_achievement_probability"] * 0.15 +
        outcomes["stakeholder_satisfaction_probability"] * 0.15
    )

    # Generate success recommendations
    recommendations = generate_success_recommendations(outcomes, assessment_data)

    # Manufacturing excellence correlation
    manufacturing_correlation = calculate_manufacturing_excellence_correlation(assessment_data, outcomes)

    return {
        "project_id": project_data.get("id", ""),
        "forecasting_confidence": round(delivery_confidence, 1),
        "overall_success_score": round(overall_success_score, 1),
        "delivery_outcomes": {
            "on_time_delivery": round(outcomes["on_time_probability"], 1),
            "budget_compliance": round(outcomes["on_budget_probability"], 1),
            "scope_completion": round(outcomes["scope_completion_probability"], 1),
            "quality_achievement": round(outcomes["quality_achievement_probability"], 1),
            "stakeholder_satisfaction": round(outcomes["stakeholder_satisfaction_probability"], 1)
        },
        "success_drivers": identify_success_drivers(assessment_data),
        "risk_mitigations": identify_risk_mitigations(assessment_data, outcomes),
        "manufacturing_excellence": manufacturing_correlation,
        "recommendations": recommendations,
        "confidence_level": "High" if delivery_confidence > 80 else "Medium" if delivery_confidence > 60 else "Low",
        "generated_at": datetime.utcnow()
    }

def generate_stakeholder_communications(project_data: dict, budget_tracking: dict, project_forecasting: dict, assessment_data: dict) -> dict:
    """Generate automated stakeholder communication content"""

    # Determine communication urgency and tone
    budget_health = budget_tracking.get("budget_tracking", {}).get("overall_metrics", {}).get("budget_health", "Good")
    success_score = project_forecasting.get("overall_success_score", 70)
    budget_alerts = budget_tracking.get("budget_alerts", [])

    # Generate executive summary
    executive_summary = generate_executive_summary(project_data, budget_health, success_score, budget_alerts)

    # Generate detailed status report
    detailed_report = generate_detailed_status_report(project_data, budget_tracking, project_forecasting)

    # Generate stakeholder-specific messages
    stakeholder_messages = {
        "executive_leadership": generate_executive_message(executive_summary, budget_health, success_score),
        "project_team": generate_team_message(project_data, budget_tracking, project_forecasting),
        "client_stakeholders": generate_client_message(project_data, success_score, project_forecasting),
        "technical_teams": generate_technical_message(budget_tracking, assessment_data)
    }

    # Generate alert notifications
    alert_notifications = generate_alert_notifications(budget_alerts, success_score)

    return {
        "project_id": project_data.get("id", ""),
        "communication_date": datetime.utcnow(),
        "executive_summary": executive_summary,
        "detailed_report": detailed_report,
        "stakeholder_messages": stakeholder_messages,
        "alert_notifications": alert_notifications,
        "recommended_frequency": determine_communication_frequency(budget_health, success_score),
        "next_communication_date": calculate_next_communication_date(budget_health, success_score),
        "escalation_required": len([alert for alert in budget_alerts if alert.get("severity") == "High"]) > 0
    }

# Helper functions for advanced forecasting
def calculate_timeline_probability(assessment_data: dict, budget_health: str) -> float:
    baseline = 75
    if assessment_data.get("resource_availability", 3) >= 4:
        baseline += 10
    if assessment_data.get("change_management_maturity", 3) >= 4:
        baseline += 10
    if budget_health in ["Critical", "Concerning"]:
        baseline -= 15
    return max(30, min(95, baseline))

def calculate_budget_probability(assessment_data: dict, budget_health: str) -> float:
    if budget_health == "Excellent":
        return 90
    elif budget_health == "Good":
        return 80
    elif budget_health == "Concerning":
        return 60
    else:
        return 40

def calculate_scope_probability(assessment_data: dict) -> float:
    baseline = 80
    if assessment_data.get("stakeholder_engagement", 3) >= 4:
        baseline += 10
    if assessment_data.get("change_management_maturity", 3) < 3:
        baseline -= 15
    return max(50, min(95, baseline))

def calculate_quality_probability(assessment_data: dict) -> float:
    baseline = 85
    if assessment_data.get("technical_readiness", 3) >= 4:
        baseline += 10
    if assessment_data.get("resource_availability", 3) < 3:
        baseline -= 10
    return max(60, min(95, baseline))

def calculate_satisfaction_probability(assessment_data: dict) -> float:
    baseline = 75
    if assessment_data.get("communication_effectiveness", 3) >= 4:
        baseline += 15
    if assessment_data.get("stakeholder_engagement", 3) >= 4:
        baseline += 10
    return max(50, min(95, baseline))

def calculate_manufacturing_excellence_correlation(assessment_data: dict, outcomes: dict) -> dict:
    """Calculate correlation between project outcomes and manufacturing excellence"""

    # Manufacturing excellence factors
    maintenance_readiness = assessment_data.get("maintenance_operations_alignment", 3.0)
    operational_impact = (outcomes["quality_achievement_probability"] + outcomes["scope_completion_probability"]) / 2

    # Calculate correlation strength
    correlation_strength = min(1.0, (maintenance_readiness / 5.0) * (operational_impact / 100))

    return {
        "correlation_strength": round(correlation_strength, 2),
        "maintenance_excellence_potential": round(maintenance_readiness * 20, 1),
        "operational_performance_impact": round(operational_impact, 1),
        "manufacturing_readiness": "High" if maintenance_readiness >= 4 else "Medium" if maintenance_readiness >= 3 else "Low",
        "excellence_pathway": generate_excellence_pathway(maintenance_readiness, operational_impact)
    }

def generate_excellence_pathway(maintenance_readiness: float, operational_impact: float) -> List[str]:
    """Generate pathway to manufacturing excellence"""
    pathway = []

    if maintenance_readiness >= 4:
        pathway.append("Strong foundation for maintenance excellence established")
    else:
        pathway.append("Focus on building maintenance-operations alignment")

    if operational_impact >= 80:
        pathway.append("High potential for operational performance improvements")
    else:
        pathway.append("Develop operational excellence capabilities")

    pathway.append("Implement continuous improvement processes")
    pathway.append("Measure and track manufacturing performance metrics")

    return pathway

def generate_success_recommendations(outcomes: dict, assessment_data: dict) -> List[str]:
    """Generate specific recommendations for project success"""
    recommendations = []

    if outcomes["on_time_probability"] < 70:
        recommendations.append("Implement accelerated timeline recovery plan")

    if outcomes["on_budget_probability"] < 70:
        recommendations.append("Activate budget control measures immediately")

    if outcomes["stakeholder_satisfaction_probability"] < 70:
        recommendations.append("Enhance stakeholder engagement and communication")

    return recommendations

def identify_success_drivers(assessment_data: dict) -> List[str]:
    """Identify key success drivers for the project"""
    drivers = []

    if assessment_data.get("leadership_support", 3) >= 4:
        drivers.append("Strong leadership commitment")
    if assessment_data.get("resource_availability", 3) >= 4:
        drivers.append("Adequate resource allocation")
    if assessment_data.get("change_management_maturity", 3) >= 4:
        drivers.append("High change management maturity")

    return drivers

def identify_risk_mitigations(assessment_data: dict, outcomes: dict) -> List[str]:
    """Identify specific risk mitigation strategies"""
    mitigations = []

    if outcomes["on_budget_probability"] < 70:
        mitigations.append("Implement weekly budget review and approval process")

    if assessment_data.get("technical_readiness", 3) < 3:
        mitigations.append("Provide additional technical training and support")

    return mitigations

def generate_executive_summary(project_data: dict, budget_health: str, success_score: float, alerts: List[dict]) -> str:
    """Generate executive summary for stakeholder communications"""

    project_name = project_data.get("project_name", "Project")
    alert_count = len([alert for alert in alerts if alert.get("severity") in ["High", "Critical"]])

    summary = f"Project {project_name} Status Update:\n\n"
    summary += f"Overall Success Score: {success_score}%\n"
    summary += f"Budget Health: {budget_health}\n"

    if alert_count > 0:
        summary += f"Critical Alerts: {alert_count} requiring immediate attention\n"
    else:
        summary += "No critical issues identified\n"

    return summary

def generate_detailed_status_report(project_data: dict, budget_tracking: dict, forecasting: dict) -> str:
    """Generate detailed project status report"""

    budget_metrics = budget_tracking.get("budget_tracking", {}).get("overall_metrics", {})

    report = f"Detailed Project Status Report\n"
    report += f"="*50 + "\n\n"
    report += f"Budget Utilization: {budget_metrics.get('budget_utilization', 0):.1f}%\n"
    report += f"Cost Performance Index: {budget_metrics.get('cost_performance_index', 1.0)}\n"
    report += f"Projected Final Cost: ${budget_metrics.get('projected_final_cost', 0):,.0f}\n"
    report += f"Overall Success Probability: {forecasting.get('overall_success_score', 0):.1f}%\n"

    return report

def generate_executive_message(summary: str, budget_health: str, success_score: float) -> str:
    """Generate message for executive leadership"""
    message = f"Executive Leadership Update:\n\n{summary}\n"

    if budget_health in ["Critical", "Concerning"]:
        message += "Immediate executive attention required for budget situation.\n"

    return message

def generate_team_message(project_data: dict, budget_tracking: dict, forecasting: dict) -> str:
    """Generate message for project team"""
    return f"Team Update: Project progressing with focus on budget management and quality delivery."

def generate_client_message(project_data: dict, success_score: float, forecasting: dict) -> str:
    """Generate message for client stakeholders"""
    return f"Client Update: Project {project_data.get('project_name', '')} maintaining {success_score}% success probability."

def generate_technical_message(budget_tracking: dict, assessment_data: dict) -> str:
    """Generate message for technical teams"""
    return f"Technical Update: Focus on technical readiness and resource optimization."

def generate_alert_notifications(alerts: List[dict], success_score: float) -> List[dict]:
    """Generate structured alert notifications"""
    notifications = []

    for alert in alerts:
        notifications.append({
            "type": alert.get("type", "Info"),
            "severity": alert.get("severity", "Low"),
            "message": alert.get("message", ""),
            "action_required": alert.get("recommended_action", ""),
            "urgent": alert.get("severity") in ["High", "Critical"]
        })

    return notifications

def determine_communication_frequency(budget_health: str, success_score: float) -> str:
    """Determine recommended communication frequency"""
    if budget_health in ["Critical"] or success_score < 60:
        return "Daily"
    elif budget_health in ["Concerning"] or success_score < 75:
        return "Weekly"
    else:
        return "Bi-weekly"

def calculate_next_communication_date(budget_health: str, success_score: float) -> datetime:
    """Calculate next recommended communication date"""
    frequency = determine_communication_frequency(budget_health, success_score)

    if frequency == "Daily":
        return datetime.utcnow() + timedelta(days=1)
    elif frequency == "Weekly":
        return datetime.utcnow() + timedelta(weeks=1)
    else:
        return datetime.utcnow() + timedelta(weeks=2)