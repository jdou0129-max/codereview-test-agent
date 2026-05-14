from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .utils import ensure_dir, timestamp


@dataclass(frozen=True)
class CodeBlock:
    language: str
    path: str | None
    code: str


FENCE_RE = re.compile(
    r"```(?P<header>[^\n`]*)\n(?P<code>.*?)\n```",
    re.DOTALL | re.MULTILINE,
)
PATH_RE = re.compile(r"path\s*=\s*[\"'](?P<path>[^\"']+)[\"']|path\s*=\s*(?P<path2>\S+)")


def extract_code_blocks(markdown: str) -> list[CodeBlock]:
    blocks: list[CodeBlock] = []
    for match in FENCE_RE.finditer(markdown):
        header = match.group("header").strip()
        code = match.group("code")
        parts = header.split()
        language = parts[0] if parts else ""
        path: str | None = None
        path_match = PATH_RE.search(header)
        if path_match:
            path = path_match.group("path") or path_match.group("path2")
        blocks.append(CodeBlock(language=language, path=path, code=code.rstrip() + "\n"))
    return blocks


def create_run_dir(root: Path, name: str | None = None) -> Path:
    dirname = name or timestamp()
    return ensure_dir(root / ".agent-runs" / dirname)


def write_markdown(path: Path, content: str) -> Path:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")
    return path


def write_first_code_block(markdown: str, target_path: Path) -> Path:
    blocks = extract_code_blocks(markdown)
    if not blocks:
        raise ValueError("No fenced code block found in LLM output.")
    block = blocks[0]
    ensure_dir(target_path.parent)
    target_path.write_text(block.code, encoding="utf-8")
    return target_path


def write_path_code_blocks(markdown: str, root: Path) -> list[Path]:
    written: list[Path] = []
    for block in extract_code_blocks(markdown):
        if not block.path:
            continue
        target = (root / block.path).resolve()
        if not str(target).startswith(str(root.resolve())):
            continue
        ensure_dir(target.parent)
        target.write_text(block.code, encoding="utf-8")
        written.append(target)
    return written
