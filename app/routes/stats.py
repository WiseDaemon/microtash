from fastapi import APIRouter
from app.database import get_user_progress
from app.models import UserProgress

router = APIRouter()

@router.get("", response_model=UserProgress)
async def get_stats():
    return get_user_progress()
