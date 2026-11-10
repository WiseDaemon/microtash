from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from app.models import Book, BookDetail, Idea
from app import database

router = APIRouter(prefix="/api/books", tags=["Books Library"])

@router.get("", response_model=List[Book])
def list_books(
    topic: Optional[str] = Query(None, description="Filter by topic/genre"),
    search: Optional[str] = Query(None, description="Search keyword in title, author, or description")
):
    """
    Lists all books globally scanned and indexed across all user requests.
    Cards are instantly available with zero scan latency.
    """
    return database.list_scanned_books(topic=topic, search=search)

@router.get("/lookup")
def lookup_book(query: str = Query(..., description="Book title, author, or keywords")):
    """
    Checks if a book has already been scanned into the Universal Global Library.
    """
    book = database.find_scanned_book(query)
    if not book:
        return {"status": "not_found", "cached": False, "query": query}
    
    ideas = database.get_book_ideas(book["id"], book["title"])
    return {
        "status": "ok",
        "cached": True,
        "book": book,
        "ideas_count": len(ideas)
    }

@router.get("/{book_slug}", response_model=BookDetail)
def get_book_detail(book_slug: str):
    """
    Returns full details for a scanned book, including all its pre-decomposed atomic cards.
    """
    book = database.get_book_by_slug(book_slug)
    if not book:
        # Try fallback find
        book = database.find_scanned_book(book_slug)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found in community library")

    ideas = database.get_book_ideas(book["id"], book["title"])
    stashes = database.get_stashes()
    matching_stash = next((s for s in stashes if book["title"].lower() in s.title.lower() or s.id == f"stash_{book['id']}"), None)

    return BookDetail(
        **book,
        ideas=ideas,
        stash_id=matching_stash.id if matching_stash else None
    )

@router.get("/{book_slug}/ideas", response_model=List[Idea])
def get_book_ideas_only(book_slug: str):
    """
    Returns all atomic idea cards for a specific book.
    """
    book = database.get_book_by_slug(book_slug)
    if not book:
        book = database.find_scanned_book(book_slug)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

    return database.get_book_ideas(book["id"], book["title"])
