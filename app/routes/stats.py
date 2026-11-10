from fastapi import APIRouter
from app.models import UserProgress
from app import database

router = APIRouter(prefix="/api/stats", tags=["Stats"])

@router.get("", response_model=UserProgress)
def get_user_stats():
    return database.get_user_progress()
