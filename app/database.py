import os
import sqlite3
import json
import uuid
import re
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from app.config import settings
from app.models import Idea, Stash, UserProgress, Book
from app.seed_data import DEFAULT_IDEAS, DEFAULT_STASHES

def generate_copyright_attribution(title: str, author: str, publisher: str = "") -> str:
    """
    Generates a legally watertight transformative educational commentary attribution credit
    to protect against copyright infringement and give full credit to original authors & publishers.
    """
    clean_title = (title or "Original Work").strip()
    clean_author = (author or "Curated Author").strip()
    pub_str = f" Originally published by {publisher.strip()}." if publisher and publisher.strip() else ""
    return (
        f"Transformative educational commentary & mental model summary of '{clean_title}' by {clean_author}.{pub_str} "
        f"All original book trademarks, copyrights, and intellectual property belong to the respective author and publisher. "
        f"Summaries are provided strictly for transformative personal study, active recall, and cognitive skill development under Fair Use."
    )

def normalize_book_title(title: str) -> str:
    """
    Normalizes a book title for robust, fuzzy matching.
    Removes all punctuation, spaces, accents/casing.
    Handles subtitles: e.g. 'Atomic Habits: Tiny Changes...' -> matches 'atomichabits'
    """
    if not title:
        return ""
    primary = title.split(":")[0].split(" - ")[0].strip()
    norm = re.sub(r'[^a-z0-9]', '', primary.lower())
    return norm if norm else re.sub(r'[^a-z0-9]', '', title.lower())

