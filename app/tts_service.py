import os
import wave
import asyncio
from pathlib import Path
from app.config import settings

async def generate_audio_for_idea(idea_id: str, text_to_speak: str) -> Path:
    """
    Generates a natural audio narration file for an idea card and caches it.
    Uses Google Gemini Neural Voice TTS with automatic caching.
    """
    wav_path = settings.AUDIO_DIR / f"{idea_id}.wav"
    if wav_path.exists() and wav_path.stat().st_size > 1000:
        return wav_path

    # Run blocking Gemini call in threadpool
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _generate_gemini_tts_sync, text_to_speak, wav_path)
    return wav_path

def _generate_gemini_tts_sync(text: str, output_path: Path):
    from google import genai
    from google.genai import types

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)
    # Natural, crisp narration text
    clean_text = text.replace('"', '').replace("'", "").strip()[:500]

    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=clean_text,
        config=types.GenerateContentConfig(response_modalities=["AUDIO"])
    )

    raw_pcm = None
    for candidate in response.candidates:
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if part.inline_data and part.inline_data.data:
                    raw_pcm = part.inline_data.data
                    break

    if not raw_pcm:
        raise ValueError("No audio stream received from TTS engine.")

    # Write PCM data as high-quality 24kHz mono WAV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(24000)
        wav_file.writeframes(raw_pcm)
