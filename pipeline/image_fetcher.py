"""
Buscador de imagens usando a API gratuita do Pexels.
Crie uma conta gratuita em: https://www.pexels.com/api/
A chave é 100% gratuita e permite até 200 requisições/hora.
"""

from pathlib import Path
import requests
from config import PEXELS_API_KEY

PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"

# Sufixos adicionados automaticamente para buscar imagens infantis e coloridas
CHILD_FRIENDLY_SUFFIX = "colorful cartoon children illustration"


def fetch_image(keywords: str, scene_index: int, output_dir: Path) -> Path | None:
    """
    Fetch a child-friendly image from Pexels and save it locally.

    Args:
        keywords: English keywords describing the scene (e.g., "letter A cartoon")
        scene_index: Scene number, used to name the file
        output_dir: Directory to save the image

    Returns:
        Path to the downloaded image, or None if Pexels key not set / no results
    """
    if not PEXELS_API_KEY or PEXELS_API_KEY == "cole_sua_chave_aqui":
        # No key configured — caller will use colored background fallback
        return None

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"img_{scene_index:02d}.jpg"

    if output_path.exists():
        return output_path

    headers = {"Authorization": PEXELS_API_KEY}

    # First attempt: keywords + child-friendly suffix
    for query in [f"{keywords} {CHILD_FRIENDLY_SUFFIX}", keywords]:
        params = {
            "query": query,
            "per_page": 5,
            "orientation": "landscape",
            "size": "large",
        }
        try:
            resp = requests.get(PEXELS_SEARCH_URL, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            photos = resp.json().get("photos", [])
            if photos:
                photo_url = photos[0]["src"]["large"]
                img_resp = requests.get(photo_url, timeout=15)
                img_resp.raise_for_status()
                output_path.write_bytes(img_resp.content)
                return output_path
        except requests.RequestException:
            continue

    return None
