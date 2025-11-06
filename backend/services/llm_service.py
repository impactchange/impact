# backend/services/llm_service.py

from fastapi import HTTPException, status
from core.config import ANTHROPIC_API_KEY
from anthropic import AsyncAnthropic, HUMAN_PROMPT, AI_PROMPT
from datetime import datetime
from typing import Dict, Any

async def generate_customized_playbook(assessment_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generates a customized change management playbook using the Anthropic API."""
    
    if not ANTHROPIC_API_KEY:
         raise HTTPException(status_code=503, detail="LLM service is currently unavailable (API key missing).")

    anthropic_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    # Simplified extraction of necessary data for the prompt
    scores = {
        "leadership_support": assessment_data.get("leadership_support", {}).get("score", 3),
        "resource_availability": assessment_data.get("resource_availability", {}).get("score", 3),
        "change_management_maturity": assessment_data.get("change_management_maturity", {}).get("score", 3),
        "communication_effectiveness": assessment_data.get("communication_effectiveness", {}).get("score", 3),
        "workforce_adaptability": assessment_data.get("workforce_adaptability", {}).get("score", 3)
    }

    prompt = f"""{HUMAN_PROMPT}
    Generate a comprehensive, customized change management playbook for the following organization:

    PROJECT DETAILS:
    - Project Name: {assessment_data.get("project_name", "")}
    - Organization: {assessment_data.get("organization", "")}
    - Assessment Type: {assessment_data.get("assessment_type", "")}
    - Overall Readiness Score: {assessment_data.get("overall_score", 0)}/5
    - Readiness Level: {assessment_data.get("readiness_level", "")}

    ASSESSMENT SCORES (1-5 scale):
    - Leadership Support: {scores["leadership_support"]}/5
    - Resource Availability: {scores["resource_availability"]}/5
    - Change Management Maturity: {scores["change_management_maturity"]}/5
    - Communication Effectiveness: {scores["communication_effectiveness"]}/5
    - Workforce Adaptability: {scores["workforce_adaptability"]}/5

    Please generate a detailed, actionable playbook.
    {AI_PROMPT}
    """

    try:
        response = await anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        playbook_content = response.content[0].text
        return {
            "assessment_id": assessment_data["id"],
            "content": playbook_content,
            "overall_readiness_score": assessment_data.get("overall_score", 0),
            "readiness_level": assessment_data.get("readiness_level", "Unknown"),
            "success_probability": assessment_data.get("success_probability", 0),
            "project_name": assessment_data.get("project_name", "N/A"),
            "generated_at": datetime.utcnow()
        }
    except Exception as e:
        print(f"Anthropic API Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"LLM service failed to generate playbook: {str(e)}")
