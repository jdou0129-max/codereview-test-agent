from codereview_test_agent.utils import truncate_text


def test_truncate_text():
    text = "a" * 100
    out = truncate_text(text, 20)
    assert len(out) <= 40
    assert "truncated" in out
