from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

from app.config import settings
from app.database import init_db
from app.routes import ideas, stashes, ai, stats, audio

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_TAGLINE,
    version="1.0.0"
)

static_dir = os.path.join(settings.BASE_DIR, "app", "static")
templates_dir = os.path.join(settings.BASE_DIR, "app", "templates")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

app.include_router(ideas.router, prefix="/api/ideas", tags=["Ideas"])
app.include_router(stashes.router, prefix="/api/stashes", tags=["Stashes"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI Extractor"])
app.include_router(stats.router, prefix="/api/stats", tags=["User Stats"])
app.include_router(audio.router, prefix="/api/audio", tags=["Audio Narration"])

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_name": settings.APP_NAME,
        "tagline": settings.APP_TAGLINE
    })
