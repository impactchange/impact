# backend/services/assessment_utils.py (CLEANED)

from db.mongo import db
from fastapi import HTTPException, status
from typing import List, Dict, Any
import uuid

async def get_assessment_document(assessment_id: str, user_id: str) -> Dict[str, Any]:
    """Retrieves an assessment document by ID, ensuring user ownership."""
    assessment = await db.assessments.find_one({"id": assessment_id, "user_id": user_id})
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found or you do not have access")
    
    assessment.pop("_id", None)
    return assessment

async def get_all_user_assessments_data(user_id: str) -> List[Dict[str, Any]]:
    """Retrieves all assessments for a given user, cleaning up MongoDB fields."""
    assessments_cursor = db.assessments.find({"user_id": user_id})
    assessments = await assessments_cursor.to_list(100)
    
    for assessment in assessments:
        assessment.pop("_id", None)
    
    return assessments

async def insert_new_assessment(assessment_doc: Dict[str, Any]):
    """Inserts the final assessment document into the database."""
    assessment_doc['id'] = assessment_doc.get('id', str(uuid.uuid4()))
    result = await db.assessments.insert_one(assessment_doc)
    return str(result.inserted_id)
