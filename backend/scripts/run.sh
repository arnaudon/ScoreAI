#!/bin/bash

# Start FastAPI backend in reload mode
uv run --frozen uvicorn app.main:app --reload --port 8000
