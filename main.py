#!/usr/bin/env python3
"""
YouTube Agent — Pipeline educativo infantil estilo Cocomelon
============================================================
Gera vídeos educativos para crianças sem custo de API.

Uso:
  python main.py --topic alfabeto
  python main.py --topic "Números de 1 a 10" --duration 120
  python main.py --topic animais --upload
  python main.py --topic higiene --dry-run
  python main.py --list-topics
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

from config import OUTPUT_DIR
from pipeline.script_generator import generate_script
from pipeline.tts_generator import generate_narration, get_audio_duration
from pipeline.image_fetcher import fetch_image
from pipeline.video_composer import compose_video
from pipeline.uploader import upload_to_youtube

# ── Temas pré-definidos (estilo Cocomelon) ───────────────────────────────────
TOPICS = {
    "alfabeto":   "Vamos aprender o Alfabeto! As letras de A a Z com imagens divertidas",
    "numeros":    "Aprendendo os Números de 1 a 10 - Vamos contar juntos!",
    "animais":    "Os Animais da Fazenda - Boi, Cavalo, Galinha e muito mais",
    "cores":      "Aprendendo as Cores do Arco-Íris - Vermelho, Azul, Verde...",
    "frutas":     "Frutas Deliciosas! Maçã, Banana, Uva, Laranja e mais",
    "corpo":      "Partes do Corpo Humano - Cabeça, Mãos, Pés e mais!",
    "higiene":    "Hora de Escovar os Dentes! Cuidando da Saúde com Alegria",
    "banho":      "Hora do Banho! Aprendendo a Se Cuidar Sozinho",
    "banheiro":   "Aprendendo a Usar o Banheiro Sozinho - Grandes Conquistas!",
    "palavras":   "Primeiras Palavras em Português - Mamãe, Papai, Água, Leite",
    "formas":     "Formas Geométricas - Círculo, Quadrado, Triângulo e mais",
    "dias":       "Os Dias da Semana - Segunda, Terça, Quarta... Vamos aprender!",
}


def _print_banner():
    print("\n" + "=" * 55)
    print("  🎬  YouTube Agent — Vídeos Infantis Educativos")
    print("       Estilo Cocomelon | Sem custo de API")
    print("=" * 55)


def run_pipeline(topic: str, duration: int, upload: bool, dry_run: bool):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_DIR / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    _print_banner()
    print(f"  Tema    : {topic}")
    print(f"  Duração : ~{duration}s")
    print(f"  Saída   : {run_dir}")
    print("=" * 55)

    # ── ETAPA 1: Roteiro via Ollama ──────────────────────────────────────────
    print("\n📝 [1/4] Gerando roteiro com Ollama...")
    script = generate_script(topic, duration)

    script_path = run_dir / "script.json"
    script_path.write_text(json.dumps(script, ensure_ascii=False, indent=2))
    print(f"   Título  : {script['title']}")
    print(f"   Cenas   : {len(script['scenes'])}")
    print(f"   Salvo em: {script_path.name}")

    if dry_run:
        print(f"\n🔍 Modo --dry-run: roteiro gerado, pipeline encerrado.")
        print(f"   Veja o roteiro: cat {script_path}")
        return

    # ── ETAPA 2: Narração via edge-tts ──────────────────────────────────────
    print("\n🎙️ [2/4] Gerando narrações (edge-tts, gratuito)...")
    audio_paths = []
    for i, scene in enumerate(script["scenes"]):
        audio_file = run_dir / f"audio_{i:02d}.mp3"
        narration_text = scene["narration"]
        print(f"   Cena {i + 1:02d}: {narration_text[:60]}...", end="", flush=True)
        path = generate_narration(narration_text, audio_file)
        audio_paths.append(path)
        print(" ✅")

    # ── ETAPA 3: Imagens via Pexels ─────────────────────────────────────────
    print("\n🖼️ [3/4] Buscando imagens no Pexels...")
    image_paths = []
    for i, scene in enumerate(script["scenes"]):
        keywords = scene.get("image_keywords", "colorful children education")
        img_path = fetch_image(keywords, i, run_dir)
        image_paths.append(img_path)
        status = "✅" if img_path else "🎨 fallback colorido"
        print(f"   Cena {i + 1:02d}: [{status}] '{keywords}'")

    # ── ETAPA 4: Composição do vídeo ─────────────────────────────────────────
    print("\n🎬 [4/4] Compondo o vídeo...")
    video_filename = f"video_{timestamp}.mp4"
    video_path = compose_video(script, audio_paths, image_paths, run_dir, video_filename)
    print(f"\n   ✅ Vídeo gerado: {video_path}")

    # ── ETAPA 5: Upload (opcional) ───────────────────────────────────────────
    if upload:
        print("\n📤 [5/5] Fazendo upload no YouTube Studio...")
        print("   O Chrome vai abrir. Se necessário, faça login.")
        success = upload_to_youtube(
            video_path=video_path,
            title=script["title"],
            description=script.get("description", topic),
            tags=script.get("tags", ["infantil", "educativo"]),
            headless=False,
        )
        if success:
            print("\n🎉 Pipeline completo! Vídeo publicado no YouTube.")
        else:
            print("\n⚠️  Upload incompleto. Verifique o YouTube Studio.")
    else:
        print(f"\n✅ Pipeline concluído!")
        print(f"   Vídeo: {video_path}")
        print(f"   Para publicar: python main.py --topic '{topic}' --upload")


def main():
    parser = argparse.ArgumentParser(
        description="YouTube Agent — Cria vídeos educativos infantis sem custo de API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python main.py --topic alfabeto
  python main.py --topic numeros --duration 120 --upload
  python main.py --topic "bichos da floresta" --duration 90
  python main.py --topic higiene --dry-run
  python main.py --list-topics
        """,
    )
    parser.add_argument(
        "--topic", "-t",
        type=str,
        help="Tema do vídeo. Use um dos temas pré-definidos ou escreva o seu.",
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=90,
        help="Duração aproximada em segundos (padrão: 90)",
    )
    parser.add_argument(
        "--upload", "-u",
        action="store_true",
        help="Fazer upload automático no YouTube após gerar o vídeo",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Gera apenas o roteiro (rápido, para validar o tema)",
    )
    parser.add_argument(
        "--list-topics",
        action="store_true",
        help="Listar os temas pré-definidos disponíveis",
    )

    args = parser.parse_args()

    if args.list_topics:
        print("\n📚 Temas pré-definidos (use com --topic <chave>):\n")
        for key, desc in TOPICS.items():
            print(f"  {key:<12} → {desc}")
        print()
        return

    if not args.topic:
        parser.print_help()
        print("\n❌ Informe um tema com --topic. Use --list-topics para ver as opções.")
        sys.exit(1)

    # Expand predefined shortcut or use topic as-is
    topic = TOPICS.get(args.topic.lower(), args.topic)

    run_pipeline(
        topic=topic,
        duration=args.duration,
        upload=args.upload,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
