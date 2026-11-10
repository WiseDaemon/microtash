from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.tts_service import get_or_create_audio

router = APIRouter()

class TTSRequest(BaseModel):
    idea_id: str
    title: str
    summary: str
    author: str

@router.post("/speak")
async def speak_idea(req: TTSRequest):
    filepath = await get_or_create_audio(req.idea_id, req.title, req.summary, req.author)
    if not filepath:
        raise HTTPException(status_code=500, detail="Could not generate neural audio")
    return FileResponse(filepath, media_type="audio/mpeg", filename=f"{req.idea_id}.mp3")

@router.get("/stream/{idea_id}")
async def stream_idea_audio(idea_id: str):
    from app.config import settings
    import os
    filepath = settings.AUDIO_DIR / f"{idea_id}.mp3"
    if os.path.exists(filepath):
        return FileResponse(str(filepath), media_type="audio/mpeg")
    raise HTTPException(status_code=404, detail="Audio file not generated yet")
