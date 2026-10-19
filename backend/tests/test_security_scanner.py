"""
Unit Tests untuk Security Code Scanner (OWASP Top 10 Static Code Analyzer).
Menguji pendeteksian celah keamanan berbahaya pada Python AST dan berkas TypeScript Next.js.
"""

from pathlib import Path
import pytest
from app.engine.quality.security_scanner import StaticSecurityScanner, SecurityFinding


@pytest.mark.asyncio
async def test_security_scanner_detects_python_vulnerabilities(tmp_path: Path) -> None:
    """Menguji deteksi eval/exec, hardcoded secret, SQL injection, dan permissive CORS."""
    proj_dir = tmp_path / "proj_sec_test"
    be_dir = proj_dir / "backend"
    be_dir.mkdir(parents=True, exist_ok=True)

    vulnerable_code = '''
import os
import sqlite3

def run_dangerous(user_query, user_code):
    eval(user_code)
    secret_key = "super_insecure_hardcoded_jwt_secret_value_12345"
    db = sqlite3.connect("test.db")
    db.execute(f"SELECT * FROM users WHERE username = '{user_query}'")

app_cors = 'allow_origins=["*"]'
creds = 'allow_credentials=True'
'''
    (be_dir / "vulnerable_service.py").write_text(vulnerable_code, encoding="utf-8")

    scanner = StaticSecurityScanner(output_base_dir=tmp_path)
    res = await scanner.scan_project("proj_sec_test")

    assert res["scanned_files_count"] == 1
    assert res["vulnerabilities_count"] >= 3
    assert res["passed"] is False
    assert res["critical_count"] >= 2

    rules = [f["rule_id"] for f in res["findings"]]
    assert "OWASP-A03-CODE-INJECTION" in rules
    assert "OWASP-A07-HARDCODED-SECRET" in rules
    assert "OWASP-A03-SQL-INJECTION" in rules


@pytest.mark.asyncio
async def test_security_scanner_detects_frontend_vulnerabilities(tmp_path: Path) -> None:
    """Menguji deteksi dangerouslySetInnerHTML dan kebocoran client secret."""
    proj_dir = tmp_path / "proj_fe_sec_test"
    fe_src = proj_dir / "frontend" / "src" / "components"
    fe_src.mkdir(parents=True, exist_ok=True)

    vulnerable_fe = '''
export default function UnsafeComponent({ htmlContent }) {
    const api_key = "sk-live-abcdef1234567890abcdef1234567890";
    return <div dangerouslySetInnerHTML={{ __html: htmlContent }} />;
}
'''
    (fe_src / "Unsafe.tsx").write_text(vulnerable_fe, encoding="utf-8")

    scanner = StaticSecurityScanner(output_base_dir=tmp_path)
    res = await scanner.scan_project("proj_fe_sec_test")

    assert res["scanned_files_count"] == 1
    assert res["vulnerabilities_count"] >= 2
    assert res["passed"] is False

    rules = [f["rule_id"] for f in res["findings"]]
    assert "OWASP-A03-REACT-XSS" in rules
    assert "OWASP-A07-CLIENT-SECRET-LEAK" in rules


@pytest.mark.asyncio
async def test_security_scanner_clean_code(tmp_path: Path) -> None:
    """Menguji bahwa kode bersih dan terstandarisasi lolos pemindaian keamanan (passed=True)."""
    proj_dir = tmp_path / "proj_clean"
    be_dir = proj_dir / "backend"
    fe_dir = proj_dir / "frontend" / "src"
    be_dir.mkdir(parents=True, exist_ok=True)
    fe_dir.mkdir(parents=True, exist_ok=True)

    clean_be = '''
import os
from sqlalchemy.orm import Session

def get_user(db: Session, user_id: int):
    api_key = os.getenv("API_KEY")
    return db.query(User).filter(User.id == user_id).first()
'''
    (be_dir / "clean_service.py").write_text(clean_be, encoding="utf-8")

    clean_fe = '''
export default function SafeComponent({ text }) {
    return <div className="text-white">{text}</div>;
}
'''
    (fe_dir / "Safe.tsx").write_text(clean_fe, encoding="utf-8")

    scanner = StaticSecurityScanner(output_base_dir=tmp_path)
    res = await scanner.scan_project("proj_clean")

    assert res["scanned_files_count"] == 2
    assert res["vulnerabilities_count"] == 0
    assert res["passed"] is True
