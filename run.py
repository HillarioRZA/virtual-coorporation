"""
Universal Backend Server Launcher.
Menjalankan server FastAPI backend pada host 127.0.0.1 dan port 8000 dengan auto-reload.
"""

import sys
from pathlib import Path
import uvicorn

# Daftarkan direktori backend ke sys.path secara eksplisit
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def main() -> None:
    """Fungsi utama untuk meluncurkan uvicorn server."""
    uvicorn.run(
        "main:app",
        app_dir=str(BACKEND_DIR),
        host="127.0.0.1",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
