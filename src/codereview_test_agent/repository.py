from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from .utils import truncate_text


@dataclass(frozen=True)
class RepoSnapshot:
    root: Path
    diff: str
    files: dict[str, str]
    changed_files: list[str]


class RepositoryError(RuntimeError):
    pass


class Repository:
    def __init__(self, root: Path | str = "."):
        self.root = Path(root).resolve()

    def _run_git(self, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
        proc = subprocess.run(
            ["git", *args],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=False,
        )
        if check and proc.returncode != 0:
            raise RepositoryError(proc.stderr.strip() or f"git {' '.join(args)} failed")
        return proc

    def is_git_repo(self) -> bool:
        proc = self._run_git(["rev-parse", "--is-inside-work-tree"], check=False)
        return proc.returncode == 0 and proc.stdout.strip() == "true"

    def git_root(self) -> Path:
        if not self.is_git_repo():
            return self.root
        proc = self._run_git(["rev-parse", "--show-toplevel"])
        return Path(proc.stdout.strip()).resolve()

    def get_diff(self, base: str | None = None) -> str:
        if not self.is_git_repo():
            return ""
        if base:
            proc = self._run_git(["diff", f"{base}...HEAD"], check=False)
            if proc.returncode == 0 and proc.stdout.strip():
                return proc.stdout
        staged = self._run_git(["diff", "--staged"], check=False)
        if staged.returncode == 0 and staged.stdout.strip():
            return staged.stdout
        unstaged = self._run_git(["diff"], check=False)
        if unstaged.returncode == 0 and unstaged.stdout.strip():
            return unstaged.stdout
        last_commit = self._run_git(["show", "--stat", "--patch", "--max-count=1", "HEAD"], check=False)
        return last_commit.stdout if last_commit.returncode == 0 else ""

    def changed_files(self, base: str | None = None) -> list[str]:
        if not self.is_git_repo():
            return []
        args = ["diff", "--name-only"]
        if base:
            args.append(f"{base}...HEAD")
        proc = self._run_git(args, check=False)
        names = [x.strip() for x in proc.stdout.splitlines() if x.strip()]
        if names:
            return names
        proc = self._run_git(["diff", "--staged", "--name-only"], check=False)
        names = [x.strip() for x in proc.stdout.splitlines() if x.strip()]
        if names:
            return names
        proc = self._run_git(["show", "--pretty=", "--name-only", "HEAD"], check=False)
        return [x.strip() for x in proc.stdout.splitlines() if x.strip()]

    def list_candidate_files(self) -> list[str]:
        """Fallback for non-git directories or empty diffs."""
        ignore_parts = {
            ".git",
            ".venv",
            "venv",
            "node_modules",
            "__pycache__",
            ".pytest_cache",
            ".agent-runs",
            "dist",
            "build",
        }
        exts = {
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
            ".go",
            ".java",
            ".rs",
            ".php",
            ".rb",
            ".cs",
            ".md",
            ".yml",
            ".yaml",
            ".json",
            ".toml",
        }
        files: list[str] = []
        for p in self.root.rglob("*"):
            if not p.is_file():
                continue
            if any(part in ignore_parts for part in p.parts):
                continue
            if p.suffix.lower() in exts:
                try:
                    files.append(str(p.relative_to(self.root)))
                except ValueError:
                    files.append(str(p))
        return files[:50]

    def read_files(self, paths: list[str], max_chars_per_file: int = 12_000) -> dict[str, str]:
        result: dict[str, str] = {}
        for name in paths:
            p = (self.root / name).resolve()
            if not str(p).startswith(str(self.root)):
                continue
            if not p.exists() or not p.is_file():
                continue
            try:
                raw = p.read_bytes()
                if b"\x00" in raw[:4096]:
                    continue
                text = raw.decode("utf-8", errors="replace")
                result[name] = truncate_text(text, max_chars_per_file)
            except OSError:
                continue
        return result

    def snapshot(self, base: str | None = None, max_context_chars: int = 60_000) -> RepoSnapshot:
        diff = self.get_diff(base)
        files = self.changed_files(base)
        if not files:
            files = self.list_candidate_files()
        context = self.read_files(files)

        # Keep total prompt context bounded.
        total = 0
        bounded: dict[str, str] = {}
        for name, text in context.items():
            remaining = max_context_chars - total
            if remaining <= 0:
                break
            bounded[name] = truncate_text(text, remaining)
            total += len(bounded[name])

        return RepoSnapshot(root=self.root, diff=truncate_text(diff, max_context_chars), files=bounded, changed_files=files)
