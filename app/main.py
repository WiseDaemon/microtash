from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.config import settings
from app import database
from app.database import init_db
from app.routes import ideas, stashes, ai, stats, audio, compliance, books, auth, substack

app = FastAPI(
    title=settings.APP_NAME,
    description="The Mental Model Gym — Retain high-leverage frameworks with active recall, system diagrams & Socratic AI challenges",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static & Templates setup
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Include API routes
app.include_router(ideas.router)
app.include_router(books.router)
app.include_router(stashes.router)
app.include_router(ai.router)
app.include_router(stats.router)
app.include_router(audio.router)
app.include_router(compliance.router)
app.include_router(auth.router)
app.include_router(substack.router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(content=b"", media_type="image/x-icon")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.APP_NAME,
            "tagline": settings.APP_TAGLINE
        }
    )

@app.get("/share/stash/{share_slug}")
def view_shared_stash(share_slug: str, request: Request):
    stash = database.get_stash_by_id(share_slug)
    if not stash:
        raise HTTPException(status_code=404, detail="Shared stash not found")
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.APP_NAME,
            "tagline": settings.APP_TAGLINE,
            "shared_stash_slug": share_slug,
            "shared_stash_title": stash["title"]
        }
    )


# =========================================================================
# GOOGLE STITCH UI SHOWCASE ROUTES
# =========================================================================
from fastapi.responses import HTMLResponse, FileResponse

@app.get("/stitch/feed", response_class=HTMLResponse)
def stitch_feed():
    template_path = TEMPLATES_DIR / "stitch_design.html"
    return HTMLResponse(content=template_path.read_text(encoding="utf-8"))

@app.get("/stitch/stress-test", response_class=HTMLResponse)
def stitch_stress_test():
    template_path = TEMPLATES_DIR / "stitch_stress_test.html"
    return HTMLResponse(content=template_path.read_text(encoding="utf-8"))

@app.get("/stitch/workout", response_class=HTMLResponse)
def stitch_workout():
    template_path = TEMPLATES_DIR / "stitch_workout.html"
    return HTMLResponse(content=template_path.read_text(encoding="utf-8"))

@app.get("/stitch", response_class=HTMLResponse)
def stitch_showcase():
    return HTMLResponse(content="""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Stitch UI Showcase — Microstash</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen py-10 px-4 sm:px-8 max-w-6xl mx-auto">
    <header class="mb-10 text-center">
        <span class="text-xs font-bold uppercase tracking-widest text-emerald-400 bg-emerald-950/60 border border-emerald-500/30 px-3 py-1 rounded-full">Google Stitch MCP</span>
        <h1 class="text-3xl sm:text-5xl font-black text-white mt-3 tracking-tight">Microstash Design System</h1>
        <p class="text-sm sm:text-base text-gray-400 mt-2 max-w-2xl mx-auto">High-fidelity, production-grade Android UI screens generated via Google Stitch using the <span class="text-emerald-400 font-semibold">Obsidian Kinetic</span> design system.</p>
        <div class="mt-6 flex justify-center space-x-3">
            <a href="/" class="px-4 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-xs font-bold text-gray-200 transition">← Back to Live App</a>
        </div>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- Screen 1 -->
        <div class="bg-gray-900 border border-gray-800 rounded-3xl p-5 shadow-2xl flex flex-col justify-between hover:border-emerald-500/50 transition">
            <div>
                <img src="/static/stitch_screen_1.png" alt="Screen 1 Feed" class="w-full rounded-2xl shadow-md border border-gray-800 object-cover max-h-96">
                <h3 class="text-lg font-bold text-white mt-4">1. Active Recall Deck & Feed</h3>
                <p class="text-xs text-gray-400 mt-1">Hero swipe deck, neural waveform audio pill, interactive systems diagram, and topic filters.</p>
            </div>
            <a href="/stitch/feed" target="_blank" class="mt-5 block w-full text-center py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-gray-950 font-black text-xs transition">
                Open Interactive Screen ↗
            </a>
        </div>

        <!-- Screen 2 -->
        <div class="bg-gray-900 border border-gray-800 rounded-3xl p-5 shadow-2xl flex flex-col justify-between hover:border-amber-500/50 transition">
            <div>
                <img src="/static/stitch_screen_2.png" alt="Screen 2 Socratic Dilemma" class="w-full rounded-2xl shadow-md border border-gray-800 object-cover max-h-96">
                <h3 class="text-lg font-bold text-white mt-4">2. Socratic Dilemma Arena</h3>
                <p class="text-xs text-gray-400 mt-1">Scenario dilemmas, cognitive trap choices, diagnostic feedback states, and first-principles heuristics.</p>
            </div>
            <a href="/stitch/stress-test" target="_blank" class="mt-5 block w-full text-center py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-gray-950 font-black text-xs transition">
                Open Interactive Screen ↗
            </a>
        </div>

        <!-- Screen 3 -->
        <div class="bg-gray-900 border border-gray-800 rounded-3xl p-5 shadow-2xl flex flex-col justify-between hover:border-indigo-500/50 transition">
            <div>
                <img src="/static/stitch_screen_3.png" alt="Screen 3 Workout" class="w-full rounded-2xl shadow-md border border-gray-800 object-cover max-h-96">
                <h3 class="text-lg font-bold text-white mt-4">3. Cognitive Workout (Leitner)</h3>
                <p class="text-xs text-gray-400 mt-1">Boxes 1–5 interval visualizer, active recall prompt flipper, and 3-tier difficulty buttons.</p>
            </div>
            <a href="/stitch/workout" target="_blank" class="mt-5 block w-full text-center py-2.5 rounded-xl bg-indigo-500 hover:bg-indigo-400 text-white font-black text-xs transition">
                Open Interactive Screen ↗
            </a>
        </div>
    </div>
</body>
</html>""")
