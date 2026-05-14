from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from .utils import ensure_dir


@dataclass(frozen=True)
class TestRunResult:
    command: str
    returncode: int
    stdout: str
    stderr: str
    log_path: Path | None = None

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    @property
    def combined_output(self) -> str:
        return f"$ {self.command}\n\nSTDOUT:\n{self.stdout}\n\nSTDERR:\n{self.stderr}\n"


class TestRunner:
    def __init__(self, cwd: Path | str = "."):
        self.cwd = Path(cwd).resolve()

    def run(self, command: str, timeout_seconds: int = 180, log_path: Path | None = None) -> TestRunResult:
        proc = subprocess.run(
            command,
            cwd=self.cwd,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        result = TestRunResult(
            command=command,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            log_path=log_path,
        )
        if log_path:
            ensure_dir(log_path.parent)
            log_path.write_text(result.combined_output, encoding="utf-8")
        return result
