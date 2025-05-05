from fastapi import APIRouter, HTTPException
from typing import List, Dict
from app.services.articles import fetch_latest_articles

router = APIRouter(prefix="/articles", tags=["articles"])

@router.get("/latest", response_model=List[Dict[str, str]])
async def get_latest_articles():
    try:
        return await fetch_latest_articles()
    except RuntimeError as e:
        # Surface our more detailed errors as 502
        raise HTTPException(status_code=502, detail=str(e))
