"""Application configuration utilities."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = "sqlite:///./backend/data/app.db"
