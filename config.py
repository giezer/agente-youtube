import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"

OUTPUT_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

# Pexels (imagens gratuitas)
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# Ollama (LLM local, sem custo)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# edge-tts (narração, sem custo, usa servidores Microsoft)
TTS_VOICE = os.getenv("TTS_VOICE", "pt-BR-FranciscaNeural")

# Vídeo
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 24
