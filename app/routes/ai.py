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
    Universal Global Cache + 1-Click Auto-Generation:
    1. Checks the Global Microstash Library FIRST:
       If ANY user has previously requested this book, returns its cards immediately
       with 0s scan time, 0 API tokens, and 0 external calls.
    2. If not found in cache, fetches web descriptions & synthesizes atomic cards via AI.
    3. Permanently indexes the book in the canonical books registry and ideas database
       so that every future user in the community gets instant 0ms access without re-scanning.
    """
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Step 1: Universal Global Cache Lookup
    existing_book = database.find_scanned_book(payload.query)
    if existing_book:
        cached_ideas = database.get_book_ideas(existing_book["id"], existing_book["title"])
        if cached_ideas and len(cached_ideas) > 0:
            stashes = database.get_stashes()
            matching_stash = next((s for s in stashes if existing_book["title"].lower() in s.title.lower() or s.id == f"stash_{existing_book['id']}"), None)
            return {
                "status": "ok",
                "cached": True,
                "global_library_hit": True,
                "book": existing_book,
                "resolved_title": existing_book["title"],
                "resolved_author": existing_book["author"],
                "web_info": {
                    "resolved_title": existing_book["title"],
                    "resolved_author": existing_book["author"],
                    "description": existing_book.get("description", ""),
                },
                "stash_id": matching_stash.id if matching_stash else None,
                "ideas": cached_ideas,
                "count": len(cached_ideas),
                "message": f"Retrieved from Global Microstash Knowledge Base — 0s scan time! Available to all users without re-scanning."
            }

    # Step 2: Not yet in Global Library - Auto-fetch from web and synthesize via AI
    try:
        web_info = auto_fetch_web_info(payload.query)
        description_text = web_info.get("description", "")
        resolved_title = web_info.get("resolved_title", payload.query)
        resolved_author = web_info.get("resolved_author", "Curated Thinker")

        raw_ideas = extract_ideas_from_content(
            input_text=description_text,
            source_title=resolved_title,
            author=resolved_author,
            topic=payload.topic or "Mental Models",
            provider=payload.provider or "gemini",
            num_ideas=payload.num_ideas if payload.num_ideas is not None else 0
        )

        # Step 3: Register globally for all users so it never needs to be scanned twice
        registered = database.register_scanned_book(
            title=resolved_title,
            author=resolved_author,
            description=description_text,
            topic=payload.topic or "Mental Models",
            ideas_list=raw_ideas,
            scanned_by="community"
        )

        return {
            "status": "ok",
            "cached": False,
            "global_library_hit": False,
            "globally_registered": True,
            "book": registered["book"],
            "stash_id": registered["stash_id"],
            "web_info": web_info,
            "ideas": registered["ideas"],
            "count": len(registered["ideas"]),
            "message": "Successfully synthesized and permanently added to Global Microstash Knowledge Base for all users."
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
    Creates a dedicated new Stash named after the book, saves all ideas,
    and registers the book into the canonical books table so all users can access it.
    """
    clean_title = payload.book_title.strip() or "Curated Book"
    clean_author = (payload.author or "Curated Thinker").strip()
    topic = "Mental Models"
    if payload.ideas and payload.ideas[0].get("topic"):
        topic = payload.ideas[0]["topic"]

    # Register into global book registry
    reg_result = database.register_scanned_book(
        title=clean_title,
        author=clean_author,
        description=f"Complete microlearning collection of all core ideas, chapters, and mental models from {clean_title} by {clean_author}.",
        topic=topic,
        ideas_list=payload.ideas,
        scanned_by="community"
    )

    return {
        "status": "ok",
        "stash_id": reg_result["stash_id"],
        "stash_title": f"{clean_title} — Complete Book",
        "book": reg_result["book"],
        "saved_count": reg_result["count"],
        "ideas": reg_result["ideas"],
        "globally_available": True
    }

@router.get("/stress-test/{idea_id}")
def get_socratic_stress_test(idea_id: str):
    """
    Returns a realistic high-stakes scenario dilemma that tests the user's ability
    to correctly apply this specific mental model in real life.
    Uses pre-cached instant dilemmas (<10ms) with dynamic AI fallback.
    """
    import json
    idea = database.get_idea_by_id(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea card not found")

    # 1. Check pre-cached dilemma bank for instant response
    if getattr(idea, "dilemma_cache", None):
        try:
            cached = json.loads(idea.dilemma_cache)
            if isinstance(cached, dict) and "scenario" in cached:
                return {
                    "status": "ok",
                    "idea_id": idea.id,
                    "idea_title": idea.title,
                    "author": idea.author,
                    "stress_test": cached,
                    "cached": True
                }
        except Exception:
            pass

    # 2. Dynamic synthesis fallback
    from app.ai_service import generate_socratic_stress_test
    dilemma = generate_socratic_stress_test(
        title=idea.title,
        summary=idea.summary,
        detailed_explanation=idea.detailed_explanation or "",
        author=idea.author
    )

    # Cache for future calls
    try:
        database.update_idea_dilemma(idea.id, json.dumps(dilemma))
    except Exception:
        pass

    return {
        "status": "ok",
        "idea_id": idea.id,
        "idea_title": idea.title,
        "author": idea.author,
        "stress_test": dilemma,
        "cached": False
    }
