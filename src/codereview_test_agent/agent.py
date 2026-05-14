from __future__ import annotations

from pathlib import Path

from .config import Settings
from .llm import ChatMessage, LLMClient
from .prompts import SYSTEM_PROMPT, fix_prompt, review_prompt, test_generation_prompt
from .repository import Repository
from .report import create_run_dir, write_first_code_block, write_markdown, write_path_code_blocks
from .test_runner import TestRunner, TestRunResult
from .utils import read_text_file, truncate_text


class CodeReviewTestAgent:
    def __init__(self, root: Path | str, settings: Settings, mock: bool = False):
        self.root = Path(root).resolve()
        self.settings = settings
        self.repo = Repository(self.root)
        self.llm = LLMClient(settings, mock=mock)

    def _chat(self, user_prompt: str) -> str:
        return self.llm.chat(
            [
                ChatMessage(role="system", content=SYSTEM_PROMPT),
                ChatMessage(role="user", content=user_prompt),
            ]
        )

    def review(self, base: str | None = None, output: Path | None = None) -> Path:
        run_dir = output.parent if output else create_run_dir(self.root)
        out = output or (run_dir / "review.md")
        snapshot = self.repo.snapshot(base=base, max_context_chars=self.settings.max_context_chars)
        content = self._chat(review_prompt(snapshot))
        return write_markdown(out, content)

    def generate_tests(
        self,
        framework: str,
        target: Path,
        base: str | None = None,
        write: bool = False,
        output: Path | None = None,
        prefer_path_blocks: bool = True,
    ) -> tuple[Path, list[Path]]:
        run_dir = output.parent if output else create_run_dir(self.root)
        out = output or (run_dir / "generated_tests.md")
        snapshot = self.repo.snapshot(base=base, max_context_chars=self.settings.max_context_chars)
        content = self._chat(test_generation_prompt(snapshot, framework=framework, target_path=str(target)))
        write_markdown(out, content)
        written: list[Path] = []
        if write:
            if prefer_path_blocks:
                written = write_path_code_blocks(content, self.root)
            if not written:
                written = [write_first_code_block(content, self.root / target)]
        return out, written

    def fix_from_log(self, log_path: Path, base: str | None = None, output: Path | None = None) -> Path:
        run_dir = output.parent if output else create_run_dir(self.root)
        out = output or (run_dir / "fix_suggestions.md")
        snapshot = self.repo.snapshot(base=base, max_context_chars=self.settings.max_context_chars)
        log = read_text_file(log_path, max_chars=30_000)
        content = self._chat(fix_prompt(snapshot, truncate_text(log, 30_000)))
        return write_markdown(out, content)

    def run_tests(self, command: str, output_log: Path | None = None, timeout_seconds: int = 180) -> TestRunResult:
        run_dir = output_log.parent if output_log else create_run_dir(self.root)
        log_path = output_log or (run_dir / "test.log")
        return TestRunner(self.root).run(command, timeout_seconds=timeout_seconds, log_path=log_path)
