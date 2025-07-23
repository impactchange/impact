# backend/services/predictive_analytics.py
from typing import Dict, Any, List

def predict_task_success_probability(task_id: str, assessment_data: dict, overall_score: float) -> dict:
    """Predict success probability for specific implementation tasks"""
    task_risk_factors = {
        "task_1": {"primary_factors": ["leadership_support", "stakeholder_engagement"], "base_risk": 0.15, "description": "Project Charter and team establishment", "critical_dependencies": ["Executive sponsorship", "Resource allocation"]},
        "task_2": {"primary_factors": ["resource_availability", "workforce_adaptability"], "base_risk": 0.20, "description": "Hands-on training and capability assessment", "critical_dependencies": ["Team availability", "Learning capacity"]},
        "task_3": {"primary_factors": ["change_management_maturity", "communication_effectiveness"], "base_risk": 0.35, "description": "Process analysis and configuration planning", "critical_dependencies": ["Process documentation", "Stakeholder engagement"]},
        "task_4": {"primary_factors": ["technical_readiness", "resource_availability"], "base_risk": 0.25, "description": "System configuration and data preparation", "critical_dependencies": ["Technical expertise", "Data quality"]},
        "task_5": {"primary_factors": ["technical_readiness", "change_management_maturity"], "base_risk": 0.40, "description": "Data loading and environment setup", "critical_dependencies": ["Data accuracy", "System stability"]},
        "task_6": {"primary_factors": ["workforce_adaptability", "communication_effectiveness"], "base_risk": 0.30, "description": "User acceptance testing and feedback", "critical_dependencies": ["User engagement", "Feedback integration"]},
        "task_7": {"primary_factors": ["technical_readiness", "change_management_maturity"], "base_risk": 0.35, "description": "System refinement and optimization", "critical_dependencies": ["Technical agility", "Change adaptability"]},
        "task_8": {"primary_factors": ["workforce_adaptability", "resource_availability"], "base_risk": 0.25, "description": "Production deployment and user training", "critical_dependencies": ["Training effectiveness", "System readiness"]},
        "task_9": {"primary_factors": ["leadership_support", "workforce_adaptability"], "base_risk": 0.45, "description": "Initial go-live with intensive support", "critical_dependencies": ["Support availability", "Issue resolution"]},
        "task_10": {"primary_factors": ["change_management_maturity", "communication_effectiveness"], "base_risk": 0.35, "description": "Stabilization and success validation", "critical_dependencies": ["System stability", "User adoption"]}
    }
    if task_id not in task_risk_factors:
        return {"success_probability": 70.0, "risk_level": "Medium", "confidence": "Low"}
    task_info = task_risk_factors[task_id]
    factor_scores = [assessment_data.get(factor, 3.0) for factor in task_info["primary_factors"]]
    avg_factor_score = sum(factor_scores) / len(factor_scores)
    base_success = 100 - (task_info["base_risk"] * 100)
    readiness_adjustment = (avg_factor_score - 3.0) * 15
    overall_adjustment = (overall_score - 3.0) * 10
    success_probability = max(10, min(95, base_success + readiness_adjustment + overall_adjustment))
    risk_level = "Low" if success_probability >= 80 else "Medium" if success_probability >= 60 else "High"
    return {
        "task_id": task_id, "task_description": task_info["description"], "success_probability": round(success_probability, 1),
        "risk_level": risk_level, "primary_factors": task_info["primary_factors"],
        "factor_scores": {factor: assessment_data.get(factor, 3.0) for factor in task_info["primary_factors"]},
        "critical_dependencies": task_info["critical_dependencies"], "confidence": "High" if len(factor_scores) >= 2 else "Medium"
    }

