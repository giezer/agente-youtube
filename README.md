# 🎬 YouTube Agent — Criador Automático de Vídeos Infantis

> Cria vídeos educativos no estilo **Cocomelon** automaticamente — do roteiro ao upload no YouTube — sem pagar nenhuma API.

---

## 📋 O que esse projeto faz?

Você escolhe um **tema** (ex: "alfabeto", "números", "animais") e o agente faz tudo sozinho:

1. 🤖 **Escreve o roteiro** — Uma IA local cria as cenas com narração em português
2. 🎙️ **Gera a narração** — Uma voz feminina brasileira lê o texto automaticamente
3. 🖼️ **Busca as imagens** — Encontra imagens coloridas e infantis automaticamente
4. 🎬 **Monta o vídeo** — Junta tudo num vídeo estilo Cocomelon com texto colorido
5. 📤 **Publica no YouTube** — Abre o Chrome e faz o upload sozinho *(opcional)*

---

## 💻 Linux ou Windows? Qual usar?

| | Linux (Ubuntu/WSL) | Windows |
|---|---|---|
| **Recomendado?** | ✅ **Sim, melhor opção** | ⚠️ Funciona, mas com mais configuração |
| Instalação | Simples, um comando | Requer ajustes manuais |
| Ollama (IA local) | Funciona perfeitamente | Funciona, mas pode ser mais lento |
| FFmpeg (vídeo) | `sudo apt install ffmpeg` | Download manual necessário |
| Selenium (Chrome) | Funciona | Funciona |

