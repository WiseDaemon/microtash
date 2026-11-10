# Microstash — Replace Doomscrolling with Microlearning! 🚀

An open-source, full-featured microlearning web application modeled after **[Deepstash](https://deepstash.com/)**, engineered to replace mindless social media feeds with atomic wisdom, mental models, and actionable takeaways from the world's best books, articles, and thinkers.

Powered by **FastAPI**, **NVIDIA NIM APIs**, **Google Gemini AI**, and neural **Edge-TTS** narration.

---

## 🌟 Key Features

### 1. The Anti-Doomscroll Swipe Deck (Tinder / TikTok for Ideas)
- **Distraction-free card deck**: Swipe left (Next) or right (Save to Stash).
- **Interactive 3D Flip**: Flip the card to uncover the deep dive context, inspiring author quotes, and a pragmatic **"Try It Today"** actionable habit.
- **Keyboard Shortcuts**:
  - `Space` or `→`: Next Idea
  - `S`: Save to Stash
  - `L`: Like / Heart
  - `A`: Listen to Audio Narration
  - `F`: Flip Card

### 2. Curated Micro-Feed & Fast Topic Filters
- Instant search by title, thinker, book, or tags.
- Category filters: **Mental Models**, **Productivity**, **Stoicism**, **Wealth & Leverage**, **Psychology**, **Tech & AI**, **Health**.
- Responsive grid view with reading times and 1-click audio playback.

### 3. AI Stashifier & Synthesizer (NVIDIA NIM + Gemini Multi-Model)
- Paste any book excerpt, article URL, podcast transcript, or broad topic prompt.
- Select your AI Engine:
  - **Gemini 3.5 Flash** (ultra-fast structured synthesis)
  - **NVIDIA NIM** (Llama 70B / Nemotron high-capacity reasoning)
- Synthesizes 3 to 6 atomic, structured idea cards with quotes, one-liners, and actionable takeaways.
- 1-click **"Save All to Feed"** or save into a specific Stash collection.

### 4. Curated Stashes (Playlists of Ideas)
- Create custom collections (e.g., *Morning Focus Rituals*, *Stoic Armor for Chaos*, *Founder Mental Models*).
- Organize ideas into thematic stashes and revisit them daily.

### 5. Doomscrolling Slayer Tracker (Gamification)
- **Daily Microlearning Streak** counter (🔥 flame meter).
- **Doomscroll Minutes Saved** calculator (track how many minutes of toxic scrolling you replaced with intellectual leverage).
- Ideas read counter.

### 6. Neural Audio Narration (Listen on the Go)
- Listen to any idea narrated with crisp, natural voice audio using **Edge-TTS** neural voice synthesis with automatic browser **SpeechSynthesis** fallback.
- Floating bottom audio player with play/pause and track controls.

### 7. Social Quote Card Studio (HTML5 Canvas Exporter)
- Generate aesthetic, high-resolution graphic quote cards on HTML5 Canvas.
- Choose between **Deepstash Purple Gradient**, **OLED Dark**, or **Warm Paper** styles.
- 1-click **Download Image (PNG)** or **Copy Text** for Instagram, X/Twitter, LinkedIn, Notion, or Obsidian.

### 8. Daily Recall Gym (Leitner Spaced Repetition)
- **Active Recall Memory Engine**: Instead of passive reading, test your conceptual retention before revealing the explanation.
- **5-Box Leitner Schedule**:
  - `Box 1` (Review Daily)
  - `Box 2` (Review every 3 days)
  - `Box 3` (Review every 7 days)
  - `Box 4` (Review every 14 days)
  - `Box 5` (Mastered / Review every 30 days)
- **Self-Grading Flow**:
  - `[❌ Hard (1)]`: Resets card to Box 1 for next-day retrieval.
  - `[👍 Good (2)]`: Advances card to next spaced repetition interval.
  - `[⚡ Easy (3)]`: Fast-tracks card by +2 intervals.
- Live progress bar, review streak tracker, and keyboard shortcuts (`Space` to reveal, `1`/`2`/`3` to grade).

### 9. Adaptive Visual Renderer (Vector Canvas & Step Flow)
- Dynamic mental model architecture visualization powered by **Mermaid.js**.
- **Interactive Node Stepper**: Step through the model flow step-by-step or click any node to open the live node inspector.
- **Adaptive View Mode Switcher**: Toggle between full **Vector Canvas** and mobile-friendly vertical **Step Flow** timeline.

---

## 🗄️ Database Architecture & Schema

The application uses an ACID-compliant, WAL-mode SQLite database with ANSI-compatible schema ready for PostgreSQL or Supabase migration.

### Database Specification (`schema.sql`)
- **`ideas`**: Atomic cards, theoretical mechanics (`detailed_explanation`), practical case studies (`example`), interactive flow diagrams (`visual_diagram`), quote, author metadata, tags, and Leitner scheduling fields (`leitner_box`, `next_review_date`, `last_reviewed_date`).
- **`stashes`**: User-curated playlist decks and thematic knowledge collections.
- **`stash_ideas`**: Relational join table mapping cards to collections with foreign key cascading deletes.
- **`user_progress`**: Anti-doomscroll gamification tracking daily streaks, cards absorbed, and time saved.
- **`read_history`**: Audit trail of daily reading sessions for retention analytics.

### Database Setup & Verification
Run the database management script to inspect or initialize the schema:
```bash
python scripts/setup_database.py
```

---

## 🚀 How to Run the Application

### Step 1: Open Command Prompt (cmd) or PowerShell
Open your terminal and navigate to the newly created project folder:

```bash
cd c:\LLM\deepstash_microlearning
```

### Step 2: (Optional) Verify or install dependencies
All required libraries (`fastapi`, `uvicorn`, `google-genai`, `openai`, `edge-tts`) are pre-installed in your environment. If running in a fresh virtualenv:

```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
Execute the single-command runner:

```bash
python run.py
```

Or using Uvicorn directly:

```bash
uvicorn app.main:app --reload --port 8000
```

### Step 4: Open in Your Browser
The launcher automatically opens your default browser. You can also manually navigate to:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 📁 Project Architecture

```
c:\LLM\deepstash_microlearning\
├── .env                  # API keys (NVIDIA NIM API, Gemini API, Port)
├── requirements.txt      # Python dependencies
├── run.py                # Single-command launcher with auto-port detection
├── app/
│   ├── config.py         # App configuration & environment loader
│   ├── database.py       # SQLite database with CRUD & progress tracker
│   ├── seed_data.py      # Pre-loaded library of 20+ top mental models & ideas
│   ├── ai_service.py     # AI Extractor (NVIDIA NIM + Gemini multi-engine)
│   ├── tts_service.py    # Neural Edge-TTS audio generator
│   ├── models.py         # Pydantic schemas
│   ├── routes/
│   │   ├── ideas.py      # Idea cards API (like, save, read, filter)
│   │   ├── stashes.py    # Stash collections API
│   │   ├── ai.py         # AI Stashifier extraction API
│   │   ├── stats.py      # Gamification & streak progress API
│   │   └── audio.py      # Audio narration MP3 streaming
│   ├── static/
│   │   ├── css/style.css # 3D perspective, flip effects & dark/light theme
│   │   └── js/
│   │       ├── app.js    # Core app state & reactive UI
│   │       ├── swipe.js  # Swipe engine (touch, mouse drag & keyboard)
│   │       ├── audio.js  # Audio player controller
│   │       └── share.js  # HTML5 Canvas social quote card generator
│   └── templates/
│       └── index.html    # Modern responsive single-page application
└── README.md             # Complete documentation
```

---

## 💡 Pre-Loaded Wisdom Library
The app comes out of the box with atomic insights from:
- *Atomic Habits* — James Clear
- *Thinking, Fast and Slow* — Daniel Kahneman
- *Poor Charlie's Almanack* — Charlie Munger
- *The Almanack of Naval Ravikant* — Naval Ravikant
- *The Psychology of Money* — Morgan Housel
- *Deep Work* — Cal Newport
- *Meditations* — Marcus Aurelius
- *Antifragile* — Nassim Nicholas Taleb
- *Hell Yeah or No* — Derek Sivers