def predict_budget_overrun_risk(assessment_data: dict, overall_score: float, total_budget: float) -> dict:
    """Predict budget overrun risk based on assessment data and historical patterns"""
    budget_risk_factors = {
        "leadership_support": {"weight": 0.25, "impact": "Low leadership support leads to scope creep and rework"},
        "change_management_maturity": {"weight": 0.30, "impact": "Poor change management causes resistance and delays"},
        "resource_availability": {"weight": 0.20, "impact": "Inadequate resources require additional expertise"},
        "communication_effectiveness": {"weight": 0.15, "impact": "Poor communication leads to misunderstandings and rework"},
        "workforce_adaptability": {"weight": 0.10, "impact": "Low adaptability requires extended training and support"}
    }
    weighted_risk = 0
    risk_details = []
    for factor, config in budget_risk_factors.items():
        score = assessment_data.get(factor, 3.0)
        risk_contribution = (3.0 - score) * config["weight"]
        weighted_risk += risk_contribution
        risk_details.append({"factor": factor, "score": score, "risk_contribution": round(risk_contribution, 2), "impact_description": config["impact"]})
    base_overrun_rate = 0.15
    risk_adjusted_rate = base_overrun_rate + (weighted_risk * 0.20)
    overrun_probability = min(80, max(5, risk_adjusted_rate * 100))
    expected_overrun_percentage = max(0, (weighted_risk * 25))
    expected_overrun_amount = total_budget * (expected_overrun_percentage / 100)
    risk_level = "Low" if overrun_probability < 20 else "Medium" if overrun_probability < 40 else "High"
    return {
        "overrun_probability": round(overrun_probability, 1), "expected_overrun_percentage": round(expected_overrun_percentage, 1),
        "expected_overrun_amount": round(expected_overrun_amount, 2), "risk_level": risk_level, "total_budget": total_budget,
        "risk_adjusted_budget": round(total_budget + expected_overrun_amount, 2), "risk_factors": risk_details,
        "recommendations": generate_budget_risk_recommendations(risk_details)
    }

def predict_scope_creep_risk(assessment_data: dict, assessment_type: str) -> dict:
    """Predict scope creep risk based on assessment data and project type"""
    scope_risk_patterns = {
        "general_readiness": {"high_risk_factors": ["change_management_maturity", "stakeholder_engagement"], "base_risk": 0.25, "typical_scope_additions": ["Additional training", "Extended pilot phase", "More stakeholder sessions"]},
        "software_implementation": {"high_risk_factors": ["technical_readiness", "change_management_maturity"], "base_risk": 0.35, "typical_scope_additions": ["Custom integrations", "Additional data migration", "Enhanced training"]},
        "business_process": {"high_risk_factors": ["change_management_maturity", "communication_effectiveness"], "base_risk": 0.30, "typical_scope_additions": ["Process redesign", "Additional documentation", "Change management activities"]},
        "manufacturing_operations": {"high_risk_factors": ["technical_readiness", "workforce_adaptability"], "base_risk": 0.40, "typical_scope_additions": ["Safety compliance", "Shift coordination", "Operations integration"]}
    }
    pattern = scope_risk_patterns.get(assessment_type, scope_risk_patterns["general_readiness"])
    risk_scores = [(3.0 - assessment_data.get(factor, 3.0)) for factor in pattern["high_risk_factors"]]
    avg_risk_score = sum(risk_scores) / len(risk_scores)
    scope_creep_probability = max(10, min(70, (pattern["base_risk"] + avg_risk_score * 0.15) * 100))
    impact_level = "Low" if scope_creep_probability < 25 else "Medium" if scope_creep_probability < 45 else "High"
    expected_impact = "5-10% additional effort" if impact_level == "Low" else "10-20% additional effort" if impact_level == "Medium" else "20-35% additional effort"
    return {
        "scope_creep_probability": round(scope_creep_probability, 1), "impact_level": impact_level, "expected_impact": expected_impact,
        "high_risk_factors": pattern["high_risk_factors"], "factor_scores": {factor: assessment_data.get(factor, 3.0) for factor in pattern["high_risk_factors"]},
        "typical_scope_additions": pattern["typical_scope_additions"], "mitigation_strategies": generate_scope_creep_mitigation(pattern["high_risk_factors"], assessment_data)
    }

