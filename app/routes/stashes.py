from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from app.models import Stash, StashCreate, SharedStashDetail
from app import database
from app.auth import get_optional_user

router = APIRouter(prefix="/api/stashes", tags=["Stashes"])

@router.get("", response_model=List[Stash])
def list_stashes(user: Optional[Dict[str, Any]] = Depends(get_optional_user)):
    user_id = user["id"] if user else None
    return database.get_stashes(owner_user_id=user_id)

@router.get("/public", response_model=List[Stash])
def list_community_stashes(search: Optional[str] = Query(None, description="Search public stashes")):
    """
    Lists all public community stashes curated and shared by learners.
    """
    return database.list_public_stashes(search=search)

@router.get("/share/{share_slug_or_id}")
def get_shared_stash_detail(share_slug_or_id: str):
    """
    Public social learning endpoint to view a shared stash and its ideas without logging in.
    """
    stash = database.get_stash_by_id(share_slug_or_id)
    if not stash:
        raise HTTPException(status_code=404, detail="Shared stash not found")
    if not stash.get("is_public", True):
        raise HTTPException(status_code=403, detail="This stash is private")
    return stash

@router.get("/{stash_id}")
def get_stash(stash_id: str):
    stash = database.get_stash_by_id(stash_id)
    if not stash:
        raise HTTPException(status_code=404, detail="Stash not found")
    return stash

@router.post("", response_model=Stash)
def create_stash(payload: StashCreate, user: Optional[Dict[str, Any]] = Depends(get_optional_user)):
    owner_id = user["id"] if user else "community"
    return database.create_stash(
        title=payload.title,
        description=payload.description,
        icon=payload.icon,
        color=payload.color,
        owner_user_id=owner_id,
        is_public=payload.is_public
    )

@router.post("/{stash_id}/publish")
def publish_stash(stash_id: str, payload: Optional[Dict[str, bool]] = None):
    """
    Toggles public community sharing for a stash, generating a public vanity share link.
    """
    is_public = True if payload is None else payload.get("is_public", True)
    updated = database.publish_stash(stash_id, is_public=is_public)
    if not updated:
        raise HTTPException(status_code=404, detail="Stash not found")
    return {
        "status": "ok",
        "stash_id": updated["id"],
        "is_public": updated["is_public"],
        "share_slug": updated["share_slug"],
        "share_path": f"/share/stash/{updated['share_slug']}"
    }

@router.post("/{stash_id}/clone")
def clone_stash_to_library(stash_id: str, user: Optional[Dict[str, Any]] = Depends(get_optional_user)):
    """
    Clones a public shared stash directly into the learner's personal collection.
    """
    owner_id = user["id"] if user else "community"
    cloned = database.clone_stash(stash_id, new_owner_id=owner_id)
    if not cloned:
        raise HTTPException(status_code=404, detail="Source stash not found")
    return {
        "status": "ok",
        "message": "Stash successfully cloned to your collection",
        "cloned_stash": cloned
    }

@router.post("/{stash_id}/ideas")
def add_idea(stash_id: str, payload: Dict[str, str]):
    idea_id = payload.get("idea_id")
    if not idea_id:
        raise HTTPException(status_code=400, detail="Missing idea_id")
    ok = database.add_idea_to_stash(stash_id, idea_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Could not add idea to stash")
    return {"status": "ok", "message": "Idea added to stash"}

@router.delete("/{stash_id}/ideas/{idea_id}")
def remove_idea(stash_id: str, idea_id: str):
    database.remove_idea_from_stash(stash_id, idea_id)
    return {"status": "ok", "message": "Idea removed from stash"}
