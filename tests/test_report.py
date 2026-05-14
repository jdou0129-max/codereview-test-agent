from codereview_test_agent.report import extract_code_blocks


def test_extract_code_blocks_with_path():
    md = """hello
```python path=\"tests/test_demo.py\"
def test_x():
    assert True
```
"""
    blocks = extract_code_blocks(md)
    assert len(blocks) == 1
    assert blocks[0].language == "python"
    assert blocks[0].path == "tests/test_demo.py"
    assert "assert True" in blocks[0].code
