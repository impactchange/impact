# backend/services/predictive_analytics.py
from typing import Dict, Any, List
# from data.constants import IMPACT_PHASES # Assuming this might be needed later for tasks based on phases
# from schemas.assessment import ChangeReadinessAssessment # Assuming this might be needed for full assessment object

def predict_task_success_probability(task_id: str, assessment_data: dict, overall_score: float) -> dict:
    """Predict success probability for specific implementation tasks"""

    # Task-specific risk factors based on DigitalThinker methodology
    task_risk_factors = {
        "task_1": {  # Kick-off Week
            "primary_factors": ["leadership_support", "stakeholder_engagement"],
            "base_risk": 0.15,
            "description": "Project Charter and team establishment",
            "critical_dependencies": ["Executive sponsorship", "Resource allocation"]
        },
        "task_2": {  # Core Team Training
            "primary_factors": ["resource_availability", "workforce_adaptability"],
            "base_risk": 0.20,
            "description": "Hands-on training and capability assessment",
            "critical_dependencies": ["Team availability", "Learning capacity"]
        },
        "task_3": {  # Business Process Review
            "primary_factors": ["change_management_maturity", "communication_effectiveness"],
            "base_risk": 0.35,
            "description": "Process analysis and configuration planning",
            "critical_dependencies": ["Process documentation", "Stakeholder engagement"]
        },
        "task_4": {  # EAM Configuration
            "primary_factors": ["technical_readiness", "resource_availability"],
            "base_risk": 0.25,
            "description": "System configuration and data preparation",
            "critical_dependencies": ["Technical expertise", "Data quality"]
        },
        "task_5": {  # Data Migration
            "primary_factors": ["technical_readiness", "change_management_maturity"],
            "base_risk": 0.40,
            "description": "Data loading and environment setup",
            "critical_dependencies": ["Data accuracy", "System stability"]
        },
        "task_6": {  # Pilot Testing
            "primary_factors": ["workforce_adaptability", "communication_effectiveness"],
            "base_risk": 0.30,
            "description": "User acceptance testing and feedback",
            "critical_dependencies": ["User engagement", "Feedback integration"]
        },
        "task_7": {  # Configuration Modifications
            "primary_factors": ["technical_readiness", "change_management_maturity"],
            "base_risk": 0.35,
            "description": "System refinement and optimization",
            "critical_dependencies": ["Technical agility", "Change adaptability"]
        },
        "task_8": {  # Production Setup & Training
            "primary_factors": ["workforce_adaptability", "resource_availability"],
            "base_risk": 0.25,
            "description": "Production deployment and user training",
            "critical_dependencies": ["Training effectiveness", "System readiness"]
        },
        "task_9": {  # Go Live - Week 1
            "primary_factors": ["leadership_support", "workforce_adaptability"],
            "base_risk": 0.45,
            "description": "Initial go-live with intensive support",
            "critical_dependencies": ["Support availability", "Issue resolution"]
        },
        "task_10": {  # Go Live - Week 2
            "primary_factors": ["change_management_maturity", "communication_effectiveness"],
            "base_risk": 0.35,
            "description": "Stabilization and success validation",
            "critical_dependencies": ["System stability", "User adoption"]
        }
    }

    if task_id not in task_risk_factors:
        return {"success_probability": 70.0, "risk_level": "Medium", "confidence": "Low"}

    task_info = task_risk_factors[task_id]

    # Calculate risk score based on primary factors
    factor_scores = []
    for factor in task_info["primary_factors"]:
        score = assessment_data.get(factor, 3.0)
        factor_scores.append(score)

    avg_factor_score = sum(factor_scores) / len(factor_scores)

    # Calculate success probability
    base_success = 100 - (task_info["base_risk"] * 100)
    readiness_adjustment = (avg_factor_score - 3.0) * 15  # ±15% per point from neutral
    overall_adjustment = (overall_score - 3.0) * 10  # ±10% per point from neutral

    success_probability = base_success + readiness_adjustment + overall_adjustment
    success_probability = max(10, min(95, success_probability))

    # Determine risk level
    if success_probability >= 80:
        risk_level = "Low"
    elif success_probability >= 60:
        risk_level = "Medium"
    else:
        risk_level = "High"

    return {
        "task_id": task_id,
        "task_description": task_info["description"],
        "success_probability": round(success_probability, 1),
        "risk_level": risk_level,
        "primary_factors": task_info["primary_factors"],
        "factor_scores": {factor: assessment_data.get(factor, 3.0) for factor in task_info["primary_factors"]},
        "critical_dependencies": task_info["critical_dependencies"],
        "confidence": "High" if len(factor_scores) >= 2 else "Medium"
    }