def predict_timeline_optimization(assessment_data: dict, overall_score: float) -> dict:
    """Predict timeline optimization opportunities based on organizational readiness"""
    timeline_factors = {
        "leadership_support": {"acceleration_potential": 0.15, "delay_risk": 0.20, "impact": "Strong leadership can accelerate decisions and approvals"},
        "resource_availability": {"acceleration_potential": 0.10, "delay_risk": 0.25, "impact": "Adequate resources prevent delays and bottlenecks"},
        "change_management_maturity": {"acceleration_potential": 0.20, "delay_risk": 0.30, "impact": "High maturity enables faster adoption and fewer iterations"},
        "workforce_adaptability": {"acceleration_potential": 0.15, "delay_risk": 0.15, "impact": "Adaptable workforce learns faster and requires less support"}
    }
    total_acceleration, total_delay_risk = 0, 0
    optimization_opportunities = []
    for factor, config in timeline_factors.items():
        score = assessment_data.get(factor, 3.0)
        if score >= 4:
            acceleration = config["acceleration_potential"] * (score - 3)
            total_acceleration += acceleration
            optimization_opportunities.append({"factor": factor, "opportunity": "Acceleration", "impact": f"{acceleration:.1%} faster", "description": config["impact"]})
        elif score < 3:
            delay = config["delay_risk"] * (3 - score)
            total_delay_risk += delay
            optimization_opportunities.append({"factor": factor, "opportunity": "Risk Mitigation", "impact": f"{delay:.1%} slower without intervention", "description": config["impact"]})
    net_timeline_impact = total_acceleration - total_delay_risk
    timeline_outlook = "Accelerated" if net_timeline_impact > 0.10 else "Optimized" if net_timeline_impact > 0 else "Standard" if net_timeline_impact > -0.10 else "At Risk"
    expected_timeline = "2-3 weeks faster than standard" if timeline_outlook == "Accelerated" else "On schedule or slightly faster" if timeline_outlook == "Optimized" else "Standard 10-week timeline" if timeline_outlook == "Standard" else "1-2 weeks additional time may be needed"
    return {
        "timeline_outlook": timeline_outlook, "expected_timeline": expected_timeline, "net_timeline_impact": round(net_timeline_impact, 2),
        "acceleration_potential": round(total_acceleration, 2), "delay_risk": round(total_delay_risk, 2),
        "optimization_opportunities": optimization_opportunities, "recommendations": generate_timeline_optimization_recommendations(optimization_opportunities)
    }

def generate_predictive_risk_trending(assessment_data: dict, overall_score: float) -> dict:
    """Generate risk trending analysis for ongoing project monitoring"""
    risk_categories = {
        "Technical Risk": {"factors": ["technical_readiness", "resource_availability"], "trend_pattern": "Decreases over time with proper preparation", "peak_weeks": [4, 5, 7]},
        "Adoption Risk": {"factors": ["workforce_adaptability", "change_management_maturity"], "trend_pattern": "Increases during training, decreases post go-live", "peak_weeks": [6, 8, 9]},
        "Stakeholder Risk": {"factors": ["leadership_support", "communication_effectiveness"], "trend_pattern": "Constant vigilance required throughout project", "peak_weeks": [1, 3, 9]},
        "Resource Risk": {"factors": ["resource_availability", "leadership_support"], "trend_pattern": "Typically increases toward go-live", "peak_weeks": [8, 9, 10]}
    }
    risk_trends = []
    for category, config in risk_categories.items():
        category_scores = [assessment_data.get(factor, 3.0) for factor in config["factors"]]
        category_avg = sum(category_scores) / len(category_scores)
        risk_level = "High" if category_avg < 2.5 else "Medium" if category_avg < 3.5 else "Low"
        risk_trends.append({
            "category": category, "current_risk_level": risk_level, "factor_scores": {factor: assessment_data.get(factor, 3.0) for factor in config["factors"]},
            "trend_pattern": config["trend_pattern"], "peak_weeks": config["peak_weeks"], "monitoring_recommendations": generate_risk_monitoring_recommendations(category, risk_level)
        })
    return {
        "overall_risk_score": round(overall_score, 2), "risk_trends": risk_trends,
        "critical_monitoring_weeks": list(set([week for trend in risk_trends for week in trend["peak_weeks"]])),
        "early_warning_indicators": generate_early_warning_indicators(risk_trends)
    }

