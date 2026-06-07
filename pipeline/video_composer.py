"""
Compositor de vídeo no estilo Cocomelon.
Usa Pillow para criar frames coloridos e MoviePy para montar o vídeo final.
Sem dependência de ImageMagick.
"""

from pathlib import Path
from typing import Optional
import textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

from config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS

# Paleta Cocomelon: barra colorida por cena
SCENE_THEMES = [
    {"bar": (220, 50, 50),   "text": (255, 255, 255)},  # vermelho
    {"bar": (50, 120, 220),  "text": (255, 255, 255)},  # azul
    {"bar": (50, 180, 60),   "text": (255, 255, 255)},  # verde
    {"bar": (240, 170, 0),   "text": (255, 255, 255)},  # amarelo/laranja
    {"bar": (180, 50, 200),  "text": (255, 255, 255)},  # roxo
    {"bar": (0,  190, 190),  "text": (255, 255, 255)},  # ciano
]

# Fundos coloridos quando não há imagem do Pexels
FALLBACK_BG_COLORS = [
    (255, 235, 100),
    (130, 200, 255),
    (180, 255, 150),
    (255, 160, 120),
    (220, 150, 255),
    (100, 240, 220),
]

# Fontes disponíveis no Linux/WSL (tentadas em ordem)
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
]


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Load a bold font; fall back to Pillow default if none found."""
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _build_frame(
    image_path: Optional[Path],
    text_overlay: str,
    scene_index: int,
    width: int,
    height: int,
) -> np.ndarray:
    """
    Build a single 1920×1080 RGB frame with Cocomelon-style aesthetics:
    - Background: Pexels image (or solid color fallback)
    - Bottom bar: colored with large bold text showing the concept being taught
    """
    theme = SCENE_THEMES[scene_index % len(SCENE_THEMES)]

    # ── Background ──────────────────────────────────────────────────────────
    if image_path and image_path.exists():
        try:
            img = Image.open(image_path).convert("RGB")
        except Exception:
            img = None
    else:
        img = None

    if img is None:
        bg_color = FALLBACK_BG_COLORS[scene_index % len(FALLBACK_BG_COLORS)]
        img = Image.new("RGB", (width, height), bg_color)
    else:
        # Resize + center-crop to fill the frame
        img_ratio = img.width / img.height
        target_ratio = width / height
        if img_ratio > target_ratio:
            new_h, new_w = height, int(height * img_ratio)
        else:
            new_w, new_h = width, int(width / img_ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - width) // 2
        top = (new_h - height) // 2
        img = img.crop((left, top, left + width, top + height))

    # ── Bottom text bar ──────────────────────────────────────────────────────
    if text_overlay:
        bar_h = int(height * 0.18)
        bar_y = height - bar_h

        # Semi-transparent colored bar via RGBA composite
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        bar_rgba = theme["bar"] + (215,)
        overlay_draw.rectangle([0, bar_y, width, height], fill=bar_rgba)

        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

        font_size = int(bar_h * 0.60)
        font = _load_font(font_size)

        text = text_overlay.upper()

        # Wrap if too long
        wrapped = textwrap.fill(text, width=20)
        bbox = draw.textbbox((0, 0), wrapped, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (width - tw) // 2
        y = bar_y + (bar_h - th) // 2

        # Outline (8 directions)
        outline = (20, 20, 20)
        for dx, dy in [(-3, -3), (3, -3), (-3, 3), (3, 3),
                       (0, -3), (0, 3), (-3, 0), (3, 0)]:
            draw.text((x + dx, y + dy), wrapped, font=font, fill=outline)

        draw.text((x, y), wrapped, font=font, fill=theme["text"])

    return np.array(img)


def compose_video(
    script: dict,
    audio_paths: list,
    image_paths: list,
    output_dir: Path,
    output_filename: str,
) -> Path:
    """
    Assemble all scenes into a single MP4 video.

    Args:
        script:          Dict returned by script_generator.generate_script()
        audio_paths:     List of MP3 paths, one per scene
        image_paths:     List of image paths (or None) per scene
        output_dir:      Directory to save the final video
        output_filename: e.g. "video_20260605_123456.mp4"

    Returns:
        Path to the rendered MP4 file
    """
    clips = []

    for i, scene in enumerate(script["scenes"]):
        text_overlay = scene.get("text_overlay", "")
        scene_duration = float(scene.get("duration", 10))

        # Adjust duration to match actual audio length (+ 0.5s buffer)
        audio_path = audio_paths[i] if i < len(audio_paths) else None
        if audio_path and audio_path.exists():
            from moviepy.editor import AudioFileClip as AFC
            with AFC(str(audio_path)) as aud:
                scene_duration = aud.duration + 0.5

        # Build frame image
        img_path = image_paths[i] if i < len(image_paths) else None
        frame = _build_frame(img_path, text_overlay, i, VIDEO_WIDTH, VIDEO_HEIGHT)

        # Create video clip from static frame
        clip = ImageClip(frame, duration=scene_duration)

        # Attach audio
        if audio_path and audio_path.exists():
            audio = AudioFileClip(str(audio_path)).subclip(0, scene_duration - 0.5)
            clip = clip.set_audio(audio)

        clips.append(clip)
        print(f"   🎞️  Cena {i + 1}/{len(script['scenes'])}: '{text_overlay}' ({scene_duration:.1f}s)")

    final = concatenate_videoclips(clips, method="compose")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_filename
    temp_audio = output_dir / "tmp_audio.m4a"

    final.write_videofile(
        str(output_path),
        fps=VIDEO_FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=str(temp_audio),
        remove_temp=True,
        logger="bar",
    )

    return output_path
