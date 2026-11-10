from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.config import settings
from app.database import init_db
from app.routes import ideas, stashes, ai, stats, audio, compliance

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
app.include_router(stashes.router)
app.include_router(ai.router)
app.include_router(stats.router)
app.include_router(audio.router)
app.include_router(compliance.router)

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
