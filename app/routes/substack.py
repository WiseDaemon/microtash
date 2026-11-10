from fastapi import APIRouter, HTTPException, Query, Header
from typing import List, Optional, Dict, Any
from app.models import (
    SubstackNote, NoteCreateRequest, IdeaRestackRequest,
    SubstackComment, CommentCreateRequest, SubscriptionRequest, Subscription
)
from app import database

router = APIRouter(prefix="/api/substack", tags=["Substack"])

@router.get("/notes", response_model=List[SubstackNote])
def list_notes(limit: int = Query(50, description="Max notes to return")):
    return database.get_substack_notes(limit=limit)

@router.post("/notes", response_model=SubstackNote)
def create_note(req: NoteCreateRequest):
    data = req.dict()
    return database.create_substack_note(data)

@router.post("/notes/{note_id}/like", response_model=SubstackNote)
def toggle_like_note(note_id: str):
    updated = database.toggle_like_substack_note(note_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated

@router.post("/ideas/{idea_id}/restack", response_model=SubstackNote)
def restack_idea(idea_id: str, req: IdeaRestackRequest):
    note = database.restack_idea_to_notes(
        idea_id=idea_id,
        comment=req.comment,
        author_name=req.author_name or "Curated Thinker",
        author_handle=req.author_handle or "thinker"
    )
    if not note:
        raise HTTPException(status_code=404, detail="Idea not found to restack")
    return note

@router.get("/ideas/{idea_id}/comments", response_model=List[SubstackComment])
def get_idea_comments(idea_id: str):
    return database.get_comments_for_idea(idea_id)

@router.post("/ideas/{idea_id}/comments", response_model=SubstackComment)
def add_idea_comment(idea_id: str, req: CommentCreateRequest, authorization: Optional[str] = Header(None)):
    user_id = "community"
    user_name = req.user_name or "Curated Reader"

    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        session = database.validate_session_token(token)
        if session:
            user_id = session["id"]
            user_name = session["full_name"] or session["username"]

    return database.create_substack_comment(
        idea_id=idea_id,
        user_name=user_name,
        comment_text=req.comment_text,
        user_id=user_id,
        parent_id=req.parent_comment_id
    )

@router.post("/subscribe")
def toggle_subscription(req: SubscriptionRequest, authorization: Optional[str] = Header(None)):
    user_id = "user_demo"
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        session = database.validate_session_token(token)
        if session:
            user_id = session["id"]

    return database.toggle_substack_subscription(
        user_id=user_id,
        target_name=req.target_name,
        target_type=req.target_type,
        target_handle=req.target_handle
    )

@router.get("/subscriptions", response_model=List[Subscription])
def get_subscriptions(authorization: Optional[str] = Header(None)):
    user_id = "user_demo"
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        session = database.validate_session_token(token)
        if session:
            user_id = session["id"]
    return database.get_user_substack_subscriptions(user_id)

@router.get("/publications")
def list_publications():
    return database.get_substack_publications()
