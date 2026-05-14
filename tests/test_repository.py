from pathlib import Path

from codereview_test_agent.repository import Repository


def test_list_candidate_files(tmp_path: Path):
    (tmp_path / "a.py").write_text("print('hello')", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "ignored.py").write_text("x=1", encoding="utf-8")
    repo = Repository(tmp_path)
    files = repo.list_candidate_files()
    assert "a.py" in files
    assert all("node_modules" not in f for f in files)


def test_snapshot_non_git(tmp_path: Path):
    (tmp_path / "a.py").write_text("def f(): return 1", encoding="utf-8")
    repo = Repository(tmp_path)
    snap = repo.snapshot()
    assert "a.py" in snap.files
