import os
import sqlite3
import json
import uuid
import re
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from app.config import settings
from app.models import Idea, Stash, UserProgress, Book, SubstackNote, SubstackComment, Subscription
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
        boundary TEXT,
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
        ("boundary", "TEXT"),
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

    # 9. Substack Notes (Short-form stream & restacks)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS substack_notes (
        id TEXT PRIMARY KEY,
        author_name TEXT NOT NULL,
        author_handle TEXT NOT NULL,
        author_avatar TEXT,
        content TEXT NOT NULL,
        referenced_idea_id TEXT,
        referenced_idea_title TEXT,
        referenced_idea_quote TEXT,
        referenced_idea_author TEXT,
        restack_comment TEXT,
        likes_count INTEGER DEFAULT 0,
        restacks_count INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        is_liked INTEGER DEFAULT 0
    );
    """)

    # 10. Substack Comments / Threaded Discussions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS substack_comments (
        id TEXT PRIMARY KEY,
        idea_id TEXT NOT NULL,
        user_id TEXT DEFAULT 'community',
        user_name TEXT NOT NULL,
        user_avatar TEXT,
        comment_text TEXT NOT NULL,
        likes_count INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        parent_comment_id TEXT
    );
    """)

    # 11. Substack Subscriptions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS substack_subscriptions (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        target_type TEXT NOT NULL,
        target_name TEXT NOT NULL,
        target_handle TEXT,
        created_at TEXT NOT NULL,
        UNIQUE(user_id, target_name)
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
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_created ON substack_notes(created_at DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_comments_idea ON substack_comments(idea_id, created_at DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_subs_user ON substack_subscriptions(user_id);")

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
        # Insert any newly added default ideas and sync existing ones
        today_iso = date.today().isoformat()
        now_str = datetime.utcnow().isoformat()
        for i in DEFAULT_IDEAS:
            c_notice = generate_copyright_attribution(i["source"], i["author"], i.get("publisher", ""))
            src_slug = slugify(i["source"])
            cursor.execute("SELECT id FROM ideas WHERE id = ?", (i["id"],))
            row = cursor.fetchone()
            if not row:
                cursor.execute("""
                    INSERT INTO ideas (
                        id, title, one_liner, summary, detailed_explanation, example, visual_diagram, boundary, quote, action_item, author, source, source_slug, publisher, copyright_notice, topic,
                        tags, read_time_mins, color_theme, likes, saved_count, is_liked, is_saved, leitner_box, next_review_date, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 1, ?, ?)
                """, (
                    i["id"], i["title"], i["one_liner"], i["summary"],
                    i.get("detailed_explanation", ""), i.get("example", ""), i.get("visual_diagram", ""),
                    i.get("boundary", ""),
                    i.get("quote", ""), i.get("action_item", ""), i["author"], i["source"], src_slug,
                    i.get("publisher", "Original Publication"), c_notice, i["topic"],
                    json.dumps(i.get("tags", [])), i.get("read_time_mins", 1),
                    i.get("color_theme", "indigo"), i.get("likes", 120), i.get("saved_count", 65),
                    today_iso, now_str
                ))
            else:
                cursor.execute("""
                    UPDATE ideas
                    SET detailed_explanation = ?, example = ?, visual_diagram = ?, boundary = ?, action_item = ?, source_slug = ?, copyright_notice = ?
                    WHERE id = ?
                """, (i.get("detailed_explanation", ""), i.get("example", ""), i.get("visual_diagram", ""), i.get("boundary", ""), i.get("action_item", ""), src_slug, c_notice, i["id"]))
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

    # Seed default Substack Notes & Discussions if empty
    cursor.execute("SELECT COUNT(*) FROM substack_notes")
    if cursor.fetchone()[0] == 0:
        seed_substack_defaults(conn)

    conn.close()

def seed_data(conn):
    cursor = conn.cursor()
    now_str = datetime.utcnow().isoformat()
    today_iso = date.today().isoformat()

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
                id, title, one_liner, summary, detailed_explanation, example, visual_diagram, boundary, quote, action_item, author, source, source_slug, publisher, copyright_notice, topic,
                tags, read_time_mins, color_theme, likes, saved_count, is_liked, is_saved, leitner_box, next_review_date, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 1, ?, ?)
        """, (
            i["id"], i["title"], i["one_liner"], i["summary"],
            i.get("detailed_explanation", ""), i.get("example", ""), i.get("visual_diagram", ""),
            i.get("boundary", ""),
            i.get("quote", ""), i.get("action_item", ""), i["author"], i["source"], src_slug,
            i.get("publisher", "Original Publication"), c_notice, i["topic"],
            json.dumps(i.get("tags", [])), i.get("read_time_mins", 1),
            i.get("color_theme", "indigo"), i.get("likes", 120), i.get("saved_count", 65),
            today_iso, now_str
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
        boundary=row_dict.get("boundary") or "",
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


# =========================================================================
# SUBSTACK ECOSYSTEM (Notes, Subscriptions, Restacks & Discussions)
# =========================================================================

def seed_substack_defaults(conn):
    cursor = conn.cursor()
    now_iso = datetime.utcnow().isoformat()
    yesterday_iso = (datetime.utcnow() - timedelta(hours=4)).isoformat()
    two_days_ago_iso = (datetime.utcnow() - timedelta(days=1)).isoformat()
    three_days_ago_iso = (datetime.utcnow() - timedelta(days=2)).isoformat()

    default_notes = [
        {
            "id": "note_1",
            "author_name": "Shane Parrish",
            "author_handle": "farnamstreet",
            "author_avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&q=80",
            "content": "The best mental models are the ones you deploy when you are angry, exhausted, or pressured. Inversion is trivial on a whiteboard; it takes immense character to ask 'How could this blow up in my face?' when the entire room is cheering.",
            "referenced_idea_id": "idea_inversion",
            "referenced_idea_title": "The Inversion Principle",
            "referenced_idea_quote": "Invert, always invert: Turn a situation or problem upside down. What happens if all our assumptions are wrong?",
            "referenced_idea_author": "Charlie Munger",
            "restack_comment": "Restacking Munger's foundational heuristic for our weekly executive review.",
            "likes_count": 84,
            "restacks_count": 29,
            "created_at": now_iso
        },
        {
            "id": "note_2",
            "author_name": "Nassim Nicholas Taleb",
            "author_handle": "nntaleb",
            "author_avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=120&q=80",
            "content": "A system that requires geniuses to operate safely is a fragile disaster waiting to detonate. Robustness comes from removing exposure to ruin, not from hoping people become smarter.",
            "referenced_idea_id": "idea_antifragility",
            "referenced_idea_title": "The Antifragile Principle",
            "referenced_idea_quote": "Antifragility is beyond resilience or robustness. The resilient resists shocks and stays the same; the antifragile gets better.",
            "referenced_idea_author": "Nassim Nicholas Taleb",
            "restack_comment": "Notice how nature uses convex optionality: errors are cheap, discoveries are 100x.",
            "likes_count": 142,
            "restacks_count": 56,
            "created_at": yesterday_iso
        },
        {
            "id": "note_3",
            "author_name": "James Clear",
            "author_handle": "jamesclear",
            "author_avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=120&q=80",
            "content": "You do not rise to the level of your goals. You fall to the level of your systems. When motivation fails—and it always does—your habit architecture is the only thing standing between progress and decay.",
            "referenced_idea_id": "idea_identity_habits",
            "referenced_idea_title": "Identity-Based Habits",
            "referenced_idea_quote": "Every action you take is a vote for the type of person you wish to become.",
            "referenced_idea_author": "James Clear",
            "restack_comment": "Cast a vote today. Just one small action.",
            "likes_count": 218,
            "restacks_count": 78,
            "created_at": two_days_ago_iso
        },
        {
            "id": "note_4",
            "author_name": "Morgan Housel",
            "author_handle": "morganhousel",
            "author_avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=120&q=80",
            "content": "Rich is what you spend to signal status to strangers. Wealth is the options you preserve that no one ever sees. The greatest dividend money pays is the ability to control your time.",
            "referenced_idea_id": "idea_rich_vs_wealthy",
            "referenced_idea_title": "Rich vs. Wealthy",
            "referenced_idea_quote": "Spending money to show people how much money you have is the fastest way to have less money. Wealth is what you don't see.",
            "referenced_idea_author": "Morgan Housel",
            "restack_comment": None,
            "likes_count": 175,
            "restacks_count": 63,
            "created_at": three_days_ago_iso
        }
    ]

    for n in default_notes:
        cursor.execute("""
            INSERT OR IGNORE INTO substack_notes (
                id, author_name, author_handle, author_avatar, content,
                referenced_idea_id, referenced_idea_title, referenced_idea_quote, referenced_idea_author,
                restack_comment, likes_count, restacks_count, created_at, is_liked
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            n["id"], n["author_name"], n["author_handle"], n["author_avatar"], n["content"],
            n.get("referenced_idea_id"), n.get("referenced_idea_title"), n.get("referenced_idea_quote"), n.get("referenced_idea_author"),
            n.get("restack_comment"), n["likes_count"], n["restacks_count"], n["created_at"]
        ))

    default_comments = [
        {
            "id": "comm_1",
            "idea_id": "idea_inversion",
            "user_name": "Elena Rostova",
            "user_avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=120&q=80",
            "comment_text": "We applied Inversion to our Q3 SaaS roadmap. Instead of asking 'What features will double customer retention?', we asked 'What bugs and confusing UI steps make trial users rage-quit within 48 hours?' Fixing those 4 friction points cut our churn by 32% with zero new code.",
            "likes_count": 19,
            "created_at": now_iso
        },
        {
            "id": "comm_2",
            "idea_id": "idea_inversion",
            "user_name": "David Chen",
            "user_avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=120&q=80",
            "comment_text": "The Munger meteorology example is gold. In trading, the best risk managers don't hunt 10x wins first; they systematically eliminate positions where leverage can trigger a margin call.",
            "likes_count": 11,
            "created_at": yesterday_iso
        },
        {
            "id": "comm_3",
            "idea_id": "idea_two_minute_rule",
            "user_name": "Marcus Vance",
            "user_avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=120&q=80",
            "comment_text": "The psychological trick is giving yourself honest permission to stop at 2 minutes. Once your subconscious trusts that you aren't running a bait-and-switch, task paralysis disappears.",
            "likes_count": 14,
            "created_at": two_days_ago_iso
        }
    ]

    for c in default_comments:
        cursor.execute("""
            INSERT OR IGNORE INTO substack_comments (
                id, idea_id, user_name, user_avatar, comment_text, likes_count, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            c["id"], c["idea_id"], c["user_name"], c["user_avatar"], c["comment_text"], c["likes_count"], c["created_at"]
        ))

    # Seed default subscriptions for demo user
    cursor.execute("""
        INSERT OR IGNORE INTO substack_subscriptions (id, user_id, target_type, target_name, target_handle, created_at)
        VALUES 
        ('sub_1', 'user_demo', 'publication', 'The Mental Model Review', 'mental-models', ?),
        ('sub_2', 'user_demo', 'author', 'Charlie Munger', 'munger', ?),
        ('sub_3', 'user_demo', 'author', 'Nassim Nicholas Taleb', 'nntaleb', ?)
    """, (now_iso, now_iso, now_iso))

    conn.commit()

def get_substack_notes(limit: int = 50) -> List[SubstackNote]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM substack_notes ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [SubstackNote(**dict(r)) for r in rows]

def create_substack_note(data: Dict[str, Any]) -> SubstackNote:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    note_id = data.get("id") or f"note_{uuid.uuid4().hex[:8]}"
    now_iso = datetime.utcnow().isoformat()
    avatar = data.get("author_avatar") or f"https://api.dicebear.com/7.x/initials/svg?seed={data.get('author_name', 'T').replace(' ', '')}"
    cursor.execute("""
        INSERT INTO substack_notes (
            id, author_name, author_handle, author_avatar, content,
            referenced_idea_id, referenced_idea_title, referenced_idea_quote, referenced_idea_author,
            restack_comment, likes_count, restacks_count, created_at, is_liked
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, 0)
    """, (
        note_id, data.get("author_name", "Anonymous Thinker"), data.get("author_handle", "thinker"),
        avatar, data["content"], data.get("referenced_idea_id"),
        data.get("referenced_idea_title"), data.get("referenced_idea_quote"), data.get("referenced_idea_author"),
        data.get("restack_comment"), now_iso
    ))
    conn.commit()
    cursor.execute("SELECT * FROM substack_notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()
    conn.close()
    return SubstackNote(**dict(row))

def toggle_like_substack_note(note_id: str) -> Optional[SubstackNote]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT is_liked, likes_count FROM substack_notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    new_liked = 0 if row["is_liked"] else 1
    new_count = max(0, row["likes_count"] + (1 if new_liked else -1))
    cursor.execute("UPDATE substack_notes SET is_liked = ?, likes_count = ? WHERE id = ?", (new_liked, new_count, note_id))
    conn.commit()
    cursor.execute("SELECT * FROM substack_notes WHERE id = ?", (note_id,))
    updated_row = cursor.fetchone()
    conn.close()
    return SubstackNote(**dict(updated_row))

def restack_idea_to_notes(idea_id: str, comment: str, author_name: str = "Curated Thinker", author_handle: str = "thinker") -> Optional[SubstackNote]:
    idea = get_idea_by_id(idea_id)
    if not idea:
        return None
    note_data = {
        "content": f"Restacked '{idea.title}' by {idea.author}",
        "author_name": author_name,
        "author_handle": author_handle,
        "referenced_idea_id": idea.id,
        "referenced_idea_title": idea.title,
        "referenced_idea_quote": idea.quote or idea.one_liner,
        "referenced_idea_author": idea.author,
        "restack_comment": comment.strip() if comment else None
    }
    return create_substack_note(note_data)

def get_comments_for_idea(idea_id: str) -> List[SubstackComment]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM substack_comments WHERE idea_id = ? ORDER BY created_at DESC", (idea_id,))
    rows = cursor.fetchall()
    conn.close()
    return [SubstackComment(**dict(r)) for r in rows]

def create_substack_comment(idea_id: str, user_name: str, comment_text: str, user_id: str = "community", parent_id: Optional[str] = None) -> SubstackComment:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    comm_id = f"comm_{uuid.uuid4().hex[:8]}"
    now_iso = datetime.utcnow().isoformat()
    avatar = f"https://api.dicebear.com/7.x/initials/svg?seed={user_name.replace(' ', '')}"
    cursor.execute("""
        INSERT INTO substack_comments (
            id, idea_id, user_id, user_name, user_avatar, comment_text, likes_count, created_at, parent_comment_id
        ) VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)
    """, (comm_id, idea_id, user_id, user_name, avatar, comment_text, now_iso, parent_id))
    conn.commit()
    cursor.execute("SELECT * FROM substack_comments WHERE id = ?", (comm_id,))
    row = cursor.fetchone()
    conn.close()
    return SubstackComment(**dict(row))

def toggle_substack_subscription(user_id: str, target_name: str, target_type: str = "author", target_handle: Optional[str] = None) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM substack_subscriptions WHERE user_id = ? AND target_name = ?", (user_id, target_name))
    row = cursor.fetchone()
    if row:
        cursor.execute("DELETE FROM substack_subscriptions WHERE id = ?", (row[0],))
        is_sub = False
    else:
        sub_id = f"sub_{uuid.uuid4().hex[:8]}"
        now_iso = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT INTO substack_subscriptions (id, user_id, target_type, target_name, target_handle, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sub_id, user_id, target_type, target_name, target_handle or slugify(target_name), now_iso))
        is_sub = True
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM substack_subscriptions WHERE target_name = ?", (target_name,))
    sub_count = cursor.fetchone()[0]
    conn.close()
    return {"subscribed": is_sub, "target_name": target_name, "subscriber_count": sub_count + 120}

def get_user_substack_subscriptions(user_id: str) -> List[Subscription]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM substack_subscriptions WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [Subscription(**dict(r)) for r in rows]

def get_substack_publications() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT author, COUNT(*) as card_count FROM ideas GROUP BY author ORDER BY card_count DESC LIMIT 6")
    authors = cursor.fetchall()
    conn.close()

    pubs = [
        {
            "name": "The Mental Model Review",
            "handle": "mental-models",
            "type": "publication",
            "description": "Weekly masterclass treatises on first principles, systems dynamics, and cognitive biases.",
            "subscribers": "14.2k",
            "avatar": "psychology"
        }
    ]
    for auth, cnt in authors:
        pubs.append({
            "name": auth,
            "handle": slugify(auth),
            "type": "author",
            "description": f"Curated masterclasses and mental model treatises from {auth}.",
            "subscribers": f"{cnt * 340 + 1200}",
            "avatar": "edit_note"
        })
    return pubs