def generate_budget_risk_recommendations(risk_details: List[dict]) -> List[str]:
    """Generate specific recommendations for budget risk mitigation"""
    recommendations = []
    for risk in risk_details:
        if risk["risk_contribution"] > 0.15:
            if risk["factor"] == "leadership_support": recommendations.append("Establish executive steering committee with clear decision-making authority")
            elif risk["factor"] == "change_management_maturity": recommendations.append("Implement comprehensive change management program with dedicated resources")
            elif risk["factor"] == "resource_availability": recommendations.append("Secure dedicated team members and establish contingency resource pool")
            elif risk["factor"] == "communication_effectiveness": recommendations.append("Develop robust communication plan with multiple channels and feedback loops")
            elif risk["factor"] == "workforce_adaptability": recommendations.append("Invest in early adopter identification and change champion development")
    return recommendations

def generate_scope_creep_mitigation(high_risk_factors: List[str], assessment_data: dict) -> List[str]:
    """Generate specific mitigation strategies for scope creep"""
    strategies = []
    for factor in high_risk_factors:
        if assessment_data.get(factor, 3.0) < 3:
            if factor == "change_management_maturity": strategies.append("Implement formal change control process with approval gates")
            elif factor == "stakeholder_engagement": strategies.append("Establish clear stakeholder roles and communication protocols")
            elif factor == "technical_readiness": strategies.append("Conduct thorough technical assessment and establish boundaries")
            elif factor == "communication_effectiveness": strategies.append("Create detailed project charter with explicit scope boundaries")
    return strategies

def generate_timeline_optimization_recommendations(opportunities: List[dict]) -> List[str]:
    """Generate timeline optimization recommendations"""
    return [f"Leverage {opp['factor']} strength to accelerate project phases" if opp["opportunity"] == "Acceleration" else f"Address {opp['factor']} weakness to prevent timeline delays" for opp in opportunities]

def generate_risk_monitoring_recommendations(category: str, risk_level: str) -> List[str]:
    """Generate risk monitoring recommendations by category"""
    recommendations = []
    if risk_level == "High":
        recommendations.extend([f"Implement daily monitoring for {category}", f"Establish escalation procedures for {category}"])
    elif risk_level == "Medium":
        recommendations.append(f"Monitor {category} weekly with regular checkpoints")
    else:
        recommendations.append(f"Standard monitoring for {category} is sufficient")
    return recommendations

def generate_early_warning_indicators(risk_trends: List[dict]) -> List[str]:
    """Generate early warning indicators for project monitoring"""
    return [f"Monitor {trend['category']} closely during weeks {trend['peak_weeks']}" for trend in risk_trends if trend["current_risk_level"] == "High"]

def generate_recommended_actions(task_predictions: List[dict], budget_risk: dict, scope_creep_risk: dict) -> List[str]:
    """Generate recommended actions based on predictive analytics"""
    recommendations = []
    if budget_risk.get("risk_level") == "High":
        recommendations.append("High budget overrun risk detected. Review resource allocation and create a contingency plan.")
    if scope_creep_risk.get("impact_level") == "High":
        recommendations.append("High scope creep risk. Implement a strict change control process.")

    high_risk_tasks = [t for t in task_predictions if t.get("risk_level") == "High"]
    if len(high_risk_tasks) > 2:
        recommendations.append(f"Multiple high-risk tasks detected ({len(high_risk_tasks)}). Focus mitigation efforts on these tasks immediately.")

    if not recommendations:
        recommendations.append("Project analytics are within acceptable parameters. Continue with standard monitoring.")

    return recommendations
