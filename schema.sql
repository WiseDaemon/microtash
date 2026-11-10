-- ============================================================================
-- MICROSTASH DATABASE SCHEMA SPECIFICATION
-- Applicable schema for Microlearning Idea Cards, Metadata, Stashes & Leitner Spaced Repetition
-- Compatible with SQLite 3.35+, PostgreSQL 12+, and Supabase
-- ============================================================================

-- 1. IDEAS (Atomic Microlearning Cards & Conceptual Frameworks)
CREATE TABLE IF NOT EXISTS ideas (
    id TEXT PRIMARY KEY,                             -- Unique UUID or slug (e.g., 'feynman-technique-101')
    title TEXT NOT NULL,                             -- Name of the mental model or concept
    one_liner TEXT NOT NULL,                         -- Punchy hook / core intuition
    summary TEXT NOT NULL,                           -- Bite-sized microlearning core model (30-60 words)
    detailed_explanation TEXT,                      -- In-depth first-principles & theoretical mechanics (markdown)
    example TEXT,                                   -- Concrete real-world / operational case study
    visual_diagram TEXT,                            -- Native Mermaid.js flowchart or graph syntax
    quote TEXT,                                     -- Key verbatim quote from author or source
    action_item TEXT,                               -- Actionable rule or asymmetric behavior change
    author TEXT NOT NULL,                           -- Thinker / Creator / Author name
    source TEXT NOT NULL,                           -- Book title, paper, or foundational origin
    topic TEXT NOT NULL,                            -- Category (e.g. Mental Models, Productivity, Stoicism)
    tags TEXT NOT NULL,                             -- JSON array of keyword tags: '["learning", "cognition"]'
    read_time_mins INTEGER DEFAULT 1,               -- Estimated reading time in minutes
    color_theme TEXT DEFAULT 'indigo',              -- Visual palette: indigo, emerald, amber, rose, sky, purple
    likes INTEGER DEFAULT 0,                        -- Aggregate community / user likes
    saved_count INTEGER DEFAULT 0,                  -- Aggregate bookmark count
    is_liked INTEGER DEFAULT 0,                     -- Local session like state (0 = false, 1 = true)
    is_saved INTEGER DEFAULT 0,                     -- Local session save state (0 = false, 1 = true)
    leitner_box INTEGER DEFAULT 1,                  -- Spaced repetition level (1: 1d, 2: 3d, 3: 7d, 4: 14d, 5: 30d)
    next_review_date TEXT,                          -- ISO 8601 date (YYYY-MM-DD) for next active recall session
    last_reviewed_date TEXT,                      -- ISO 8601 date (YYYY-MM-DD) of last review
    created_at TEXT NOT NULL                        -- ISO 8601 creation timestamp
);

-- Indices for rapid feed filtering, search, and spaced repetition scheduling
CREATE INDEX IF NOT EXISTS idx_ideas_topic ON ideas(topic);
CREATE INDEX IF NOT EXISTS idx_ideas_leitner ON ideas(next_review_date, leitner_box);
CREATE INDEX IF NOT EXISTS idx_ideas_created ON ideas(created_at DESC);


-- 2. STASHES (Curated Idea Decks & Thematic Stashes)
CREATE TABLE IF NOT EXISTS stashes (
    id TEXT PRIMARY KEY,                             -- Unique UUID (e.g., 'first-principles-pack')
    title TEXT NOT NULL,                             -- Title of collection (e.g., 'Warren Buffett Mental Models')
    description TEXT NOT NULL,                      -- Overview description of the collection
    icon TEXT DEFAULT 'sparkles',                   -- Lucide icon name (e.g., 'book-open', 'brain')
    color TEXT DEFAULT 'indigo',                     -- Theme accent color
    created_at TEXT NOT NULL                        -- ISO 8601 creation timestamp
);


-- 3. STASH_IDEAS (Many-to-Many Mapping between Stashes and Idea Cards)
CREATE TABLE IF NOT EXISTS stash_ideas (
    stash_id TEXT NOT NULL,
    idea_id TEXT NOT NULL,
    added_at TEXT NOT NULL,
    PRIMARY KEY (stash_id, idea_id),
    FOREIGN KEY (stash_id) REFERENCES stashes(id) ON DELETE CASCADE,
    FOREIGN KEY (idea_id) REFERENCES ideas(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_stash_ideas_stash ON stash_ideas(stash_id);
CREATE INDEX IF NOT EXISTS idx_stash_ideas_idea ON stash_ideas(idea_id);


-- 4. USER_PROGRESS (Anti-Doomscroll Gamification & Habit Loop)
CREATE TABLE IF NOT EXISTS user_progress (
    id INTEGER PRIMARY KEY CHECK (id = 1),          -- Single-user singleton row
    streak_days INTEGER DEFAULT 1,                  -- Current consecutive daily learning streak
    last_active_date TEXT,                          -- ISO 8601 date (YYYY-MM-DD) of latest activity
    ideas_read_count INTEGER DEFAULT 0,             -- Total count of cards absorbed
    doomscroll_mins_saved INTEGER DEFAULT 0         -- Calculated screen time converted to microlearning
);


-- 5. READ_HISTORY (Audit Log for Spaced Repetition & Daily Habit Streaks)
CREATE TABLE IF NOT EXISTS read_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea_id TEXT NOT NULL,                          -- ID of card reviewed
    read_date TEXT NOT NULL                         -- ISO 8601 date (YYYY-MM-DD)
);

CREATE INDEX IF NOT EXISTS idx_read_history_date ON read_history(read_date);
