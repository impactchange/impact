from fastapi import APIRouter

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/advanced")
async def get_advanced_analytics():
    # Return placeholder data so the dashboard loads
    return {
        "roi_data": [10, 20, 30, 40, 50],
        "risk_heatmap": {"high": 2, "medium": 5, "low": 12},
        "velocity_metrics": {"sprint_1": 25, "sprint_2": 28}
    }
