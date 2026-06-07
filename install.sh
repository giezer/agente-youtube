#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# YouTube Agent — Script de instalação
# ─────────────────────────────────────────────────────────────────
set -e

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  🎬  YouTube Agent — Instalação                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ── Python ───────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.10+."
    exit 1
fi
PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python $PYTHON_VER"

# ── Virtualenv ───────────────────────────────────────────────────
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# shellcheck disable=SC1091
source venv/bin/activate
echo "✅ Ambiente virtual ativado"

# ── Dependências Python ──────────────────────────────────────────
echo "📦 Instalando dependências Python..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "✅ Dependências instaladas"

# ── FFmpeg ───────────────────────────────────────────────────────
if ! command -v ffmpeg &>/dev/null; then
    echo ""
    echo "⚠️  FFmpeg não encontrado. Instalando..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y ffmpeg
    elif command -v brew &>/dev/null; then
        brew install ffmpeg
    else
        echo "   Instale manualmente: https://ffmpeg.org/download.html"
    fi
else
    echo "✅ FFmpeg $(ffmpeg -version 2>&1 | head -1 | awk '{print $3}')"
fi

# ── Google Chrome ─────────────────────────────────────────────────
if ! command -v google-chrome &>/dev/null && ! command -v chromium-browser &>/dev/null; then
    echo ""
    echo "⚠️  Chrome/Chromium não encontrado (necessário para upload)."
    echo "   Instale em: https://www.google.com/chrome/"
    echo "   Ou: sudo apt install chromium-browser"
else
    echo "✅ Chrome/Chromium disponível"
fi

# ── Ollama ───────────────────────────────────────────────────────
echo ""
if command -v ollama &>/dev/null; then
    echo "✅ Ollama instalado"
    echo "   Baixando modelo llama3.2 (se ainda não tiver)..."
    ollama pull llama3.2
else
    echo "⚠️  Ollama não encontrado."
    echo "   Instale em: https://ollama.com"
    echo "   Depois execute: ollama pull llama3.2"
fi

# ── Arquivo .env ─────────────────────────────────────────────────
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "📋 Arquivo .env criado!"
    echo "   ✏️  IMPORTANTE: Edite o .env e adicione sua chave do Pexels."
    echo "   👉 Crie conta gratuita em: https://www.pexels.com/api/"
else
    echo "✅ .env já existe"
fi

# ── Finalização ───────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  ✅  Instalação concluída!                           ║"
echo "║                                                      ║"
echo "║  Próximos passos:                                    ║"
echo "║  1. Edite o .env com sua chave do Pexels             ║"
echo "║  2. Inicie o Ollama:  ollama serve                   ║"
echo "║  3. Teste o roteiro:                                 ║"
echo "║     source venv/bin/activate                         ║"
echo "║     python main.py --topic alfabeto --dry-run        ║"
echo "║  4. Gere o vídeo completo:                           ║"
echo "║     python main.py --topic alfabeto                  ║"
echo "║  5. Gere e publique no YouTube:                      ║"
echo "║     python main.py --topic alfabeto --upload         ║"
echo "║                                                      ║"
echo "║  Listar todos os temas:                              ║"
echo "║     python main.py --list-topics                     ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
