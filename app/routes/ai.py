from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.models import ExtractionRequest, Idea
from app.ai_service import extract_ideas_from_content
from app.web_fetcher import auto_fetch_web_info
from app import database

router = APIRouter(prefix="/api/ai", tags=["AI Extractor"])

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
    """
    Auto-fetches description, author, and summaries from the live web
    (via Firecrawl, Wikipedia, OpenLibrary) given just a book name, author, or idea.
    """
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    web_info = auto_fetch_web_info(payload.query)
    return {"status": "ok", "web_info": web_info}

@router.post("/auto-fetch-and-generate")
def auto_fetch_and_generate(payload: AutoFetchAndGenerateRequest):
    """
    1-Click Auto-Generation:
    1. Fetches descriptions and summaries from the web for the book/author/idea.
    2. Synthesizes atomic microlearning Deepstash cards via NVIDIA NIM / Gemini.
    """
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        # Step 1: Auto-fetch description from the web
        web_info = auto_fetch_web_info(payload.query)
        description_text = web_info.get("description", "")
        resolved_title = web_info.get("resolved_title", payload.query)
        resolved_author = web_info.get("resolved_author", "Curated Thinker")

        # Step 2: Feed auto-fetched web text to AI synthesis engine
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
    """
    Deconstructs text, article URL, or book excerpt into atomic Deepstash idea cards.
    Powered by NVIDIA NIM / Gemini APIs.
    """
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
    """Saves generated ideas into the database and optionally assigns them to a stash."""
    created_ideas = []
    for item in payload.ideas:
        idea = database.create_idea(item)
        created_ideas.append(idea)
        if payload.stash_id:
            database.add_idea_to_stash(payload.stash_id, idea.id)

    return {"status": "ok", "saved_count": len(created_ideas), "ideas": created_ideas}

@router.post("/save-as-book-stash")
def save_as_book_stash(payload: SaveAsBookStashRequest):
    """
    Creates a dedicated new Stash named after the book and saves all ideas into it.
    """
    clean_title = payload.book_title.strip() or "Curated Book"
    stash_title = f"{clean_title} — Complete Book"
    description = f"Complete microlearning collection of all core ideas, chapters, and mental models from {clean_title} by {payload.author}."
    
    # 1. Create the new stash
    stash = database.create_stash(
        title=stash_title,
        description=description,
        icon=payload.icon or "book-open",
        color=payload.color or "indigo"
    )

    # 2. Save each idea and assign to the new stash
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


@router.get("/stress-test/{idea_id}")
def get_socratic_stress_test(idea_id: str):
    """
    Synthesizes a realistic high-stakes scenario dilemma that tests the user's ability
    to correctly apply this specific mental model in real life.
    """
    idea = database.get_idea_by_id(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea card not found")

    from app.ai_service import generate_socratic_stress_test
    dilemma = generate_socratic_stress_test(
        title=idea.title,
        summary=idea.summary,
        detailed_explanation=idea.detailed_explanation or "",
        author=idea.author
    )

    return {
        "status": "ok",
        "idea_id": idea.id,
        "idea_title": idea.title,
        "author": idea.author,
        "stress_test": dilemma
    }