> **Recomendação para iniciantes:** Use **Linux (Ubuntu)** ou **WSL no Windows** (Windows Subsystem for Linux). Se você usa Windows, instale o WSL seguindo [este guia da Microsoft](https://learn.microsoft.com/pt-br/windows/wsl/install) — é gratuito e funciona dentro do próprio Windows.

---

## ✅ O que você precisa ter instalado

Antes de começar, verifique se tem estes programas:

| Programa | Para que serve | Como instalar |
|---|---|---|
| **Python 3.10+** | Rodar o projeto | [python.org](https://www.python.org/downloads/) |
| **Git** | Baixar o projeto | [git-scm.com](https://git-scm.com/downloads) |
| **Ollama** | IA local para gerar roteiros | [ollama.com](https://ollama.com) |
| **Google Chrome** | Para fazer upload no YouTube | [google.com/chrome](https://www.google.com/chrome/) |
| **FFmpeg** | Para montar os vídeos | Veja abaixo |

### Instalar o FFmpeg

**Linux/WSL:**
```bash
sudo apt update && sudo apt install ffmpeg -y
```

**Windows:** Baixe em [ffmpeg.org/download.html](https://ffmpeg.org/download.html) e adicione ao PATH.

---

## 🚀 Instalação passo a passo

### Passo 1 — Baixe o projeto

Abra o terminal e execute:

```bash
git clone https://github.com/seu-usuario/youtube-agent.git
cd youtube-agent
```

> Se você não tem o projeto no GitHub ainda, navegue até a pasta onde está o projeto:
> ```bash
> cd /home/wsl/github/youtube-agent
> ```

---

### Passo 2 — Execute o instalador automático

```bash
bash install.sh
```

Esse script faz automaticamente:
- Cria o ambiente virtual Python
- Instala todas as bibliotecas necessárias
- Cria o arquivo `.env` de configuração
- Verifica se FFmpeg e Chrome estão instalados

---

### Passo 3 — Configure a chave do Pexels (imagens gratuitas)

O Pexels fornece imagens gratuitamente — só precisa criar uma conta:

1. Acesse [pexels.com/api](https://www.pexels.com/api/)
2. Crie uma conta gratuita
3. Copie sua chave de API
4. Abra o arquivo `.env` na pasta do projeto:

```bash
nano .env
```

5. Substitua `cole_sua_chave_aqui` pela sua chave:

```
PEXELS_API_KEY=SuaChaveAqui123456789
```

6. Salve com `Ctrl+O` → `Enter` → `Ctrl+X`

> **Sem a chave do Pexels** o projeto ainda funciona! Usará fundos coloridos no lugar das imagens.

---

### Passo 4 — Instale a IA local (Ollama)

```bash
# Instalar o Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Baixar o modelo de linguagem (faz isso só uma vez, ~2GB)
ollama pull llama3.2
```

---

### Passo 5 — Inicie a IA local

Abra um **terminal separado** e deixe esse comando rodando:

```bash
ollama serve
```

> Deixe esse terminal aberto enquanto usa o YouTube Agent. Ele é a "cabeça pensante" que escreve os roteiros.

---

## 🎮 Como usar — Guia prático

Abra um novo terminal, ative o ambiente virtual e use o projeto:

```bash
cd /home/wsl/github/youtube-agent
source venv/bin/activate
```

---

### Listar os temas disponíveis

```bash
python main.py --list-topics
```

Saída esperada:
```
📚 Temas pré-definidos:

  alfabeto     → Vamos aprender o Alfabeto! As letras de A a Z com imagens divertidas
  numeros      → Aprendendo os Números de 1 a 10 - Vamos contar juntos!
  animais      → Os Animais da Fazenda - Boi, Cavalo, Galinha e muito mais
  cores        → Aprendendo as Cores do Arco-Íris - Vermelho, Azul, Verde...
  frutas       → Frutas Deliciosas! Maçã, Banana, Uva, Laranja e mais
  corpo        → Partes do Corpo Humano - Cabeça, Mãos, Pés e mais!
  higiene      → Hora de Escovar os Dentes! Cuidando da Saúde com Alegria
  banho        → Hora do Banho! Aprendendo a Se Cuidar Sozinho
  banheiro     → Aprendendo a Usar o Banheiro Sozinho - Grandes Conquistas!
  palavras     → Primeiras Palavras em Português - Mamãe, Papai, Água, Leite
  formas       → Formas Geométricas - Círculo, Quadrado, Triângulo e mais
  dias         → Os Dias da Semana - Segunda, Terça, Quarta... Vamos aprender!
```

---

### Testar antes de gerar o vídeo (`--dry-run`)

Use esse modo para ver apenas o roteiro gerado, sem criar o vídeo. Rápido e útil para validar o tema:

```bash
python main.py --topic alfabeto --dry-run
```

O roteiro será salvo em `output/<data_hora>/script.json`. Abra para conferir antes de gerar o vídeo completo.

---

### Gerar um vídeo completo

Com um dos **temas pré-definidos**:
```bash
python main.py --topic alfabeto
```

Com um **tema personalizado** (escreva em português):
```bash
python main.py --topic "Os dinossauros e seus nomes"
python main.py --topic "Como plantar uma flor"
python main.py --topic "Os meios de transporte"
```

Controlando a **duração** (padrão: 90 segundos):
```bash
python main.py --topic numeros --duration 120
python main.py --topic cores --duration 60
```

---

### Gerar o vídeo E publicar no YouTube automaticamente

```bash
python main.py --topic alfabeto --upload
```

Na **primeira vez** que usar `--upload`:
1. O Chrome abrirá automaticamente
2. Você verá a tela de login do Google
3. Faça login na conta do YouTube onde quer publicar
4. Pressione **Enter** no terminal
5. O agente assumirá e fará o upload sozinho

Nas próximas vezes, o login estará salvo e o upload acontece sem interação.

---

### Tabela resumida dos comandos

| O que fazer | Comando |
|---|---|
| Ver os temas disponíveis | `python main.py --list-topics` |
| Testar apenas o roteiro | `python main.py --topic alfabeto --dry-run` |
| Gerar vídeo (tema pré-definido) | `python main.py --topic animais` |
| Gerar vídeo (tema personalizado) | `python main.py --topic "seu tema aqui"` |
| Gerar vídeo mais longo | `python main.py --topic cores --duration 120` |
| Gerar e publicar no YouTube | `python main.py --topic higiene --upload` |

---

## 📁 Onde ficam os vídeos gerados?

Cada execução cria uma pasta nova dentro de `output/`:

```
youtube-agent/
└── output/
    └── 20260605_143022/          ← data e hora da execução
        ├── script.json           ← roteiro gerado pela IA
        ├── audio_00.mp3          ← narração da cena 1
        ├── audio_01.mp3          ← narração da cena 2
        ├── img_00.jpg            ← imagem da cena 1
        ├── img_01.jpg            ← imagem da cena 2
        └── video_20260605.mp4    ← vídeo final ← AQUI!
```

---

## 🔧 Configurações avançadas (arquivo `.env`)

```env
# Chave gratuita do Pexels para buscar imagens
PEXELS_API_KEY=sua_chave_aqui

# Modelo de IA local (llama3.2 é leve e rápido)
# Alternativas: mistral, gemma2:2b (mais leves), llama3.1:8b (melhor qualidade)
OLLAMA_MODEL=llama3.2

# Endereço do Ollama (não mude, a menos que saiba o que faz)
OLLAMA_HOST=http://localhost:11434

# Voz da narração em português brasileiro
# Opções: pt-BR-FranciscaNeural (feminina), pt-BR-AntonioNeural (masculina)
TTS_VOICE=pt-BR-FranciscaNeural
```

---

## ❓ Perguntas frequentes

**Preciso pagar alguma coisa?**
> Não. O Ollama (IA) roda no seu computador, o edge-tts usa os servidores gratuitos da Microsoft, o Pexels tem plano gratuito e o Selenium usa o seu próprio Chrome.

**O vídeo vai para o YouTube mesmo sem minha permissão?**
> Não. O upload só acontece se você usar `--upload` no comando. Sem esse parâmetro, o vídeo fica salvo na pasta `output/` do seu computador.

**A IA precisa de internet?**
> O Ollama (roteiro) funciona **offline**, no seu próprio PC. Apenas o edge-tts (voz) e o Pexels (imagens) precisam de internet.

**Quanto tempo leva para gerar um vídeo?**
> Depende do seu computador. Em média:
> - Roteiro: 30 a 90 segundos (depende do Ollama)
> - Narração: 20 a 40 segundos
> - Imagens: 15 a 30 segundos
> - Composição do vídeo: 1 a 3 minutos
> - Total: **2 a 5 minutos** por vídeo

**Posso mudar a voz para masculina?**
> Sim. No arquivo `.env`, altere para:
> ```
> TTS_VOICE=pt-BR-AntonioNeural
> ```

**O Ollama está lento. O que fazer?**
> Tente um modelo menor. No arquivo `.env`, altere:
> ```
> OLLAMA_MODEL=gemma2:2b
> ```
> Depois execute: `ollama pull gemma2:2b`

**Como adicionar um novo tema que não está na lista?**
> Basta escrever diretamente no `--topic`:
> ```bash
> python main.py --topic "Como fazer bolo de chocolate"
> python main.py --topic "Os planetas do sistema solar"
> ```

---

## 🆘 Problemas comuns e soluções

| Erro | Causa provável | Solução |
|---|---|---|
| `Connection refused` no Ollama | Ollama não está rodando | Execute `ollama serve` em outro terminal |
| `ModuleNotFoundError` | Ambiente virtual não ativado | Execute `source venv/bin/activate` |
| Vídeo sem imagens (só fundo colorido) | Chave do Pexels não configurada | Edite o `.env` com sua chave |
| Chrome não abre para upload | Chrome não instalado | Instale o Google Chrome |
| `ffmpeg not found` | FFmpeg não instalado | `sudo apt install ffmpeg` |

---

## 🏗️ Estrutura do projeto (para quem quer entender o código)

```
youtube-agent/
├── main.py                   ← Ponto de entrada. Execute este arquivo
├── config.py                 ← Lê as configurações do .env
├── requirements.txt          ← Lista de bibliotecas necessárias
├── .env                      ← Suas chaves e configurações (não compartilhe!)
├── .env.example              ← Modelo do .env sem as chaves reais
├── install.sh                ← Script de instalação automática
└── pipeline/
    ├── script_generator.py   ← Chama o Ollama e gera o roteiro
    ├── tts_generator.py      ← Converte texto em fala (edge-tts)
    ├── image_fetcher.py      ← Busca imagens no Pexels
    ├── video_composer.py     ← Monta o vídeo com MoviePy e Pillow
    └── uploader.py           ← Abre o Chrome e faz o upload no YouTube
```

---

## 📄 Licença

MIT — Uso livre para projetos pessoais e educativos.
