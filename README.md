# ScoreAI

ScoreAI is an AI‑assisted music score library and practice companion.

It lets you build a personal database of PDF scores, browse and filter them, track what you play, and get suggestions and context from an AI assistant – all through a web UI.

---

## Features

- **Score library**
  - Add PDF scores with metadata (title, composer, year, period, genre, etc.).
  - Store everything in a database tied to your user account.
  - Track how often each score is played.

- **Rich PDF experience**
  - View scores in a Streamlit-based PDF reader.
  - Navigate pages comfortably for practice sessions.
  - Keep multiple scores open with cached viewers.

- **AI assistant for musicians**
  - Ask for help choosing what to play.
  - Get random suggestions filtered by composer.
  - Receive contextual information about your repertoire.
  - Conversations are powered by `pydantic-ai` and related tools.

- **User accounts & authentication**
  - Create user accounts stored in the database.
  - Secure passwords using Argon2 hashing.
  - JWT-based authentication for the API.
  - Per-user score libraries (you only see your own scores).

- **Modern Python stack**
  - **Backend**: FastAPI, SQLModel, SQLite (by default).
  - **Frontend**: Streamlit UI.
  - **Shared**: Pydantic/SQLModel models shared across services.
  - **Tooling**: `uv` workspace, pytest, black, pylint, mypy.

---

## Monorepo layout

```text
ScoreAI/
├─ backend/           # FastAPI backend (API, auth, DB, AI agent)
│  ├─ app/
│  │  ├─ main.py      # FastAPI app, routes for scores & agent
│  │  ├─ db.py        # Database engine & session handling
│  │  ├─ users.py     # User CRUD and JWT auth
│  │  └─ agent.py     # LLM agent (pydantic-ai)
│  ├─ scripts/
│  │  └─ run.sh       # Run backend in dev mode
│  └─ tests/          # Backend unit tests
├─ frontend/          # Streamlit frontend
│  ├─ ui/
│  │  ├─ app.py       # Main navigation & login
│  │  ├─ reader.py    # PDF score viewer
│  │  ├─ database.py  # Score database view
│  │  └─ ...          # Components, locales, account page, etc.
│  ├─ scripts/
│  │  └─ run.sh       # Run frontend in dev mode
│  └─ tests/          # Frontend tests
├─ shared/            # Shared models and logic
│  ├─ shared/
│  │  ├─ scores.py    # Score + Scores models (SQLModel + Pydantic)
│  │  ├─ user.py      # User model (SQLModel)
│  │  └─ responses.py # Response / FullResponse models for the agent
│  └─ tests/          # Shared-code tests
├─ compose.yaml       # Docker Compose for backend + frontend
├─ Dockerfile.backend
├─ Dockerfile.frontend
├─ pyproject.toml     # uv workspace definition
└─ uv.lock
```

The workspace is managed via `uv`, with three members: `backend`, `frontend`, and `shared`.

---

## Getting started

### Prerequisites

- Python **3.12+**
- [`uv`](https://github.com/astral-sh/uv) installed
- (Optional) Docker and Docker Compose (for containerized runs)

### 1. Install dependencies

From the repository root:

```bash
uv sync
```

This installs dependencies for the whole workspace (`backend`, `frontend`, `shared`).

---

## Running the app (local dev, without Docker)

You can run backend and frontend separately, each via its helper script.

### Backend (FastAPI API)

From the repo root:

```bash
cd backend
./scripts/run.sh
```

This starts a FastAPI server (with reload) on port **8000**:

- API root: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`

By default, it uses an SQLite database (see `DATABASE_URL` below).

### Frontend (Streamlit UI)

In another terminal:

```bash
cd frontend
./scripts/run.sh
```

This starts the Streamlit app (by default on port **8501**):

- UI: `http://localhost:8501`

Log in, browse your score database, open a score in the reader, and interact with the AI assistant.

---

## Running with Docker Compose

You can also run everything via Docker:

```bash
docker compose up --build
```

This will:

- Build backend and frontend images using `Dockerfile.backend` and `Dockerfile.frontend`.
- Start:
  - Backend on `http://localhost:8000`
  - Frontend on `http://localhost:8501`
- Mount local directories (so code changes are reflected in containers):
  - `./backend` and `./shared` into the backend container
  - `./frontend` and `./data` into the frontend container
  - `./database` as SQLite storage for the backend

Make sure you have a `.env` file in the repo root before running (see next section).

---

## Configuration

### Environment variables

Some useful environment variables:

- **Backend**
  - `DATABASE_URL`  
    - Default: `sqlite:///database/app.db` (local dev)  
    - In `compose.yaml`, this is set to `sqlite:///database/database.db`.

  - `MODEL`  
    - LLM identifier for the pydantic-ai agent.  
    - Default: `google-gla:gemini-2.5-flash-lite`.

- **Frontend (in Docker Compose)**
  - `API_URL`  
    - URL used by the frontend to reach the backend.  
    - Default in `compose.yaml`: `http://backend:8000`.

  - `DATA_PATH`  
    - Path inside the container where PDFs are stored.  
    - Default: `/app/data`.

Create a `.env` file in the project root and set any overrides you need (e.g. DB path, model name, etc.). The `compose.yaml` file automatically loads `.env`.

---

## Development workflow

### Running tests

Each package has its own test suite. From the repo root:

```bash
# Backend tests
cd backend
uv run --frozen pytest

# Frontend tests
cd ../frontend
uv run --frozen pytest

# Shared tests
cd ../shared
uv run --frozen pytest
```

### Type checking & linting

Common tools are included as dev dependencies: `mypy`, `pylint`, `black`, etc. Typical usage from a package directory:

```bash
# Type checking
uv run mypy .

# Linting
uv run pylint <your_module_or_package>

# Formatting
uv run black .
```

Run these separately in `backend`, `frontend`, and `shared` as needed.

---

## High-level architecture

- **Shared models (`shared/`)**
  - `User`, `Score`, and `Scores` are defined as SQLModel / Pydantic models.
  - `Response` and `FullResponse` define the structure of AI responses and message history.

- **Backend (`backend/app/`)**
  - Handles:
    - User sign-up and authentication (JWT).
    - CRUD operations on scores.
    - Tracking play counts.
    - Running the AI agent via `/agent` endpoint.
  - Uses:
    - FastAPI for routing and dependency injection.
    - SQLModel + SQLite for persistence.
    - `pydantic-ai` and tools for LLM interactions.

- **Frontend (`frontend/ui/`)**
  - A Streamlit app that:
    - Manages login/logout and session via cookies.
    - Shows a “Choose a score” homepage.
    - Displays a database view with filtering/search.
    - Opens a dedicated PDF reader page for a selected score.
  - Talks to the backend via an internal API layer, handling authentication tokens and caching.

---

## Roadmap / ideas

Some potential directions (many of which are already partially implemented):

- More advanced search and filtering (e.g. by difficulty, mood, instrumentation).
- Direct integration with public score libraries (e.g. IMSLP) for one-click imports.
- Richer practice analytics (time spent, repetition tracking, etc.).
- Deeper AI assistance:
  - Practice strategies.
  - Suggested fingerings or phrasing pointers.
  - Recommended listening playlists.

---

## License

See `LICENSE` for full details.
