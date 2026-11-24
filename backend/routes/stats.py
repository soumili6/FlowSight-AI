from fastapi import APIRouter
from backend import crud

router = APIRouter(prefix="/stats", tags=["Dashboard Statistics"])

@router.get("/dashboard")
async def get_dashboard_summary():
    """Aggregates high-level metrics for dashboard cards and category distribution."""
    stats = crud.get_dashboard_stats()
    return stats
