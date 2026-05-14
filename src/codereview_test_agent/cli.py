from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .agent import CodeReviewTestAgent
from .config import get_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codereview-agent",
        description="AI Code Review and Unit Test Generation Agent",
    )
    parser.add_argument("--root", default=".", help="Project root directory. Default: current directory")
    parser.add_argument("--mock", action="store_true", help="Run without API key using deterministic mock outputs")
    parser.add_argument("--max-context", type=int, default=None, help="Max characters of repository context sent to LLM")

    sub = parser.add_subparsers(dest="command", required=True)

    review = sub.add_parser("review", help="Review git diff and source context")
    review.add_argument("--base", default=None, help="Base branch/ref, e.g. main")
    review.add_argument("--output", default=None, help="Output Markdown path")

    gen = sub.add_parser("generate-tests", help="Generate unit tests from diff and context")
    gen.add_argument("--base", default=None, help="Base branch/ref, e.g. main")
    gen.add_argument("--framework", default="pytest", help="Test framework, e.g. pytest, jest, vitest")
    gen.add_argument("--target", default="tests/test_generated_by_agent.py", help="Target test file path")
    gen.add_argument("--write", action="store_true", help="Write generated test code to target file")
    gen.add_argument("--output", default=None, help="Output Markdown path")

    run = sub.add_parser("run-tests", help="Run a local test command and save logs")
    run.add_argument("--cmd", required=True, help='Test command, e.g. "python -m pytest -q"')
    run.add_argument("--output-log", default=None, help="Output log path")
    run.add_argument("--timeout", type=int, default=180, help="Timeout seconds")

    fix = sub.add_parser("fix-from-log", help="Analyze test failure log and suggest fixes")
    fix.add_argument("--log", required=True, help="Path to test log")
    fix.add_argument("--base", default=None, help="Base branch/ref, e.g. main")
    fix.add_argument("--output", default=None, help="Output Markdown path")

    all_cmd = sub.add_parser("all", help="Run review -> generate tests -> run tests -> fix if failed")
    all_cmd.add_argument("--base", default=None, help="Base branch/ref, e.g. main")
    all_cmd.add_argument("--framework", default="pytest", help="Test framework")
    all_cmd.add_argument("--target", default="tests/test_generated_by_agent.py", help="Target test file path")
    all_cmd.add_argument("--write-tests", action="store_true", help="Write generated tests")
    all_cmd.add_argument("--test-cmd", default="python -m pytest -q", help="Test command")
    all_cmd.add_argument("--timeout", type=int, default=180, help="Timeout seconds")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = get_settings(max_context_chars=args.max_context)
    agent = CodeReviewTestAgent(root=args.root, settings=settings, mock=args.mock)

    try:
        if args.command == "review":
            out = agent.review(base=args.base, output=Path(args.output) if args.output else None)
            print(f"Review report written: {out}")
            return 0

        if args.command == "generate-tests":
            out, written = agent.generate_tests(
                framework=args.framework,
                target=Path(args.target),
                base=args.base,
                write=args.write,
                output=Path(args.output) if args.output else None,
            )
            print(f"Generated test report written: {out}")
            for path in written:
                print(f"Generated test file written: {path}")
            if not args.write:
                print("No files changed. Add --write to write generated test code.")
            return 0

        if args.command == "run-tests":
            result = agent.run_tests(
                command=args.cmd,
                output_log=Path(args.output_log) if args.output_log else None,
                timeout_seconds=args.timeout,
            )
            print(result.combined_output)
            print(f"Test log written: {result.log_path}")
            return result.returncode

        if args.command == "fix-from-log":
            out = agent.fix_from_log(
                log_path=Path(args.log),
                base=args.base,
                output=Path(args.output) if args.output else None,
            )
            print(f"Fix suggestion report written: {out}")
            return 0

        if args.command == "all":
            review_out = agent.review(base=args.base)
            print(f"Review report written: {review_out}")
            tests_out, written = agent.generate_tests(
                framework=args.framework,
                target=Path(args.target),
                base=args.base,
                write=args.write_tests,
            )
            print(f"Generated test report written: {tests_out}")
            for path in written:
                print(f"Generated test file written: {path}")
            result = agent.run_tests(command=args.test_cmd, timeout_seconds=args.timeout)
            print(f"Test log written: {result.log_path}")
            if not result.ok and result.log_path:
                fix_out = agent.fix_from_log(log_path=result.log_path, base=args.base)
                print(f"Fix suggestion report written: {fix_out}")
            return result.returncode

        raise AssertionError(f"Unknown command: {args.command}")
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
