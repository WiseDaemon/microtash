from pydantic import BaseModel, Field
from typing import List, Optional, Any, Union
from datetime import datetime

class IdeaBase(BaseModel):
    title: str = Field(..., description="The core thesis or headline concept")
    one_liner: str = Field(..., description="Bold, punchy memorable hook")
    summary: str = Field(..., description="Concise microlearning explanation (1-2 paragraphs)")
    detailed_explanation: Optional[str] = Field(None, description="In-depth conceptual breakdown explaining how and why it works")
    example: Optional[str] = Field(None, description="Concrete real-world case study or story showing the concept in action")
    visual_diagram: Optional[str] = Field(None, description="Mermaid.js diagram syntax or conceptual visual architecture flow")
    quote: Optional[str] = Field(None, description="Inspiring quote or key takeaway statement")
    action_item: Optional[str] = Field(None, description="Practical 'Try it today' action step")
    author: str = Field(..., description="Original thinker, author, or speaker")
    source: str = Field(..., description="Book title, article, or podcast name")
    topic: str = Field("Mental Models", description="Primary category/topic")
    tags: List[str] = Field(default_factory=list, description="Sub-topics or keywords")
    read_time_mins: int = Field(1, description="Estimated microlearning read time in minutes")

class IdeaCreate(IdeaBase):
    pass

class Idea(IdeaBase):
    id: str
    created_at: str
    likes: int = 0
    saved_count: int = 0
    is_liked: bool = False
    is_saved: bool = False
    color_theme: Optional[str] = "indigo"  # indigo, emerald, amber, rose, sky, purple, teal
    leitner_box: int = 1
    next_review_date: Optional[str] = None
    last_reviewed_date: Optional[str] = None

class LeitnerReviewRequest(BaseModel):
    grade: Any = Field("good", description="'hard', 'good', 'easy' or 1-5")

class StashBase(BaseModel):
    title: str
    description: str
    icon: str = "sparkles"
    color: str = "indigo"

class StashCreate(StashBase):
    pass

class Stash(StashBase):
    id: str
    created_at: str
    idea_ids: List[str] = Field(default_factory=list)
    ideas_count: int = 0

class ExtractionRequest(BaseModel):
    input_text: str = Field(..., description="Text, article excerpt, transcript, or topic to summarize")
    source_title: Optional[str] = Field("Unknown Source", description="Title or book name")
    author: Optional[str] = Field("Unknown Author", description="Author or speaker")
    topic: Optional[str] = Field("Mental Models", description="Category tag")
    provider: Optional[str] = Field("gemini", description="'gemini' or 'nvidia'")
    num_ideas: Optional[int] = Field(0, description="0 for all ideas in book, or specific count")

class UserProgress(BaseModel):
    streak_days: int = 1
    last_active_date: str = ""
    ideas_read_count: int = 0
    doomscroll_mins_saved: int = 0
    stashes_count: int = 0
    favorites_count: int = 0
