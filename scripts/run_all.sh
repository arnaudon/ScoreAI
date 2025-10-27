#!/bin/bash

# Start FastAPI backend in reload mode
uv run --frozen uvicorn scoreai.backend.main:app --reload --port 8000  &

# Start Streamlit frontend
uv run --frozen streamlit run src/scoreai/frontend/app.py

