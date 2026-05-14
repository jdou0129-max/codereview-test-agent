#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python -m pip install -e . >/dev/null
codereview-agent review --mock
codereview-agent generate-tests --mock --target tests/test_generated_by_agent.py --write
codereview-agent run-tests --cmd "python -m pytest -q"
