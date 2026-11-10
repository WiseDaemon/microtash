from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.models import ExtractionRequest, Idea
from app.ai_service import extract_ideas_from_content
from app.web_fetcher import auto_fetch_web_info
from app import database

router = APIRouter()

class SaveExtractedBatch(BaseModel):
    ideas: List[Dict[str, Any]]
    stash_id: Optional[str] = None

class AutoFetchRequest(BaseModel):
    query: str = Field(..., description="Book title, author name, or concept/idea")

class AutoFetchAndGenerateRequest(BaseModel):
    query: str = Field(..., description="Book title, author name, or concept/idea")
    provider: Optional[str] = Field("gemini", description="'gemini' or 'nvidia'")
    num_ideas: Optional[int] = Field(0, description="0 for ALL ideas in the book, or positive integer for specific count")
    topic: Optional[str] = Field("Mental Models", description="Preferred category/topic")

class SaveAsBookStashRequest(BaseModel):
    ideas: List[Dict[str, Any]]
    book_title: str
    author: Optional[str] = "Curated Author"
    color: Optional[str] = "indigo"
    icon: Optional[str] = "book-open"

@router.post("/auto-fetch")
def auto_fetch_info(payload: AutoFetchRequest):
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    web_info = auto_fetch_web_info(payload.query)
    return {"status": "ok", "web_info": web_info}

@router.post("/auto-fetch-and-generate")
def auto_fetch_and_generate(payload: AutoFetchAndGenerateRequest):
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        web_info = auto_fetch_web_info(payload.query)
        description_text = web_info.get("description", "")
        resolved_title = web_info.get("resolved_title", payload.query)
        resolved_author = web_info.get("resolved_author", "Curated Thinker")

        ideas = extract_ideas_from_content(
            input_text=description_text,
            source_title=resolved_title,
            author=resolved_author,
            topic=payload.topic or "Mental Models",
            provider=payload.provider or "gemini",
            num_ideas=payload.num_ideas if payload.num_ideas is not None else 0
        )

        return {
            "status": "ok",
            "web_info": web_info,
            "ideas": ideas,
            "count": len(ideas)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-fetch and generation failed: {str(e)}")

@router.post("/extract")
def extract_microlearning(request: ExtractionRequest):
    if not request.input_text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty")

    try:
        ideas = extract_ideas_from_content(
            input_text=request.input_text,
            source_title=request.source_title or "Extracted Summary",
            author=request.author or "Curated Author",
            topic=request.topic or "Mental Models",
            provider=request.provider or "gemini",
            num_ideas=request.num_ideas or 3
        )
        return {"status": "ok", "count": len(ideas), "ideas": ideas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI extraction error: {str(e)}")

@router.post("/save-batch")
def save_extracted_batch(payload: SaveExtractedBatch):
    created_ideas = []
    for item in payload.ideas:
        idea = database.create_idea(item)
        created_ideas.append(idea)
        if payload.stash_id:
            database.add_idea_to_stash(payload.stash_id, idea.id)

    return {"status": "ok", "saved_count": len(created_ideas), "ideas": created_ideas}

@router.post("/save-as-book-stash")
def save_as_book_stash(payload: SaveAsBookStashRequest):
    clean_title = payload.book_title.strip() or "Curated Book"
    stash_title = f"{clean_title} — Complete Book"
    description = f"Complete microlearning collection of all core ideas, chapters, and mental models from {clean_title} by {payload.author}."
    
    stash = database.create_stash(
        title=stash_title,
        description=description,
        icon=payload.icon or "book-open",
        color=payload.color or "indigo"
    )

    created_ideas = []
    for item in payload.ideas:
        idea = database.create_idea(item)
        database.add_idea_to_stash(stash.id, idea.id)
        created_ideas.append(idea)

    return {
        "status": "ok",
        "stash_id": stash.id,
        "stash_title": stash_title,
        "saved_count": len(created_ideas),
        "ideas": created_ideas
    }
