from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app import database
from app.tts_service import generate_audio_for_idea

router = APIRouter(prefix="/api/audio", tags=["Audio"])

@router.get("/{idea_id}")
async def get_audio_narration(idea_id: str):
    idea = database.get_idea_by_id(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    # Construct spoken narrative: Headline, punchy hook, summary, action step
    text_to_speak = f"{idea.title}. {idea.one_liner}. {idea.summary} "
    if idea.action_item:
        text_to_speak += f"Practical action step: {idea.action_item}. "
    if idea.author:
        text_to_speak += f"By {idea.author}."

    try:
        audio_file = await generate_audio_for_idea(idea_id, text_to_speak)
        return FileResponse(path=str(audio_file), media_type="audio/wav", filename=f"{idea_id}.wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")
