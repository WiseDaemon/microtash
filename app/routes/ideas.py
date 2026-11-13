from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models import Idea, IdeaCreate, LeitnerReviewRequest
from app import database

router = APIRouter(prefix="/api/ideas", tags=["Ideas"])

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

    # If already cached with genuine depth and not forced, return cached
    if not force and idea.detailed_explanation and len(idea.detailed_explanation.strip()) >= 150 and idea.detailed_explanation.strip() != idea.summary.strip():
        return idea

    # Synthesize authentic in-depth treatise and case study
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


@router.get("/{idea_id}/export-markdown")
def export_idea_markdown(idea_id: str):
    """
    Exports a single mental model in Obsidian/Notion compatible Markdown,
    complete with YAML frontmatter, Mermaid diagram blocks, and callout quotes.
    """
    idea = database.get_idea_by_id(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    tag_str = ", ".join([f'"{t}"' for t in idea.tags]) if idea.tags else f'"{idea.topic}"'
    visual_diag = idea.visual_diagram or "graph TD\n  Input --> Process --> Output"
    
    md = f"""---
title: "{idea.title}"
author: "{idea.author}"
source: "{idea.source}"
topic: "{idea.topic}"
tags: [{tag_str}]
leitner_box: {idea.leitner_box}
created_at: "{idea.created_at}"
type: "mental-model"
---

# {idea.title}

> [!QUOTE] Core Intuition
> **"{idea.one_liner}"** — *{idea.author}* ({idea.source})

## 📌 Summary
{idea.summary}

## ⚙️ Core Mechanism & First Principles
{idea.detailed_explanation or "Deconstruct problems into their foundational components."}

## 📊 Visual System Architecture
```mermaid
{visual_diag}
```

## 🏢 Real-World Case Study
{idea.example or "In high-stakes operational environments, teams implementing this principle preserved asymmetric upside."}

## ⚡ Try It Today (Action Item)
> [!TIP] Actionable Heuristic
> {idea.action_item or "Identify one high-friction decision today and filter it through this framework."}
"""
    return {"status": "ok", "idea_id": idea.id, "filename": f"{idea.id}.md", "markdown": md}


@router.get("/export/markdown-vault")
def export_all_markdown_vault():
    """
    Exports all mental models as a concatenated Obsidian vault Markdown file.
    """
    ideas = database.get_ideas()
    vault_md = "# Microstash — Personal Mental Model Vault\n\n"
    vault_md += f"Exported: {len(ideas)} high-leverage frameworks and decision models.\n\n---\n\n"

    for idea in ideas:
        vault_md += f"## {idea.title}\n"
        vault_md += f"**Thinker:** {idea.author} | **Source:** *{idea.source}* | **Topic:** `{idea.topic}`\n\n"
        vault_md += f"> \"{idea.one_liner}\"\n\n"
        vault_md += f"### Mechanism\n{idea.summary}\n\n"
        if idea.visual_diagram:
            vault_md += f"```mermaid\n{idea.visual_diagram}\n```\n\n"
        if idea.example:
            vault_md += f"### Case Study\n{idea.example}\n\n"
        if idea.action_item:
            vault_md += f"**Action Rule:** {idea.action_item}\n\n"
        vault_md += "---\n\n"

    return {"status": "ok", "total_count": len(ideas), "markdown": vault_md}
