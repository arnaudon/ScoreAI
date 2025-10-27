"""Configuration module"""

import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database/app.db")
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
