from fastapi import APIRouter, HTTPException
from db.mongo import db
from schemas.project import Project
from datetime import datetime

router = APIRouter()

@router.post("/create", status_code=201)
async def create_project(project: Project):
    existing = await db.projects.find_one({"name": project.name, "organization": project.organization})
    if existing:
        raise HTTPException(status_code=400, detail="Project with this name already exists")
    doc = project.dict()
    doc.update({
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    result = await db.projects.insert_one(doc)
    return {"message": "Project created", "id": str(result.inserted_id)}

@router.get("/all")
async def list_projects():
    projects = await db.projects.find().to_list(100)
    return projects

@router.get("/{project_id}")
async def get_project(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}/update")
async def update_project(project_id: str, update_data: dict):
    update_data["updated_at"] = datetime.utcnow()
    result = await db.projects.update_one({"id": project_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project updated"}
