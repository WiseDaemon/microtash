import os
import sqlite3
import json
import uuid
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from app.config import settings
from app.models import Idea, Stash, UserProgress
from app.seed_data import DEFAULT_IDEAS, DEFAULT_STASHES

def get_connection():
    os.makedirs(os.path.dirname(settings.DB_PATH), exist_ok=True)
    conn = sqlite3.connect(settings.DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Ideas table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ideas (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        one_liner TEXT NOT NULL,
        summary TEXT NOT NULL,
        detailed_explanation TEXT,
        example TEXT,
        visual_diagram TEXT,
        quote TEXT,
        action_item TEXT,
        author TEXT NOT NULL,
        source TEXT NOT NULL,
        topic TEXT NOT NULL,
        tags TEXT NOT NULL, -- JSON array
        read_time_mins INTEGER DEFAULT 1,
        color_theme TEXT DEFAULT 'indigo',
        likes INTEGER DEFAULT 0,
        saved_count INTEGER DEFAULT 0,
        is_liked INTEGER DEFAULT 0,
        is_saved INTEGER DEFAULT 0,
        leitner_box INTEGER DEFAULT 1,
        next_review_date TEXT,
        last_reviewed_date TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # Ensure schema upgrades for existing DB files
    try:
        cursor.execute("ALTER TABLE ideas ADD COLUMN detailed_explanation TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE ideas ADD COLUMN example TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE ideas ADD COLUMN visual_diagram TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE ideas ADD COLUMN leitner_box INTEGER DEFAULT 1")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE ideas ADD COLUMN next_review_date TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE ideas ADD COLUMN last_reviewed_date TEXT")
    except Exception:
        pass

    # Stashes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stashes (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        icon TEXT DEFAULT 'sparkles',
        color TEXT DEFAULT 'indigo',
        created_at TEXT NOT NULL
    );
    """)

    # Stash-Idea join table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stash_ideas (
        stash_id TEXT NOT NULL,
        idea_id TEXT NOT NULL,
        added_at TEXT NOT NULL,
        PRIMARY KEY (stash_id, idea_id),
        FOREIGN KEY (stash_id) REFERENCES stashes(id) ON DELETE CASCADE,
        FOREIGN KEY (idea_id) REFERENCES ideas(id) ON DELETE CASCADE
    );
    """)

    # User progress & gamification table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_progress (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        streak_days INTEGER DEFAULT 1,
        last_active_date TEXT,
        ideas_read_count INTEGER DEFAULT 0,
        doomscroll_mins_saved INTEGER DEFAULT 0
    );
    """)

    # Ideas read history log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS read_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        idea_id TEXT NOT NULL,
        read_date TEXT NOT NULL
    );
    """)

    # Performance & Spaced Repetition Indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ideas_topic ON ideas(topic);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ideas_leitner ON ideas(next_review_date, leitner_box);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ideas_created ON ideas(created_at DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_stash_ideas_stash ON stash_ideas(stash_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_stash_ideas_idea ON stash_ideas(idea_id);")

    conn.commit()

    # Initialize progress row if absent
    cursor.execute("SELECT id FROM user_progress WHERE id = 1")
    if not cursor.fetchone():
        today_str = date.today().isoformat()
        cursor.execute("""
            INSERT INTO user_progress (id, streak_days, last_active_date, ideas_read_count, doomscroll_mins_saved)
            VALUES (1, 1, ?, 0, 0)
        """, (today_str,))
        conn.commit()

    # Seed data if empty, or sync rich detailed explanations & examples
    cursor.execute("SELECT COUNT(*) FROM ideas")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_data(conn)
    else:
        # Sync rich detailed explanations, examples and visual diagrams to existing seed records
        for i in DEFAULT_IDEAS:
            cursor.execute("""
                UPDATE ideas
                SET detailed_explanation = ?, example = ?, visual_diagram = ?
                WHERE id = ? AND (detailed_explanation IS NULL OR detailed_explanation = '' OR example IS NULL OR example = '' OR visual_diagram IS NULL OR visual_diagram = '')
            """, (i.get("detailed_explanation", ""), i.get("example", ""), i.get("visual_diagram", ""), i["id"]))
        conn.commit()

        # Backfill any remaining ideas that lack visual diagrams
        cursor.execute("SELECT id, title, summary, topic, visual_diagram FROM ideas WHERE visual_diagram IS NULL OR visual_diagram = ''")
        missing_diags = cursor.fetchall()
        if missing_diags:
            from app.ai_service import generate_default_mermaid_diagram
            for row in missing_diags:
                diag = generate_default_mermaid_diagram(row["title"], row["summary"], row["topic"] or "Mental Models")
                cursor.execute("UPDATE ideas SET visual_diagram = ? WHERE id = ?", (diag, row["id"]))
            conn.commit()

        # Initialize Leitner review dates for cards with no review date
        today_iso = date.today().isoformat()
        cursor.execute("UPDATE ideas SET next_review_date = ? WHERE next_review_date IS NULL OR next_review_date = ''", (today_iso,))
        cursor.execute("UPDATE ideas SET leitner_box = 1 WHERE leitner_box IS NULL OR leitner_box < 1")
        conn.commit()

    conn.close()

