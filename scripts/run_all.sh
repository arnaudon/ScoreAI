#!/bin/bash

# Start FastAPI backend in reload mode
uv run uvicorn src.backend.main:app --reload --port 8000  &

# Start Streamlit frontend
uv run streamlit run src/frontend/app.py

