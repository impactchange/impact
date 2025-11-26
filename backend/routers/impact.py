from fastapi import APIRouter

router = APIRouter(prefix="/api/impact", tags=["Impact"])

@router.get("/phases")
async def get_impact_phases():
    # Return the standard IMPACT phases
    return [
        {"id": "phase_1", "name": "Identification", "order": 1},
        {"id": "phase_2", "name": "Model", "order": 2},
        {"id": "phase_3", "name": "Proof of Value", "order": 3},
        {"id": "phase_4", "name": "Adopt", "order": 4},
        {"id": "phase_5", "name": "Control", "order": 5},
        {"id": "phase_6", "name": "Target", "order": 6}
    ]