def seed_data(conn):
    cursor = conn.cursor()
    now_str = datetime.utcnow().isoformat()

    # Seed stashes
    for s in DEFAULT_STASHES:
        cursor.execute("""
            INSERT OR IGNORE INTO stashes (id, title, description, icon, color, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (s["id"], s["title"], s["description"], s.get("icon", "sparkles"), s.get("color", "indigo"), now_str))

    # Seed ideas
    for i in DEFAULT_IDEAS:
        cursor.execute("""
            INSERT OR IGNORE INTO ideas (
                id, title, one_liner, summary, detailed_explanation, example, visual_diagram, quote, action_item, author, source, topic,
                tags, read_time_mins, color_theme, likes, saved_count, is_liked, is_saved, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?)
        """, (
            i["id"], i["title"], i["one_liner"], i["summary"],
            i.get("detailed_explanation", ""), i.get("example", ""), i.get("visual_diagram", ""),
            i.get("quote", ""), i.get("action_item", ""), i["author"], i["source"], i["topic"],
            json.dumps(i.get("tags", [])), i.get("read_time_mins", 1),
            i.get("color_theme", "indigo"), i.get("likes", 0), i.get("saved_count", 0), now_str
        ))
        # Update existing records with detailed_explanation, example & visual_diagram if empty
        cursor.execute("""
            UPDATE ideas
            SET detailed_explanation = ?, example = ?, visual_diagram = ?
            WHERE id = ? AND (detailed_explanation IS NULL OR detailed_explanation = '' OR visual_diagram IS NULL OR visual_diagram = '')
        """, (i.get("detailed_explanation", ""), i.get("example", ""), i.get("visual_diagram", ""), i["id"]))

        # Assign to appropriate default stashes
        if i["topic"] == "Mental Models":
            cursor.execute("INSERT OR IGNORE INTO stash_ideas (stash_id, idea_id, added_at) VALUES (?, ?, ?)",
                           ("stash_mental_models", i["id"], now_str))
        elif i["topic"] == "Productivity":
            cursor.execute("INSERT OR IGNORE INTO stash_ideas (stash_id, idea_id, added_at) VALUES (?, ?, ?)",
                           ("stash_habits_productivity", i["id"], now_str))
        elif i["topic"] == "Stoicism":
            cursor.execute("INSERT OR IGNORE INTO stash_ideas (stash_id, idea_id, added_at) VALUES (?, ?, ?)",
                           ("stash_stoic_armor", i["id"], now_str))
        elif i["topic"] == "Wealth":
            cursor.execute("INSERT OR IGNORE INTO stash_ideas (stash_id, idea_id, added_at) VALUES (?, ?, ?)",
                           ("stash_wealth_psychology", i["id"], now_str))

    conn.commit()

# --- Idea Operations ---

def get_ideas(topic: Optional[str] = None, search: Optional[str] = None, is_saved: Optional[bool] = None) -> List[Idea]:
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM ideas WHERE 1=1"
    params = []

    if topic and topic.lower() != "all":
        query += " AND LOWER(topic) = LOWER(?)"
        params.append(topic)

    if is_saved is not None and is_saved:
        query += " AND is_saved = 1"

    if search:
        search_pattern = f"%{search.lower()}%"
        query += " AND (LOWER(title) LIKE ? OR LOWER(one_liner) LIKE ? OR LOWER(summary) LIKE ? OR LOWER(author) LIKE ? OR LOWER(source) LIKE ? OR LOWER(tags) LIKE ?)"
        params.extend([search_pattern] * 6)

    query += " ORDER BY rowid DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    ideas = []
    for r in rows:
        ideas.append(row_to_idea(r))
    conn.close()
    return ideas

def get_idea_by_id(idea_id: str) -> Optional[Idea]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ideas WHERE id = ?", (idea_id,))
    row = cursor.fetchone()
    conn.close()
    return row_to_idea(row) if row else None

def create_idea(data: Dict[str, Any]) -> Idea:
    conn = get_connection()
    cursor = conn.cursor()
    idea_id = data.get("id") or f"idea_{uuid.uuid4().hex[:8]}"
    created_at = datetime.utcnow().isoformat()
    tags_json = json.dumps(data.get("tags", []))
    
    cursor.execute("""
        INSERT INTO ideas (
            id, title, one_liner, summary, detailed_explanation, example, visual_diagram, quote, action_item, author, source, topic,
            tags, read_time_mins, color_theme, likes, saved_count, is_liked, is_saved, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0, ?)
    """, (
        idea_id, data["title"], data["one_liner"], data["summary"],
        data.get("detailed_explanation", ""), data.get("example", ""), data.get("visual_diagram", ""),
        data.get("quote"), data.get("action_item"), data["author"], data["source"], data.get("topic", "General"),
        tags_json, data.get("read_time_mins", 1), data.get("color_theme", "indigo"), created_at
    ))
    conn.commit()
    conn.close()
    return get_idea_by_id(idea_id)

def toggle_like_idea(idea_id: str) -> Optional[Idea]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_liked, likes FROM ideas WHERE id = ?", (idea_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    
    current_liked = bool(row["is_liked"])
    new_liked = not current_liked
    new_likes = row["likes"] + (1 if new_liked else -1)
    if new_likes < 0:
        new_likes = 0
        
    cursor.execute("UPDATE ideas SET is_liked = ?, likes = ? WHERE id = ?", (int(new_liked), new_likes, idea_id))
    conn.commit()
    conn.close()
    return get_idea_by_id(idea_id)

def toggle_save_idea(idea_id: str) -> Optional[Idea]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_saved, saved_count FROM ideas WHERE id = ?", (idea_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    current_saved = bool(row["is_saved"])
    new_saved = not current_saved
    new_saved_count = row["saved_count"] + (1 if new_saved else -1)
    if new_saved_count < 0:
        new_saved_count = 0

    cursor.execute("UPDATE ideas SET is_saved = ?, saved_count = ? WHERE id = ?", (int(new_saved), new_saved_count, idea_id))
    conn.commit()
    conn.close()
    return get_idea_by_id(idea_id)

def update_idea_details(idea_id: str, detailed_explanation: str, example: str, visual_diagram: str = "") -> Optional[Idea]:
    conn = get_connection()
    cursor = conn.cursor()
    if visual_diagram:
        cursor.execute("""
            UPDATE ideas
            SET detailed_explanation = ?, example = ?, visual_diagram = ?
            WHERE id = ?
        """, (detailed_explanation, example, visual_diagram, idea_id))
    else:
        cursor.execute("""
            UPDATE ideas
            SET detailed_explanation = ?, example = ?
            WHERE id = ?
        """, (detailed_explanation, example, idea_id))
    conn.commit()
    conn.close()
    return get_idea_by_id(idea_id)

# --- Stash Operations ---

def get_stashes() -> List[Stash]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stashes ORDER BY rowid ASC")
    rows = cursor.fetchall()
    stashes = []
    for r in rows:
        stash_id = r["id"]
        cursor.execute("SELECT idea_id FROM stash_ideas WHERE stash_id = ?", (stash_id,))
        idea_ids = [row["idea_id"] for row in cursor.fetchall()]
        stashes.append(Stash(
            id=stash_id,
            title=r["title"],
            description=r["description"],
            icon=r["icon"],
            color=r["color"],
            created_at=r["created_at"],
            idea_ids=idea_ids,
            ideas_count=len(idea_ids)
        ))
    conn.close()
    return stashes

def get_stash_by_id(stash_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stashes WHERE id = ?", (stash_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    cursor.execute("""
        SELECT i.* FROM ideas i
        JOIN stash_ideas si ON i.id = si.idea_id
        WHERE si.stash_id = ?
        ORDER BY si.added_at DESC
    """, (stash_id,))
    idea_rows = cursor.fetchall()
    ideas = [row_to_idea(ir) for ir in idea_rows]
    
    stash_data = {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "icon": row["icon"],
        "color": row["color"],
        "created_at": row["created_at"],
        "ideas": ideas,
        "ideas_count": len(ideas)
    }
    conn.close()
    return stash_data

def create_stash(title: str, description: str, icon: str = "sparkles", color: str = "indigo") -> Stash:
    conn = get_connection()
    cursor = conn.cursor()
    stash_id = f"stash_{uuid.uuid4().hex[:8]}"
    created_at = datetime.utcnow().isoformat()
    cursor.execute("""
        INSERT INTO stashes (id, title, description, icon, color, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (stash_id, title, description, icon, color, created_at))
    conn.commit()
    conn.close()
    return Stash(
        id=stash_id,
        title=title,
        description=description,
        icon=icon,
        color=color,
        created_at=created_at,
        idea_ids=[],
        ideas_count=0
    )

def add_idea_to_stash(stash_id: str, idea_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.utcnow().isoformat()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO stash_ideas (stash_id, idea_id, added_at)
            VALUES (?, ?, ?)
        """, (stash_id, idea_id, now_str))
        # Also mark as saved
        cursor.execute("UPDATE ideas SET is_saved = 1, saved_count = saved_count + 1 WHERE id = ?", (idea_id,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def remove_idea_from_stash(stash_id: str, idea_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM stash_ideas WHERE stash_id = ? AND idea_id = ?", (stash_id, idea_id))
    conn.commit()
    conn.close()
    return True

# --- User Progress & Gamification ---

def get_user_progress() -> UserProgress:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_progress WHERE id = 1")
    row = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) FROM stashes")
    stashes_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ideas WHERE is_saved = 1")
    favorites_count = cursor.fetchone()[0]

    conn.close()

    if not row:
        return UserProgress(stashes_count=stashes_count, favorites_count=favorites_count)

    return UserProgress(
        streak_days=row["streak_days"],
        last_active_date=row["last_active_date"] or "",
        ideas_read_count=row["ideas_read_count"],
        doomscroll_mins_saved=row["doomscroll_mins_saved"],
        stashes_count=stashes_count,
        favorites_count=favorites_count
    )

def record_idea_read(idea_id: str) -> UserProgress:
    conn = get_connection()
    cursor = conn.cursor()
    today_str = date.today().isoformat()

    # Record read log
    cursor.execute("INSERT INTO read_history (idea_id, read_date) VALUES (?, ?)", (idea_id, today_str))

    cursor.execute("SELECT streak_days, last_active_date, ideas_read_count, doomscroll_mins_saved FROM user_progress WHERE id = 1")
    row = cursor.fetchone()
    
    streak_days = row["streak_days"]
    last_date = row["last_active_date"]
    ideas_read = row["ideas_read_count"] + 1
    # Each idea read saves ~4 minutes of toxic doomscrolling
    doomscroll_mins = row["doomscroll_mins_saved"] + 4

    if last_date != today_str:
        # Check if yesterday was active
        if last_date:
            try:
                last_d = date.fromisoformat(last_date)
                delta = (date.today() - last_d).days
                if delta == 1:
                    streak_days += 1
                elif delta > 1:
                    streak_days = 1
            except Exception:
                streak_days = 1
        else:
            streak_days = 1
        last_date = today_str

    cursor.execute("""
        UPDATE user_progress
        SET streak_days = ?, last_active_date = ?, ideas_read_count = ?, doomscroll_mins_saved = ?
        WHERE id = 1
    """, (streak_days, last_date, ideas_read, doomscroll_mins))
    conn.commit()
    conn.close()
    return get_user_progress()

def row_to_idea(row) -> Idea:
    tags = []
    if row["tags"]:
        try:
            tags = json.loads(row["tags"])
        except Exception:
            tags = [t.strip() for t in row["tags"].split(",") if t.strip()]

    return Idea(
        id=row["id"],
        title=row["title"],
        one_liner=row["one_liner"],
        summary=row["summary"],
        detailed_explanation=dict(row).get("detailed_explanation") or "",
        example=dict(row).get("example") or "",
        visual_diagram=dict(row).get("visual_diagram") or "",
        quote=row["quote"] or "",
        action_item=row["action_item"] or "",
        author=row["author"],
        source=row["source"],
        topic=row["topic"],
        tags=tags,
        read_time_mins=row["read_time_mins"] or 1,
        color_theme=row["color_theme"] or "indigo",
        likes=row["likes"] or 0,
        saved_count=row["saved_count"] or 0,
        is_liked=bool(row["is_liked"]),
        is_saved=bool(row["is_saved"]),
        leitner_box=dict(row).get("leitner_box") or 1,
        next_review_date=dict(row).get("next_review_date"),
        last_reviewed_date=dict(row).get("last_reviewed_date"),
        created_at=row["created_at"]
    )

# --- Leitner Spaced Repetition Engine ---

def get_due_leitner_ideas(limit: int = 20) -> List[Idea]:
    """Retrieves atomic cards due for active recall review according to the Leitner schedule."""
    conn = get_connection()
    cursor = conn.cursor()
    today_iso = date.today().isoformat()
    cursor.execute("""
        SELECT * FROM ideas
        WHERE next_review_date IS NULL OR next_review_date <= ?
        ORDER BY leitner_box ASC, RANDOM()
        LIMIT ?
    """, (today_iso, limit))
    rows = cursor.fetchall()
    ideas = [row_to_idea(r) for r in rows]
    conn.close()
    return ideas

def record_leitner_review(idea_id: str, grade: str) -> Optional[Idea]:
    """
    Grades an active recall review and schedules the next review date using Leitner intervals:
    Box 1: 1 day, Box 2: 3 days, Box 3: 7 days, Box 4: 14 days, Box 5: 30 days.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT leitner_box FROM ideas WHERE id = ?", (idea_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    current_box = row["leitner_box"] or 1
    today = date.today()
    today_iso = today.isoformat()

    intervals = {1: 1, 2: 3, 3: 7, 4: 14, 5: 30}
    grade_lower = (grade or "good").lower()

    if grade_lower == "hard":
        new_box = 1
        days_ahead = 1
    elif grade_lower == "easy":
        new_box = min(5, current_box + 2)
        days_ahead = intervals.get(new_box, 14)
    else:  # good
        new_box = min(5, current_box + 1)
        days_ahead = intervals.get(new_box, 3)

    from datetime import timedelta
    next_review = (today + timedelta(days=days_ahead)).isoformat()

    cursor.execute("""
        UPDATE ideas
        SET leitner_box = ?, next_review_date = ?, last_reviewed_date = ?
        WHERE id = ?
    """, (new_box, next_review, today_iso, idea_id))

    # Update daily streak & cards reviewed count
    cursor.execute("""
        UPDATE user_progress
        SET ideas_read_count = ideas_read_count + 1,
            last_active_date = ?
        WHERE id = 1
    """, (today_iso,))

    conn.commit()
    conn.close()
    return get_idea_by_id(idea_id)
