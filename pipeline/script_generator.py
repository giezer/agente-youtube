"""
Gerador de roteiros usando Ollama (LLM local, sem custo).
Instale o Ollama em: https://ollama.com
Execute: ollama pull llama3.2
"""

import json
import sys
import ollama
from config import OLLAMA_MODEL, OLLAMA_HOST

SYSTEM_PROMPT = (
    "Você é um roteirista especializado em vídeos educativos infantis no estilo Cocomelon. "
    "Cria roteiros alegres, simples, coloridos e repetitivos para crianças de 1 a 5 anos. "
    "SEMPRE responda com JSON válido, sem texto antes ou depois."
)


def _call_ollama(prompt: str) -> str:
    """Call local Ollama model and return the raw text response."""
    client = ollama.Client(host=OLLAMA_HOST)
    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        options={"temperature": 0.7},
    )
    return response.message.content


def _extract_json(text: str) -> dict:
    """Extract JSON object from a string that may have extra text."""
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("Nenhum JSON encontrado na resposta do Ollama.")
    return json.loads(text[start:end])


def generate_script(topic: str, duration_seconds: int = 90) -> dict:
    """
    Generate an educational kids video script using a local Ollama LLM.

    Returns a dict with keys:
        title, description, tags, scenes
    Each scene has:
        scene_number, narration, text_overlay, image_keywords, duration
    """
    num_scenes = max(5, duration_seconds // 15)

    prompt = f"""Crie um roteiro de vídeo educativo infantil no estilo Cocomelon sobre: "{topic}".
Duração aproximada: {duration_seconds} segundos | Número de cenas: {num_scenes}

Retorne SOMENTE este JSON (sem comentários):
{{
  "title": "Título chamativo até 60 caracteres",
  "description": "Descrição do vídeo para YouTube (2 frases, máx 150 caracteres)",
  "tags": ["tag1", "tag2", "tag3", "infantil", "educativo", "criancas"],
  "scenes": [
    {{
      "scene_number": 1,
      "narration": "Texto falado em português brasileiro, simples e alegre para crianças pequenas",
      "text_overlay": "PALAVRA EM MAIÚSCULAS",
      "image_keywords": "english keywords to search colorful children image on pexels",
      "duration": 12
    }}
  ]
}}

Regras obrigatórias:
- Narração em português brasileiro, alegre e repetitiva (estilo Cocomelon)
- image_keywords SEMPRE em inglês (ex: "colorful alphabet letter A cartoon")
- text_overlay: 1 a 3 palavras em MAIÚSCULAS (a letra, número ou palavra ensinada)
- Duração de cada cena: 8 a 15 segundos
- Use linguagem para crianças de 1 a 5 anos"""

    print(f"   🤖 Consultando Ollama ({OLLAMA_MODEL})...", end="", flush=True)
    try:
        raw = _call_ollama(prompt)
        script = _extract_json(raw)
        print(" ✅")
        return script
    except ollama.ResponseError as e:
        print(f"\n❌ Erro no Ollama: {e}")
        print(f"   Verifique se o Ollama está rodando: ollama serve")
        print(f"   E se o modelo está instalado: ollama pull {OLLAMA_MODEL}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"\n❌ Ollama retornou JSON inválido: {e}")
        print("   Tente novamente — às vezes o modelo falha na primeira tentativa.")
        sys.exit(1)
