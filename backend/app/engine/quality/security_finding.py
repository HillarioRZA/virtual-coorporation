"""
Security Finding Data Model.
Merepresentasikan temuan kerentanan keamanan kode terstruktur dari AST static code analyzer.
"""

from typing import Any, Dict


class SecurityFinding:
    """Representasi temuan kerentanan keamanan kode terstruktur."""

    def __init__(
        self,
        rule_id: str,
        title: str,
        severity: str,
        file_path: str,
        line_number: int,
        description: str,
        remediation: str,
    ) -> None:
        self.rule_id = rule_id
        self.title = title
        self.severity = severity
        self.file_path = file_path
        self.line_number = line_number
        self.description = description
        self.remediation = remediation

    def to_dict(self) -> Dict[str, Any]:
        """Mengonversi temuan keamanan ke format dictionary JSON."""
        return {
            "rule_id": self.rule_id,
            "title": self.title,
            "severity": self.severity,
            "file": self.file_path,
            "line": self.line_number,
            "description": self.description,
            "remediation": self.remediation,
        }
