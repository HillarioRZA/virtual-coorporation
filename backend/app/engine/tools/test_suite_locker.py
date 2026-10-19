"""
Adversarial TDD Test Suite Locker Tool.
Menulis skenario pengujian unit, mengunci izin berkas (chmod 444), dan mendaftarkan read-only guardrails.
"""

from pathlib import Path
from typing import Any, Dict, Optional
from app.core.logger import logger


PROJECTS_OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "projects_output"


def lock_test_suite(
    project_id: str,
    test_filename: str,
    test_content: str,
    state: Optional[Any] = None,
) -> Dict[str, Any]:
    """Menyimpan berkas pengujian, mengunci izinnya (chmod 444), dan mendaftarkannya ke state read_only_files.

    Args:
        project_id: ID proyek sasaran.
        test_filename: Nama file pengujian (misal: 'test_api.py').
        test_content: Blok kode pengujian Pytest/Jest.
        state: VentureState opsional untuk mendaftarkan read_only_files.

    Returns:
        Dict status penguncian dan path file.
    """
    clean_name = Path(test_filename).name
    if not clean_name.startswith("test_") and not clean_name.endswith((".test.ts", ".test.tsx", ".spec.ts")):
        clean_name = f"test_{clean_name}"

    tests_dir = PROJECTS_OUTPUT_DIR / project_id / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    target_path = tests_dir / clean_name

    try:
        # Jika sebelumnya readonly, reset izin sementara agar bisa diperbarui oleh pemegang hak lock
        if target_path.exists():
            target_path.chmod(0o666)
        target_path.write_text(test_content, encoding="utf-8")
        target_path.chmod(0o444)
        logger.info(f"Adversarial TDD: Berkas [{clean_name}] berhasil ditulis dan dikunci (chmod 444).")
    except OSError as err:
        logger.error(f"Gagal mengunci berkas pengujian [{clean_name}]: {err}")
        return {"status": "ERROR", "error": str(err)}

    rel_keys = [clean_name, f"tests/{clean_name}", f"backend/tests/{clean_name}"]
    if state and hasattr(state, "read_only_files"):
        for k in rel_keys:
            if k not in state.read_only_files:
                state.read_only_files.append(k)

    return {
        "status": "LOCKED",
        "file_name": clean_name,
        "file_path": str(target_path),
        "permissions": "0444 (read-only)",
    }
