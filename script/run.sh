#!/bin/bash


export DATABASE_URL=sqlite:///database/database.db

# Start FastAPI backend in reload mode
uv run uvicorn backend.app.main:app --reload --port 8000 --host 0.0.0.0 &

# Start Streamlit frontend
uv run streamlit run frontend/ui/app.py & 