def slugify(text: str) -> str:
    """Converts a title or string to a URL-safe canonical slug."""
    if not text:
        return "untitled"
    primary = text.split(":")[0].split(" - ")[0].strip()
    s = re.sub(r'[^a-z0-9]+', '-', primary.lower()).strip('-')
    return s or re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-') or "untitled"

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
    
    # 1. Ideas table
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
        source_slug TEXT,
        publisher TEXT DEFAULT 'Original Publication',
        copyright_notice TEXT,
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
        dilemma_cache TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # Ensure schema upgrades for existing DB files
    for col, col_type in [
        ("detailed_explanation", "TEXT"),
        ("example", "TEXT"),
        ("visual_diagram", "TEXT"),
        ("source_slug", "TEXT"),
        ("publisher", "TEXT DEFAULT 'Original Publication'"),
        ("copyright_notice", "TEXT"),
        ("leitner_box", "INTEGER DEFAULT 1"),
        ("next_review_date", "TEXT"),
        ("last_reviewed_date", "TEXT"),
        ("dilemma_cache", "TEXT")
    ]:
        try:
            cursor.execute(f"ALTER TABLE ideas ADD COLUMN {col} {col_type};")
        except Exception:
            pass

    # 2. Canonical Books Registry (Universal Global Book & Idea Cache)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id TEXT PRIMARY KEY,                       -- canonical slug: e.g. "atomic-habits"
        title TEXT NOT NULL,                      -- original title: "Atomic Habits"
        normalized_title TEXT NOT NULL UNIQUE,    -- stripped/lower: "atomichabits"
        author TEXT NOT NULL,                     -- "James Clear"
        publisher TEXT DEFAULT 'Original Publication',
        copyright_notice TEXT,
        description TEXT,                         -- overview/summary
        cover_url TEXT,                           -- cover image or placeholder
        topic TEXT DEFAULT 'Mental Models',
        ideas_count INTEGER DEFAULT 0,
        scanned_by_user TEXT DEFAULT 'community', -- user account or 'community'
        scanned_at TEXT NOT NULL,
        scan_status TEXT DEFAULT 'completed'
    );
    """)

    for col, col_type in [
        ("publisher", "TEXT DEFAULT 'Original Publication'"),
        ("copyright_notice", "TEXT")
    ]:
        try:
            cursor.execute(f"ALTER TABLE books ADD COLUMN {col} {col_type};")
        except Exception:
            pass

    # Ensure all books have a valid copyright attribution notice
    cursor.execute("""
        UPDATE books 
        SET copyright_notice = 'Transformative educational commentary & mental model summary of ''' || title || ''' by ' || author || '. All original book trademarks, copyrights, and intellectual property belong to the respective author and publisher under Fair Use.'
        WHERE copyright_notice IS NULL OR copyright_notice = ''
    """)
    conn.commit()

    # 3. Stashes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stashes (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        icon TEXT DEFAULT 'sparkles',
        color TEXT DEFAULT 'indigo',
        created_at TEXT NOT NULL,
        is_public INTEGER DEFAULT 0,
        owner_user_id TEXT DEFAULT 'community',
        share_slug TEXT UNIQUE,
        clone_count INTEGER DEFAULT 0
    );
    """)

    # Ensure schema upgrades for stashes table
    for col, col_type in [
        ("is_public", "INTEGER DEFAULT 0"),
        ("owner_user_id", "TEXT DEFAULT 'community'"),
        ("share_slug", "TEXT"),
        ("clone_count", "INTEGER DEFAULT 0")
    ]:
        try:
            cursor.execute(f"ALTER TABLE stashes ADD COLUMN {col} {col_type};")
        except Exception:
            pass

    # Backfill default public status and share_slugs for existing stashes
    cursor.execute("""
        UPDATE stashes 
        SET is_public = 1,
            share_slug = id
        WHERE share_slug IS NULL OR share_slug = ''
    """)
    conn.commit()

    # 4. Stash-Idea join table
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

    # 5. User progress & gamification table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_progress (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        streak_days INTEGER DEFAULT 1,
        last_active_date TEXT,
        ideas_read_count INTEGER DEFAULT 0,
        doomscroll_mins_saved INTEGER DEFAULT 0
    );
    """)

    # 6. Ideas read history log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS read_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        idea_id TEXT NOT NULL,
        read_date TEXT NOT NULL
    );
    """)

    # 7. Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        full_name TEXT DEFAULT '',
        created_at TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        is_verified INTEGER DEFAULT 1
    );
    """)

    # 8. User sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_sessions (
        token TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # Performance & Spaced Repetition Indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ideas_topic ON ideas(topic);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ideas_leitner ON ideas(next_review_date, leitner_box);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ideas_created ON ideas(created_at DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ideas_source_slug ON ideas(source_slug);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_norm_title ON books(normalized_title);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_stash_ideas_stash ON stash_ideas(stash_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_stash_ideas_idea ON stash_ideas(idea_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id);")

    conn.commit()

    # Seed default demo account if absent
    cursor.execute("SELECT id FROM users LIMIT 1")
    if not cursor.fetchone():
        from app.auth import hash_password
        p_hash, salt = hash_password("demo1234")
        now_str = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT OR IGNORE INTO users (id, email, username, password_hash, salt, full_name, created_at, is_active, is_verified)
            VALUES ('user_demo', 'demo@microstash.app', 'demo', ?, ?, 'Demo Thinker', ?, 1, 1)
        """, (p_hash, salt, now_str))
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
        # Sync rich detailed explanations, examples, visual diagrams, and copyright notices
        for i in DEFAULT_IDEAS:
            c_notice = generate_copyright_attribution(i["source"], i["author"], i.get("publisher", ""))
            cursor.execute("""
                UPDATE ideas
                SET detailed_explanation = ?, example = ?, visual_diagram = ?, source_slug = ?, copyright_notice = ?
                WHERE id = ? AND (detailed_explanation IS NULL OR detailed_explanation = '' OR example IS NULL OR example = '' OR visual_diagram IS NULL OR visual_diagram = '' OR source_slug IS NULL OR source_slug = '' OR copyright_notice IS NULL OR copyright_notice = '')
            """, (i.get("detailed_explanation", ""), i.get("example", ""), i.get("visual_diagram", ""), slugify(i["source"]), c_notice, i["id"]))
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

    # Backfill books registry from all existing ideas with copyright notices
    cursor.execute("SELECT DISTINCT source, author, topic FROM ideas WHERE source IS NOT NULL AND source != ''")
    distinct_sources = cursor.fetchall()
    now_iso = datetime.utcnow().isoformat()
    for row in distinct_sources:
        src = row["source"].strip()
        auth = row["author"].strip() if row["author"] else "Curated Thinker"
        top = row["topic"] or "Mental Models"
        slug = slugify(src)
        norm = normalize_book_title(src)
        if not norm:
            continue
        c_notice = generate_copyright_attribution(src, auth)
        cursor.execute("SELECT COUNT(*) FROM ideas WHERE LOWER(source) = LOWER(?)", (src,))
        cnt = cursor.fetchone()[0]
        # Stamp source_slug and copyright_notice on matching ideas
        cursor.execute("""
            UPDATE ideas 
            SET source_slug = ?, copyright_notice = COALESCE(copyright_notice, ?)
            WHERE (source_slug IS NULL OR source_slug = '' OR copyright_notice IS NULL OR copyright_notice = '') 
              AND LOWER(source) = LOWER(?)
        """, (slug, c_notice, src))
        # Insert book if not exists
        cursor.execute("""
            INSERT OR IGNORE INTO books (id, title, normalized_title, author, publisher, copyright_notice, topic, ideas_count, scanned_by_user, scanned_at, scan_status)
            VALUES (?, ?, ?, ?, 'Original Publication', ?, ?, ?, 'community', ?, 'completed')
        """, (slug, src, norm, auth, c_notice, top, cnt, now_iso))
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
        src_slug = slugify(i["source"])
        c_notice = generate_copyright_attribution(i["source"], i["author"], i.get("publisher", ""))
        cursor.execute("""
            INSERT OR IGNORE INTO ideas (
                id, title, one_liner, summary, detailed_explanation, example, visual_diagram, quote, action_item, author, source, source_slug, publisher, copyright_notice, topic,
                tags, read_time_mins, color_theme, likes, saved_count, is_liked, is_saved, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?)
        """, (
            i["id"], i["title"], i["one_liner"], i["summary"],
            i.get("detailed_explanation", ""), i.get("example", ""), i.get("visual_diagram", ""),
            i.get("quote", ""), i.get("action_item", ""), i["author"], i["source"], src_slug,
            i.get("publisher", "Original Publication"), c_notice, i["topic"],
            json.dumps(i.get("tags", [])), i.get("read_time_mins", 1),
            i.get("color_theme", "indigo"), i.get("likes", 0), i.get("saved_count", 0), now_str
        ))

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
    source_slug = data.get("source_slug") or slugify(data.get("source", ""))
    publisher = data.get("publisher") or "Original Publication"
    c_notice = data.get("copyright_notice") or generate_copyright_attribution(data["source"], data["author"], publisher)
    dilemma_cache = data.get("dilemma_cache")
    
    cursor.execute("""
        INSERT INTO ideas (
            id, title, one_liner, summary, detailed_explanation, example, visual_diagram, quote, action_item, author, source, source_slug, publisher, copyright_notice, topic,
            tags, read_time_mins, color_theme, likes, saved_count, is_liked, is_saved, dilemma_cache, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0, ?, ?)
    """, (
        idea_id, data["title"], data["one_liner"], data["summary"],
        data.get("detailed_explanation", ""), data.get("example", ""), data.get("visual_diagram", ""),
        data.get("quote"), data.get("action_item"), data["author"], data["source"], source_slug,
        publisher, c_notice, data.get("topic", "General"),
        tags_json, data.get("read_time_mins", 1), data.get("color_theme", "indigo"),
        dilemma_cache, created_at
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

def get_stashes(owner_user_id: Optional[str] = None) -> List[Stash]:
    conn = get_connection()
    cursor = conn.cursor()
    if owner_user_id:
        cursor.execute("SELECT * FROM stashes WHERE owner_user_id = ? OR owner_user_id = 'community' ORDER BY rowid ASC", (owner_user_id,))
    else:
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
            is_public=bool(r["is_public"] if "is_public" in r.keys() else 0),
            owner_user_id=r["owner_user_id"] if "owner_user_id" in r.keys() else "community",
            share_slug=r["share_slug"] if "share_slug" in r.keys() else stash_id,
            clone_count=r["clone_count"] if "clone_count" in r.keys() else 0,
            idea_ids=idea_ids,
            ideas_count=len(idea_ids)
        ))
    conn.close()
    return stashes

def get_stash_by_id(stash_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stashes WHERE id = ? OR share_slug = ?", (stash_id, stash_id))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    actual_id = row["id"]
    cursor.execute("""
        SELECT i.* FROM ideas i
        JOIN stash_ideas si ON i.id = si.idea_id
        WHERE si.stash_id = ?
        ORDER BY si.added_at DESC
    """, (actual_id,))
    idea_rows = cursor.fetchall()
    ideas = [row_to_idea(ir) for ir in idea_rows]
    
    owner_username = "community"
    owner_id = row["owner_user_id"] if "owner_user_id" in row.keys() else "community"
    if owner_id and owner_id != "community":
        cursor.execute("SELECT username FROM users WHERE id = ?", (owner_id,))
        u = cursor.fetchone()
        if u:
            owner_username = u["username"]

    stash_data = {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "icon": row["icon"],
        "color": row["color"],
        "created_at": row["created_at"],
        "is_public": bool(row["is_public"] if "is_public" in row.keys() else 0),
        "owner_user_id": owner_id,
        "owner_username": owner_username,
        "share_slug": row["share_slug"] if "share_slug" in row.keys() else row["id"],
        "clone_count": row["clone_count"] if "clone_count" in row.keys() else 0,
        "ideas": ideas,
        "ideas_count": len(ideas)
    }
    conn.close()
    return stash_data

def create_stash(
    title: str,
    description: str,
    icon: str = "sparkles",
    color: str = "indigo",
    owner_user_id: str = "community",
    is_public: bool = False
) -> Stash:
    conn = get_connection()
    cursor = conn.cursor()
    stash_id = f"stash_{uuid.uuid4().hex[:8]}"
    slug = f"{slugify(title)}-{uuid.uuid4().hex[:6]}"
    created_at = datetime.utcnow().isoformat()
    cursor.execute("""
        INSERT INTO stashes (id, title, description, icon, color, created_at, is_public, owner_user_id, share_slug, clone_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (stash_id, title, description, icon, color, created_at, 1 if is_public else 0, owner_user_id, slug))
    conn.commit()
    conn.close()
    return Stash(
        id=stash_id,
        title=title,
        description=description,
        icon=icon,
        color=color,
        created_at=created_at,
        is_public=is_public,
        owner_user_id=owner_user_id,
        share_slug=slug,
        clone_count=0,
        idea_ids=[],
        ideas_count=0
    )

def publish_stash(stash_id: str, is_public: bool = True) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stashes WHERE id = ? OR share_slug = ?", (stash_id, stash_id))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    actual_id = row["id"]
    slug = row["share_slug"] if row["share_slug"] else f"{slugify(row['title'])}-{uuid.uuid4().hex[:6]}"
    cursor.execute("""
        UPDATE stashes 
        SET is_public = ?, share_slug = ? 
        WHERE id = ?
    """, (1 if is_public else 0, slug, actual_id))
    conn.commit()
    conn.close()
    return get_stash_by_id(actual_id)

def list_public_stashes(search: Optional[str] = None) -> List[Stash]:
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM stashes WHERE is_public = 1"
    params = []
    if search:
        search_pattern = f"%{search.lower()}%"
        query += " AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ?)"
        params.extend([search_pattern, search_pattern])
    query += " ORDER BY clone_count DESC, created_at DESC"
    cursor.execute(query, params)
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
            is_public=True,
            owner_user_id=r["owner_user_id"] if "owner_user_id" in r.keys() else "community",
            share_slug=r["share_slug"] if "share_slug" in r.keys() else stash_id,
            clone_count=r["clone_count"] if "clone_count" in r.keys() else 0,
            idea_ids=idea_ids,
            ideas_count=len(idea_ids)
        ))
    conn.close()
    return stashes

def clone_stash(stash_id_or_slug: str, new_owner_id: str = "community") -> Optional[Dict[str, Any]]:
    orig = get_stash_by_id(stash_id_or_slug)
    if not orig:
        return None

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE stashes SET clone_count = clone_count + 1 WHERE id = ?", (orig["id"],))
    conn.commit()
    conn.close()

    new_title = f"{orig['title']} (My Stash)"
    new_desc = f"Cloned from @{orig.get('owner_username', 'community')}: {orig['description']}"
    new_stash = create_stash(
        title=new_title,
        description=new_desc,
        icon=orig["icon"],
        color=orig["color"],
        owner_user_id=new_owner_id,
        is_public=False
    )

    for idea in orig.get("ideas", []):
        add_idea_to_stash(new_stash.id, idea.id)

    return get_stash_by_id(new_stash.id)

def add_idea_to_stash(stash_id: str, idea_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.utcnow().isoformat()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO stash_ideas (stash_id, idea_id, added_at)
            VALUES (?, ?, ?)
        """, (stash_id, idea_id, now_str))
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

    cursor.execute("INSERT INTO read_history (idea_id, read_date) VALUES (?, ?)", (idea_id, today_str))

    cursor.execute("SELECT streak_days, last_active_date, ideas_read_count, doomscroll_mins_saved FROM user_progress WHERE id = 1")
    row = cursor.fetchone()
    
    streak_days = row["streak_days"]
    last_date = row["last_active_date"]
    ideas_read = row["ideas_read_count"] + 1
    doomscroll_mins = row["doomscroll_mins_saved"] + 4

    if last_date != today_str:
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
    row_dict = dict(row)
    tags = []
    if row_dict.get("tags"):
        try:
            tags = json.loads(row_dict["tags"])
        except Exception:
            tags = [t.strip() for t in row_dict["tags"].split(",") if t.strip()]

    return Idea(
        id=row_dict["id"],
        title=row_dict["title"],
        one_liner=row_dict["one_liner"],
        summary=row_dict["summary"],
        detailed_explanation=row_dict.get("detailed_explanation") or "",
        example=row_dict.get("example") or "",
        visual_diagram=row_dict.get("visual_diagram") or "",
        quote=row_dict.get("quote") or "",
        action_item=row_dict.get("action_item") or "",
        author=row_dict["author"],
        source=row_dict["source"],
        source_slug=row_dict.get("source_slug"),
        publisher=row_dict.get("publisher") or "Original Publication",
        copyright_notice=row_dict.get("copyright_notice") or generate_copyright_attribution(row_dict["source"], row_dict["author"], row_dict.get("publisher", "")),
        topic=row_dict["topic"],
        tags=tags,
        read_time_mins=row_dict.get("read_time_mins") or 1,
        color_theme=row_dict.get("color_theme") or "indigo",
        likes=row_dict.get("likes") or 0,
        saved_count=row_dict.get("saved_count") or 0,
        is_liked=bool(row_dict.get("is_liked")),
        is_saved=bool(row_dict.get("is_saved")),
        leitner_box=row_dict.get("leitner_box") or 1,
        next_review_date=row_dict.get("next_review_date"),
        last_reviewed_date=row_dict.get("last_reviewed_date"),
        created_at=row_dict["created_at"],
        dilemma_cache=row_dict.get("dilemma_cache")
    )

# --- Leitner Spaced Repetition Engine ---

def get_due_leitner_ideas(limit: int = 20) -> List[Idea]:
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

def record_leitner_review(idea_id: str, grade: Any) -> Optional[Idea]:
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
    grade_str = str(grade or "good").strip().lower()

    if grade_str in ("hard", "1", "2"):
        new_box = 1
        days_ahead = 1
    elif grade_str in ("easy", "5"):
        new_box = min(5, current_box + 2)
        days_ahead = intervals.get(new_box, 14)
    else:  # good, 3, 4
        new_box = min(5, current_box + 1)
        days_ahead = intervals.get(new_box, 3)

    next_review = (today + timedelta(days=days_ahead)).isoformat()

    cursor.execute("""
        UPDATE ideas
        SET leitner_box = ?, next_review_date = ?, last_reviewed_date = ?
        WHERE id = ?
    """, (new_box, next_review, today_iso, idea_id))

    cursor.execute("""
        UPDATE user_progress
        SET ideas_read_count = ideas_read_count + 1,
            last_active_date = ?
        WHERE id = 1
    """, (today_iso,))

    conn.commit()
    conn.close()
    return get_idea_by_id(idea_id)

def update_idea_dilemma(idea_id: str, dilemma_json: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE ideas SET dilemma_cache = ? WHERE id = ?", (dilemma_json, idea_id))
    conn.commit()
    conn.close()

# --- Universal Global Book & Idea Cache ---

def find_scanned_book(query: str) -> Optional[Dict[str, Any]]:
    if not query or not query.strip():
        return None

    conn = get_connection()
    cursor = conn.cursor()

    clean_q = query.strip()
    norm_q = normalize_book_title(clean_q)
    slug_q = slugify(clean_q)

    def _return_book(r):
        if not r:
            conn.close()
            return None
        d = dict(r)
        if not d.get("copyright_notice"):
            d["copyright_notice"] = generate_copyright_attribution(d.get("title", ""), d.get("author", "Curated Thinker"), d.get("publisher", "Original Publication"))
            try:
                cursor.execute("UPDATE books SET copyright_notice = ? WHERE id = ?", (d["copyright_notice"], d["id"]))
                conn.commit()
            except Exception:
                pass
        conn.close()
        return d

    # 1. Exact slug match
    cursor.execute("SELECT * FROM books WHERE id = ?", (slug_q,))
    row = cursor.fetchone()
    if row:
        return _return_book(row)

    # 2. Normalized title match
    if norm_q:
        cursor.execute("SELECT * FROM books WHERE normalized_title = ?", (norm_q,))
        row = cursor.fetchone()
        if row:
            return _return_book(row)

    # 3. Case-insensitive exact title
    cursor.execute("SELECT * FROM books WHERE LOWER(title) = LOWER(?)", (clean_q,))
    row = cursor.fetchone()
    if row:
        return _return_book(row)

    # 4. Normalized containment
    if norm_q and len(norm_q) >= 4:
        cursor.execute("""
            SELECT * FROM books 
            WHERE normalized_title LIKE ? 
               OR ? LIKE '%' || normalized_title || '%'
            ORDER BY ideas_count DESC
            LIMIT 1
        """, (f"%{norm_q}%", norm_q))
        row = cursor.fetchone()
        if row:
            return _return_book(row)

    # 5. Fallback check directly in ideas table
    cursor.execute("""
        SELECT source, author, topic, COUNT(*) as cnt 
        FROM ideas 
        WHERE LOWER(source) = LOWER(?) OR LOWER(source) LIKE ?
        GROUP BY source
        ORDER BY cnt DESC
        LIMIT 1
    """, (clean_q, f"%{clean_q.lower()}%"))
    idea_match = cursor.fetchone()
    if idea_match:
        src = idea_match["source"]
        auth = idea_match["author"] or "Curated Thinker"
        top = idea_match["topic"] or "Mental Models"
        cnt = idea_match["cnt"]
        b_slug = slugify(src)
        b_norm = normalize_book_title(src)
        c_notice = generate_copyright_attribution(src, auth)

        cursor.execute("""
            INSERT OR IGNORE INTO books (id, title, normalized_title, author, publisher, copyright_notice, topic, ideas_count, scanned_by_user, scanned_at, scan_status)
            VALUES (?, ?, ?, ?, 'Original Publication', ?, ?, ?, 'community', ?, 'completed')
        """, (b_slug, src, b_norm, auth, c_notice, top, cnt, datetime.utcnow().isoformat()))
        conn.commit()

        cursor.execute("SELECT * FROM books WHERE id = ?", (b_slug,))
        new_row = cursor.fetchone()
        return _return_book(new_row)

    conn.close()
    return None

def get_book_ideas(source_slug: str, source_title: str = "") -> List[Idea]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM ideas 
        WHERE source_slug = ? 
           OR (LOWER(source) = LOWER(?) AND ? != '')
        ORDER BY created_at ASC
    """, (source_slug, source_title, source_title))
    rows = cursor.fetchall()
    ideas = [row_to_idea(r) for r in rows]
    conn.close()
    return ideas

def register_scanned_book(
    title: str,
    author: str,
    description: str = "",
    topic: str = "Mental Models",
    ideas_list: List[Dict[str, Any]] = None,
    scanned_by: str = "community",
    cover_url: Optional[str] = None,
    publisher: str = "Original Publication"
) -> Dict[str, Any]:
    if not title or not title.strip():
        raise ValueError("Book title is required")

    conn = get_connection()
    cursor = conn.cursor()

    clean_title = title.strip()
    slug = slugify(clean_title)
    norm = normalize_book_title(clean_title)
    clean_author = author.strip() if author else "Curated Thinker"
    now_iso = datetime.utcnow().isoformat()
    ideas_list = ideas_list or []
    c_notice = generate_copyright_attribution(clean_title, clean_author, publisher)

    cursor.execute("SELECT * FROM books WHERE id = ? OR normalized_title = ?", (slug, norm))
    existing_book = cursor.fetchone()

    if existing_book:
        book_id = existing_book["id"]
        cursor.execute("""
            UPDATE books 
            SET copyright_notice = COALESCE(copyright_notice, ?),
                publisher = CASE WHEN publisher IS NULL OR publisher = 'Original Publication' THEN ? ELSE publisher END
            WHERE id = ?
        """, (c_notice, publisher, book_id))
        conn.commit()
    else:
        book_id = slug
        cursor.execute("""
            INSERT INTO books (id, title, normalized_title, author, publisher, copyright_notice, description, cover_url, topic, ideas_count, scanned_by_user, scanned_at, scan_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'completed')
        """, (book_id, clean_title, norm, clean_author, publisher, c_notice, description, cover_url, topic, len(ideas_list), scanned_by, now_iso))
        conn.commit()

    conn.close()

    # Find or create public book stash
    stashes = get_stashes()
    stash_title = f"{clean_title} — Complete Book"
    matching_stash = next((s for s in stashes if s.title.lower() == stash_title.lower() or s.id == f"stash_{slug}"), None)

    if not matching_stash:
        stash = create_stash(
            title=stash_title,
            description=f"Complete microlearning collection of all core mental models and ideas from '{clean_title}' by {clean_author}. {c_notice}",
            icon="book-open",
            color="indigo"
        )
        stash_id = stash.id
    else:
        stash_id = matching_stash.id

    created_or_found_ideas = []
    for item in ideas_list:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM ideas 
            WHERE LOWER(title) = LOWER(?) AND (source_slug = ? OR LOWER(source) = LOWER(?))
        """, (item["title"], slug, clean_title))
        existing_idea = cursor.fetchone()
        conn.close()

        if existing_idea:
            idea = get_idea_by_id(existing_idea["id"])
        else:
            item_data = dict(item)
            item_data["source"] = clean_title
            item_data["author"] = clean_author
            item_data["source_slug"] = slug
            item_data["publisher"] = publisher
            item_data["copyright_notice"] = c_notice
            if not item_data.get("topic"):
                item_data["topic"] = topic
            idea = create_idea(item_data)

        if idea:
            add_idea_to_stash(stash_id, idea.id)
            created_or_found_ideas.append(idea)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE books SET ideas_count = ? WHERE id = ?", (len(created_or_found_ideas), book_id))
    conn.commit()

    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    final_book = dict(cursor.fetchone())
    conn.close()

    return {
        "book": final_book,
        "stash_id": stash_id,
        "ideas": created_or_found_ideas,
        "count": len(created_or_found_ideas)
    }

def list_scanned_books(topic: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM books WHERE 1=1"
    params = []

    if topic and topic.lower() != "all":
        query += " AND LOWER(topic) = LOWER(?)"
        params.append(topic)

    if search:
        search_pattern = f"%{search.lower()}%"
        query += " AND (LOWER(title) LIKE ? OR LOWER(author) LIKE ? OR LOWER(publisher) LIKE ? OR LOWER(description) LIKE ?)"
        params.extend([search_pattern] * 4)

    query += " ORDER BY ideas_count DESC, scanned_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    books = [dict(r) for r in rows]
    conn.close()
    return books

def get_book_by_slug(slug_or_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE id = ? OR normalized_title = ?", (slug_or_id, normalize_book_title(slug_or_id)))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    d = dict(row)
    if not d.get("copyright_notice"):
        d["copyright_notice"] = generate_copyright_attribution(d.get("title", ""), d.get("author", "Curated Thinker"), d.get("publisher", "Original Publication"))
        try:
            cursor.execute("UPDATE books SET copyright_notice = ? WHERE id = ?", (d["copyright_notice"], d["id"]))
            conn.commit()
        except Exception:
            pass
    conn.close()
    return d


# --- User Accounts & Session Operations ---

def create_user(email: str, username: str, password: str, full_name: str = "") -> Dict[str, Any]:
    from app.auth import hash_password
    conn = get_connection()
    cursor = conn.cursor()
    
    clean_email = email.strip().lower()
    clean_username = username.strip().lower()
    
    cursor.execute("SELECT id FROM users WHERE LOWER(email) = ? OR LOWER(username) = ?", (clean_email, clean_username))
    if cursor.fetchone():
        conn.close()
        raise ValueError("An account with this email or username already exists.")
        
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    pwd_hash, salt = hash_password(password)
    now_iso = datetime.utcnow().isoformat()
    
    cursor.execute("""
        INSERT INTO users (id, email, username, password_hash, salt, full_name, created_at, is_active, is_verified)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1, 1)
    """, (user_id, clean_email, clean_username, pwd_hash, salt, full_name.strip(), now_iso))
    conn.commit()
    conn.close()
    
    return {
        "id": user_id,
        "email": clean_email,
        "username": clean_username,
        "full_name": full_name.strip(),
        "created_at": now_iso,
        "is_active": True
    }

def get_user_by_email_or_username(identifier: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    clean_id = identifier.strip().lower()
    cursor.execute("""
        SELECT * FROM users 
        WHERE LOWER(email) = ? OR LOWER(username) = ?
        LIMIT 1
    """, (clean_id, clean_id))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_user_session(user_id: str, token: str, expires_at: datetime):
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.utcnow().isoformat()
    exp_iso = expires_at.isoformat()
    cursor.execute("""
        INSERT OR REPLACE INTO user_sessions (token, user_id, created_at, expires_at)
        VALUES (?, ?, ?, ?)
    """, (token, user_id, now_iso, exp_iso))
    conn.commit()
    conn.close()

def validate_session_token(token: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.utcnow().isoformat()
    cursor.execute("""
        SELECT s.token, s.expires_at, u.id, u.email, u.username, u.full_name, u.created_at, u.is_active
        FROM user_sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.token = ? AND s.expires_at > ? AND u.is_active = 1
        LIMIT 1
    """, (token, now_iso))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_user_session(token: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()
    return True

def delete_all_user_sessions(user_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True
