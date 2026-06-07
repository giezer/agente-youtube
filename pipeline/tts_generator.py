"""
Gerador de narração usando Microsoft Edge TTS.
Completamente gratuito — usa os servidores do Microsoft Edge, sem chave de API.
Mais de 400 vozes disponíveis em dezenas de idiomas.
"""

import asyncio
from pathlib import Path
import edge_tts
from config import TTS_VOICE


async def _save_audio(text: str, output_path: Path, voice: str) -> None:
    """Async function to generate and save TTS audio."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))


def generate_narration(text: str, output_path: Path, voice: str = None) -> Path:
    """
    Generate speech narration from text using edge-tts (free).

    Args:
        text: Text to convert to speech (Portuguese BR)
        output_path: Full path where the MP3 file will be saved
        voice: Edge TTS voice name (defaults to config TTS_VOICE)

    Returns:
        Path to the generated MP3 file
    """
    voice = voice or TTS_VOICE
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        asyncio.run(_save_audio(text, output_path, voice))
    except RuntimeError:
        # Fallback for environments where asyncio.run() fails (e.g., Jupyter)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_save_audio(text, output_path, voice))
        loop.close()

    return output_path


def get_audio_duration(audio_path: Path) -> float:
    """Return the duration in seconds of an MP3 file."""
    from moviepy.editor import AudioFileClip

    with AudioFileClip(str(audio_path)) as clip:
        return clip.duration


def list_portuguese_voices() -> list:
    """List all available Portuguese voices (pt-BR and pt-PT)."""

    async def _list():
        voices = await edge_tts.list_voices()
        return [v for v in voices if v["Locale"].startswith("pt")]

    return asyncio.run(_list())
