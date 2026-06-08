"""
Gerador de narração usando Microsoft Edge TTS.
Completamente gratuito — usa os servidores do Microsoft Edge, sem chave de API.
"""

import asyncio
from pathlib import Path
import edge_tts
from config import TTS_VOICE


async def _save_audio(text: str, output_path: Path, voice: str) -> None:
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))


def generate_narration(text: str, output_path: Path, voice: str = None) -> Path:
    voice = voice or TTS_VOICE
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        asyncio.run(_save_audio(text, output_path, voice))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_save_audio(text, output_path, voice))
        loop.close()

    return output_path


def get_audio_duration(audio_path: Path) -> float:
    # ✅ moviepy 2.x: import direto (sem .editor)
    from moviepy import AudioFileClip
    with AudioFileClip(str(audio_path)) as clip:
        return clip.duration


def list_portuguese_voices() -> list:
    async def _list():
        voices = await edge_tts.list_voices()
        return [v for v in voices if v["Locale"].startswith("pt")]
    return asyncio.run(_list())