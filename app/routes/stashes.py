from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.models import Stash, StashCreate
from app import database

router = APIRouter()

@router.get("", response_model=List[Stash])
def list_stashes():
    return database.get_stashes()

@router.get("/{stash_id}")
def get_stash(stash_id: str):
    stash = database.get_stash_by_id(stash_id)
    if not stash:
        raise HTTPException(status_code=404, detail="Stash not found")
    return stash

@router.post("", response_model=Stash)
def create_stash(payload: StashCreate):
    return database.create_stash(
        title=payload.title,
        description=payload.description,
        icon=payload.icon,
        color=payload.color
    )

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