def predict_budget_overrun_risk(assessment_data: dict, overall_score: float, total_budget: float) -> dict:
    """Predict budget overrun risk based on assessment data and historical patterns"""

    # Risk factors that historically correlate with budget overruns
    budget_risk_factors = {
        "leadership_support": {
            "weight": 0.25,
            "impact": "Low leadership support leads to scope creep and rework"
        },
        "change_management_maturity": {
            "weight": 0.30,
            "impact": "Poor change management causes resistance and delays"
        },
        "resource_availability": {
            "weight": 0.20,
            "impact": "Inadequate resources require additional expertise"
        },
        "communication_effectiveness": {
            "weight": 0.15,
            "impact": "Poor communication leads to misunderstandings and rework"
        },
        "workforce_adaptability": {
            "weight": 0.10,
            "impact": "Low adaptability requires extended training and support"
        }
    }

    # Calculate weighted risk score
    weighted_risk = 0
    risk_details = []

    for factor, config in budget_risk_factors.items():
        score = assessment_data.get(factor, 3.0)
        risk_contribution = (3.0 - score) * config["weight"]  # Higher risk for lower scores
        weighted_risk += risk_contribution

        risk_details.append({
            "factor": factor,
            "score": score,
            "risk_contribution": round(risk_contribution, 2),
            "impact_description": config["impact"]
        })

    # Calculate overrun probability and amount
    base_overrun_rate = 0.15  # 15% base overrun rate
    risk_adjusted_rate = base_overrun_rate + (weighted_risk * 0.20)  # Up to 20% additional risk

    overrun_probability = min(80, max(5, risk_adjusted_rate * 100))
    expected_overrun_percentage = max(0, (weighted_risk * 25))  # Up to 25% overrun
    expected_overrun_amount = total_budget * (expected_overrun_percentage / 100)

    # Determine risk level
    if overrun_probability < 20:
        risk_level = "Low"
    elif overrun_probability < 40:
        risk_level = "Medium"
    else:
        risk_level = "High"

    return {
        "overrun_probability": round(overrun_probability, 1),
        "expected_overrun_percentage": round(expected_overrun_percentage, 1),
        "expected_overrun_amount": round(expected_overrun_amount, 2),
        "risk_level": risk_level,
        "total_budget": total_budget,
        "risk_adjusted_budget": round(total_budget + expected_overrun_amount, 2),
        "risk_factors": risk_details,
        "recommendations": generate_budget_risk_recommendations(risk_details)
    }

def predict_scope_creep_risk(assessment_data: dict, assessment_type: str) -> dict:
    """Predict scope creep risk based on assessment data and project type"""

    # Scope creep risk factors by assessment type
    scope_risk_patterns = {
        "general_readiness": {
            "high_risk_factors": ["change_management_maturity", "stakeholder_engagement"],
            "base_risk": 0.25,
            "typical_scope_additions": ["Additional training", "Extended pilot phase", "More stakeholder sessions"]
        },
        "software_implementation": {
            "high_risk_factors": ["technical_readiness", "change_management_maturity"],
            "base_risk": 0.35,
            "typical_scope_additions": ["Custom integrations", "Additional data migration", "Enhanced training"]
        },
        "business_process": {
            "high_risk_factors": ["change_management_maturity", "communication_effectiveness"],
            "base_risk": 0.30,
            "typical_scope_additions": ["Process redesign", "Additional documentation", "Change management activities"]
        },
        "manufacturing_operations": {
            "high_risk_factors": ["technical_readiness", "workforce_adaptability"],
            "base_risk": 0.40,
            "typical_scope_additions": ["Safety compliance", "Shift coordination", "Operations integration"]
        }
    }

    pattern = scope_risk_patterns.get(assessment_type, scope_risk_patterns["general_readiness"])

    # Calculate scope creep probability
    risk_scores = []
    for factor in pattern["high_risk_factors"]:
        score = assessment_data.get(factor, 3.0)
        risk_scores.append(3.0 - score)  # Higher risk for lower scores

    avg_risk_score = sum(risk_scores) / len(risk_scores)
    scope_creep_probability = (pattern["base_risk"] + avg_risk_score * 0.15) * 100
    scope_creep_probability = max(10, min(70, scope_creep_probability))

    # Determine scope impact
    if scope_creep_probability < 25:
        impact_level = "Low"
        expected_impact = "5-10% additional effort"
    elif scope_creep_probability < 45:
        impact_level = "Medium"
        expected_impact = "10-20% additional effort"
    else:
        impact_level = "High"
        expected_impact = "20-35% additional effort"

    return {
        "scope_creep_probability": round(scope_creep_probability, 1),
        "impact_level": impact_level,
        "expected_impact": expected_impact,
        "high_risk_factors": pattern["high_risk_factors"],
        "factor_scores": {factor: assessment_data.get(factor, 3.0) for factor in pattern["high_risk_factors"]},
        "typical_scope_additions": pattern["typical_scope_additions"],
        "mitigation_strategies": generate_scope_creep_mitigation(pattern["high_risk_factors"], assessment_data)
    }

