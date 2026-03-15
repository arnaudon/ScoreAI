# 🎵 ScoreAI

**ScoreAI** is your personal, AI‑powered music score library and practice companion. 

Build a digital database of your PDF scores, track your practice sessions, and chat with a smart AI assistant that helps you choose what to play, auto-completes missing score info, and even searches the massive IMSLP database for you!

---

## ✨ Features

- 📚 **Smart Library**: Upload PDFs, let AI auto-complete missing metadata, and keep your repertoire organized.
- 🤖 **AI Assistant**: Chat with an LLM to discover pieces in your library, or search the massive public domain IMSLP database using natural language.
- 🎹 **Practice Reader**: Built-in distraction-free PDF viewer tailored for your practice sessions.
- 🌍 **Bilingual**: Fully available in both English and French.

---

## 🛠️ Stack

- **Frontend**: SvelteKit 5, Tailwind CSS v4, shadcn-svelte
- **Backend**: Python 3.12, FastAPI, SQLModel (PostgreSQL/SQLite)
- **AI**: `pydantic-ai` (with DuckDuckGo tools and MCP integration)
- **Tooling**: `uv` (fast Python package manager)
- **Infrastructure**: Docker Compose, Caddy (Reverse Proxy), PostgreSQL

---

## 📄 License

See `LICENSE` for full details.
