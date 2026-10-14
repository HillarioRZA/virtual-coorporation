"""
FastAPI Entrypoint Compatibility Alias.
Mendukung pemanggilan uvicorn melalui app.main:app secara konsisten.
"""

from pathlib import Path
import sys

# Pastikan folder backend berada di sys.path
BACKEND_DIR = str(Path(__file__).resolve().parent.parent)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app  # noqa: F401