def predict_timeline_optimization(assessment_data: dict, overall_score: float) -> dict:
    """Predict timeline optimization opportunities based on organizational readiness"""

    # Timeline factors that can accelerate or delay implementation
    timeline_factors = {
        "leadership_support": {
            "acceleration_potential": 0.15,
            "delay_risk": 0.20,
            "impact": "Strong leadership can accelerate decisions and approvals"
        },
        "resource_availability": {
            "acceleration_potential": 0.10,
            "delay_risk": 0.25,
            "impact": "Adequate resources prevent delays and bottlenecks"
        },
        "change_management_maturity": {
            "acceleration_potential": 0.20,
            "delay_risk": 0.30,
            "impact": "High maturity enables faster adoption and fewer iterations"
        },
        "workforce_adaptability": {
            "acceleration_potential": 0.15,
            "delay_risk": 0.15,
            "impact": "Adaptable workforce learns faster and requires less support"
        }
    }

    total_acceleration = 0
    total_delay_risk = 0
    optimization_opportunities = []

    for factor, config in timeline_factors.items():
        score = assessment_data.get(factor, 3.0)

        if score >= 4:
            # High score enables acceleration
            acceleration = config["acceleration_potential"] * (score - 3)
            total_acceleration += acceleration
            optimization_opportunities.append({
                "factor": factor,
                "opportunity": "Acceleration",
                "impact": f"{acceleration:.1%} faster",
                "description": config["impact"]
            })
        elif score < 3:
            # Low score causes delays
            delay = config["delay_risk"] * (3 - score)
            total_delay_risk += delay
            optimization_opportunities.append({
                "factor": factor,
                "opportunity": "Risk Mitigation",
                "impact": f"{delay:.1%} slower without intervention",
                "description": config["impact"]
            })

    # Calculate net timeline impact
    net_timeline_impact = total_acceleration - total_delay_risk

    if net_timeline_impact > 0.10:
        timeline_outlook = "Accelerated"
        expected_timeline = "2-3 weeks faster than standard"
    elif net_timeline_impact > 0:
        timeline_outlook = "Optimized"
        expected_timeline = "On schedule or slightly faster"
    elif net_timeline_impact > -0.10:
        timeline_outlook = "Standard"
        expected_timeline = "Standard 10-week timeline"
    else:
        timeline_outlook = "At Risk"
        expected_timeline = "1-2 weeks additional time may be needed"

    return {
        "timeline_outlook": timeline_outlook,
        "expected_timeline": expected_timeline,
        "net_timeline_impact": round(net_timeline_impact, 2),
        "acceleration_potential": round(total_acceleration, 2),
        "delay_risk": round(total_delay_risk, 2),
        "optimization_opportunities": optimization_opportunities,
        "recommendations": generate_timeline_optimization_recommendations(optimization_opportunities)
    }

