# EpicChain Telegram Bot

An AI-powered Telegram community bot for **EpicChain**, built with Google Gemini 2.5 Pro and a Qdrant vector database for Retrieval-Augmented Generation (RAG). The bot monitors group chats, responds only when mentioned or replied to, and answers questions using an authoritative knowledge base aligned with the EpicChain brand voice.

---

## Features

- **Mention-only responses** — only activates when tagged (`@botname`) or replied to, keeping chats clean
- **RAG-powered answers** — retrieves relevant context from a Qdrant vector store before generating a response
- **Brand-aligned voice** — fintech-forward, confident, data-backed tone (Monzo/Revolut energy)
- **Guardrails built-in** — no price talk, redirects complaints to support, ignores non-questions
- **Dockerized** — one-command deployment anywhere

---

## Architecture

```
User message (Telegram)
        │
        ▼
  mention/reply check
        │
        ▼
  RAG Search (Qdrant)          ← knowledge-base.md chunks as embeddings
        │
        ▼
  Gemini 2.5 Pro (LLM)         ← system prompt + KB context + user message
        │
        ▼
  Reply to user (Telegram)
```

**Stack:**
| Component | Technology |
|---|---|
| Bot framework | `python-telegram-bot` |
| LLM | Google Gemini 2.5 Pro |
| Embeddings | `gemini-embedding-001` (3072-dim) |
| Vector DB | Qdrant Cloud |
| Runtime | Python 3.11, Docker |

---

## Project Structure

```
telegram_epicchain/
├── src/
│   ├── main.py           # Telegram bot entrypoint & handlers
│   ├── agent.py          # EpicAgent — LLM calls via Gemini
│   └── rag_engine.py     # Qdrant client, ingestion, and search
├── prompts/
│   └── agent_system_prompt.txt  # Brand voice & behavior rules
├── knowledge-base.md     # Authoritative EpicChain knowledge (edit this)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## Prerequisites

- Python 3.11+
- A Telegram Bot token from [@BotFather](https://t.me/BotFather)
- A [Google AI Studio](https://aistudio.google.com) API key (Gemini)
- A [Qdrant Cloud](https://cloud.qdrant.io) cluster (free tier works)

---

## Local Setup

**1. Clone the repo**
```bash
git clone https://github.com/malvinrusli/telegram-epicchain-bot.git
cd telegram-epicchain-bot
```

**2. Create your `.env` file**
```bash
cp .env.example .env
```
Fill in your secrets:
```env
TELEGRAM_BOT_TOKEN=your_token_here
GEMINI_API_KEY=your_key_here
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_key_here
```

**3. Run with Docker Compose**
```bash
docker compose up --build
```

Or run directly with Python:
```bash
pip install -r requirements.txt
python src/main.py
```

On startup, the bot automatically chunks and ingests `knowledge-base.md` into Qdrant.

---

## Knowledge Base

Edit `knowledge-base.md` to update what the bot knows. The file is split by `##` headers into chunks — each chunk becomes a vector in Qdrant. After editing, restart the bot and it will re-ingest automatically.

---

## Environment Variables

| Variable | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather |
| `GEMINI_API_KEY` | Google AI Studio API key |
| `QDRANT_URL` | Qdrant cluster URL |
| `QDRANT_API_KEY` | Qdrant API key |

---

## Deployment

### DigitalOcean App Platform (recommended)

The repo includes a pre-configured app spec. After pushing to GitHub, deploy with:

```bash
doctl apps create --spec .do/app.yaml
```

Then set your environment variable secrets in the DigitalOcean dashboard under **App → Settings → Environment Variables**.

### Docker (any VPS)

```bash
docker compose up -d --build
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for a full guide.

---

## Bot Behavior Rules

Defined in `prompts/agent_system_prompt.txt`:

- **Answers questions** using KB context + Gemini
- **No price talk** — redirects to: *"We don't discuss price movements in official channels."*
- **Unknown answers** — redirects to: *support@epicchain.io*
- **Non-questions** (e.g., "nice logo") → silent (`[IGNORE]` response)
- **User tagging** — always prepends `@username` to the response

---

## License

MIT
