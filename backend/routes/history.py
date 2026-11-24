from fastapi import APIRouter, HTTPException
from backend import crud

router = APIRouter(prefix="/history", tags=["History"])

@router.get("")
async def get_analysis_history(limit: int = 50):
    """Returns past traffic analysis records with summary statistics."""
    records = crud.list_analyses(limit=limit)
    return {"analyses": records}

@router.delete("/{analysis_id}")
async def delete_analysis_record(analysis_id: str):
    """Deletes an analysis record."""
    success = crud.delete_analysis(analysis_id)
    if not success:
        raise HTTPException(status_code=404, detail="Analysis record not found")
    return {"message": "Analysis record deleted successfully"}
