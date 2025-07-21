from typing import Dict, Any
from data.constants import ASSESSMENT_TYPES

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
