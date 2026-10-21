"""
Unit Tests untuk ProjectRepoMapper (Lightweight AST Repo Map).
Menguji ekstraksi class, method, interface, dan function dari berkas Python dan TypeScript.
"""

from pathlib import Path
import pytest
from app.engine.memory.repo_map import repo_mapper


def test_extract_python_symbols() -> None:
    """Menguji parsing AST Python untuk class dan functions."""
    py_code = """
class VentureService:
    def __init__(self):
        pass

    async def launch_project(self, name: str) -> bool:
        return True

async def standalone_handler():
    pass
"""
    symbols = repo_mapper._extract_python_symbols(py_code)
    assert any("class VentureService" in s for s in symbols)
    assert any("launch_project" in s for s in symbols)
    assert any("standalone_handler" in s for s in symbols)


def test_extract_typescript_symbols() -> None:
    """Menguji parsing regex TypeScript untuk interface, type, dan exports."""
    ts_code = """
export interface ProductConfig {
    id: string;
    name: string;
}

export type StatusType = "OPEN" | "CLOSED";

export default function ProductCard(props: ProductConfig) {
    return null;
}

export const API_BASE_URL = "http://localhost:8000";
"""
    symbols = repo_mapper._extract_typescript_symbols(ts_code)
    assert "interface ProductConfig" in symbols
    assert "type StatusType" in symbols
    assert "function ProductCard()" in symbols
    assert "const API_BASE_URL" in symbols


def test_generate_symbol_map_nonexistent_dir(tmp_path: Path) -> None:
    """Menguji bahwa direktori yang tidak ada mengembalikan None."""
    non_existent = tmp_path / "does_not_exist"
    assert repo_mapper.generate_symbol_map(non_existent) is None


def test_generate_symbol_map_with_files(tmp_path: Path) -> None:
    """Menguji pembuatan symbol map lengkap dari direktori temporer."""
    py_file = tmp_path / "service.py"
    py_file.write_text("class MyService:\n    def do_work(self):\n        pass\n", encoding="utf-8")

    ts_file = tmp_path / "Component.tsx"
    ts_file.write_text("export interface Props {}\nexport default function Component() {}\n", encoding="utf-8")

    sym_map = repo_mapper.generate_symbol_map(tmp_path)
    assert sym_map is not None
    assert "DAY-2" in sym_map
    assert "service.py" in sym_map
    assert "class MyService" in sym_map
    assert "Component.tsx" in sym_map
