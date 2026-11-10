from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models import Idea, IdeaCreate, LeitnerReviewRequest
from app import database

router = APIRouter()

@router.get("", response_model=List[Idea])
def list_ideas(
    topic: Optional[str] = Query(None, description="Filter by topic tag"),
    search: Optional[str] = Query(None, description="Search keyword in title, summary, author"),
    saved_only: Optional[bool] = Query(None, description="Filter only favorited/saved cards")
):
    return database.get_ideas(topic=topic, search=search, is_saved=saved_only)

@router.get("/leitner/due", response_model=List[Idea])
def list_due_leitner_ideas(limit: int = Query(20, description="Max cards to review")):
    return database.get_due_leitner_ideas(limit=limit)

@router.get("/{idea_id}", response_model=Idea)
def get_idea(idea_id: str):
    idea = database.get_idea_by_id(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea

@router.post("/{idea_id}/leitner-review", response_model=Idea)
def submit_leitner_review(idea_id: str, review_in: LeitnerReviewRequest):
    updated = database.record_leitner_review(idea_id, review_in.grade)
    if not updated:
        raise HTTPException(status_code=404, detail="Idea not found")
    return updated

@router.post("", response_model=Idea)
def create_idea(idea_in: IdeaCreate):
    return database.create_idea(idea_in.dict())

@router.post("/{idea_id}/like", response_model=Idea)
def toggle_like(idea_id: str):
    idea = database.toggle_like_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea

@router.post("/{idea_id}/save", response_model=Idea)
def toggle_save(idea_id: str):
    idea = database.toggle_save_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea

@router.post("/{idea_id}/read")
def mark_read(idea_id: str):
    progress = database.record_idea_read(idea_id)
    return {"status": "ok", "progress": progress}

@router.post("/{idea_id}/deep-dive", response_model=Idea)
def get_or_generate_deep_dive(idea_id: str, force: bool = Query(False, description="Force regeneration")):
    idea = database.get_idea_by_id(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    if not force and idea.detailed_explanation and len(idea.detailed_explanation.strip()) >= 150 and idea.detailed_explanation.strip() != idea.summary.strip():
        return idea

    from app.ai_service import generate_concept_deep_dive
    res = generate_concept_deep_dive(
        title=idea.title,
        author=idea.author,
        source=idea.source,
        one_liner=idea.one_liner,
        summary=idea.summary
    )

    if res.get("detailed_explanation"):
        updated = database.update_idea_details(
            idea_id=idea_id,
            detailed_explanation=res["detailed_explanation"],
            example=res.get("example") or idea.example or "",
            visual_diagram=res.get("visual_diagram") or idea.visual_diagram or ""
        )
        if updated:
            return updated

    return idea