def generate_predictive_risk_trending(assessment_data: dict, overall_score: float) -> dict:
    """Generate risk trending analysis for ongoing project monitoring"""

    # Risk categories and their trending patterns
    risk_categories = {
        "Technical Risk": {
            "factors": ["technical_readiness", "resource_availability"],
            "trend_pattern": "Decreases over time with proper preparation",
            "peak_weeks": [4, 5, 7]  # Configuration and data migration weeks
        },
        "Adoption Risk": {
            "factors": ["workforce_adaptability", "change_management_maturity"],
            "trend_pattern": "Increases during training, decreases post go-live",
            "peak_weeks": [6, 8, 9]  # Testing and go-live weeks
        },
        "Stakeholder Risk": {
            "factors": ["leadership_support", "communication_effectiveness"],
            "trend_pattern": "Constant vigilance required throughout project",
            "peak_weeks": [1, 3, 9]  # Kickoff, process review, go-live
        },
        "Resource Risk": {
            "factors": ["resource_availability", "leadership_support"],
            "trend_pattern": "Typically increases toward go-live",
            "peak_weeks": [8, 9, 10]  # Training and go-live weeks
        }
    }

    risk_trends = []

    for category, config in risk_categories.items():
        # Calculate category risk level
        category_scores = [assessment_data.get(factor, 3.0) for factor in config["factors"]]
        category_avg = sum(category_scores) / len(category_scores)

        risk_level = "High" if category_avg < 2.5 else "Medium" if category_avg < 3.5 else "Low"

        risk_trends.append({
            "category": category,
            "current_risk_level": risk_level,
            "factor_scores": {factor: assessment_data.get(factor, 3.0) for factor in config["factors"]},
            "trend_pattern": config["trend_pattern"],
            "peak_weeks": config["peak_weeks"],
            "monitoring_recommendations": generate_risk_monitoring_recommendations(category, risk_level)
        })

    return {
        "overall_risk_score": round(overall_score, 2),
        "risk_trends": risk_trends,
        "critical_monitoring_weeks": list(set([week for trend in risk_trends for week in trend["peak_weeks"]])),
        "early_warning_indicators": generate_early_warning_indicators(risk_trends)
    }

def generate_budget_risk_recommendations(risk_details: List[dict]) -> List[str]:
    """Generate specific recommendations for budget risk mitigation"""
    recommendations = []

    for risk in risk_details:
        if risk["risk_contribution"] > 0.15:
            if risk["factor"] == "leadership_support":
                recommendations.append("Establish executive steering committee with clear decision-making authority")
            elif risk["factor"] == "change_management_maturity":
                recommendations.append("Implement comprehensive change management program with dedicated resources")
            elif risk["factor"] == "resource_availability":
                recommendations.append("Secure dedicated team members and establish contingency resource pool")
            elif risk["factor"] == "communication_effectiveness":
                recommendations.append("Develop robust communication plan with multiple channels and feedback loops")
            elif risk["factor"] == "workforce_adaptability":
                recommendations.append("Invest in early adopter identification and change champion development")

    return recommendations

def generate_scope_creep_mitigation(high_risk_factors: List[str], assessment_data: dict) -> List[str]:
    """Generate specific mitigation strategies for scope creep"""
    strategies = []

    for factor in high_risk_factors:
        score = assessment_data.get(factor, 3.0)
        if score < 3:
            if factor == "change_management_maturity":
                strategies.append("Implement formal change control process with approval gates")
            elif factor == "stakeholder_engagement":
                strategies.append("Establish clear stakeholder roles and communication protocols")
            elif factor == "technical_readiness":
                strategies.append("Conduct thorough technical assessment and establish boundaries")
            elif factor == "communication_effectiveness":
                strategies.append("Create detailed project charter with explicit scope boundaries")

    return strategies

def generate_timeline_optimization_recommendations(opportunities: List[dict]) -> List[str]:
    """Generate timeline optimization recommendations"""
    recommendations = []

    for opp in opportunities:
        if opp["opportunity"] == "Acceleration":
            recommendations.append(f"Leverage {opp['factor']} strength to accelerate project phases")
        elif opp["opportunity"] == "Risk Mitigation":
            recommendations.append(f"Address {opp['factor']} weakness to prevent timeline delays")

    return recommendations

def generate_risk_monitoring_recommendations(category: str, risk_level: str) -> List[str]:
    """Generate risk monitoring recommendations by category"""
    recommendations = []

    if risk_level == "High":
        recommendations.append(f"Implement daily monitoring for {category}")
        recommendations.append(f"Establish escalation procedures for {category}")
    elif risk_level == "Medium":
        recommendations.append(f"Monitor {category} weekly with regular checkpoints")
    else:
        recommendations.append(f"Standard monitoring for {category} is sufficient")

    return recommendations

def generate_early_warning_indicators(risk_trends: List[dict]) -> List[str]:
    """Generate early warning indicators for project monitoring"""
    indicators = []

    for trend in risk_trends:
        if trend["current_risk_level"] == "High":
            indicators.append(f"Monitor {trend['category']} closely during weeks {trend['peak_weeks']}")

    return indicators