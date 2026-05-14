from __future__ import annotations


class MockLLM:
    """Deterministic LLM replacement for demos and screenshots."""

    def chat(self, messages: list[dict[str, str]]) -> str:
        joined = "\n".join(m.get("content", "") for m in messages).lower()
        if "测试代码" in joined or "generate" in joined or "unit test" in joined:
            return self._tests()
        if "失败日志" in joined or "fix" in joined or "error log" in joined:
            return self._fix()
        return self._review()

    def _review(self) -> str:
        return """# CodeReview-Test Agent Review Report

## 1. 变更总结

本次变更涉及核心业务函数的输入处理和结果返回逻辑。Agent 已读取 Git diff、相关源码文件和测试目录，并从正确性、边界条件、异常路径和可测试性四个角度完成审查。

## 2. 主要风险

| 风险 | 严重度 | 说明 | 建议 |
|---|---:|---|---|
| 输入为空或类型异常 | High | 当前逻辑可能默认信任调用方输入 | 增加参数校验和异常测试 |
| 边界值未覆盖 | Medium | 0、负数、空列表等情况容易遗漏 | 增加边界测试 |
| 错误信息不稳定 | Medium | 测试可能依赖具体报错文案 | 建议断言错误类型或错误码 |
| 缺少回归测试 | High | 后续修改可能重新引入 Bug | 为关键路径补充单元测试 |

## 3. 建议补充的测试

1. 正常输入返回正确结果；
2. 空输入或非法类型时抛出明确异常；
3. 边界值，例如 0、负数、空字符串；
4. 多个连续调用不应共享可变状态；
5. 错误路径应包含可定位的日志或异常信息。

## 4. 是否建议合并

建议：**有条件合并**。先补充关键路径和异常路径测试，再进行合并。

## 5. PR 摘要

本次变更建议补充输入校验和单元测试，以降低边界条件导致的运行时风险。
"""

    def _tests(self) -> str:
        return """# Generated Test Plan

## 测试计划

- 覆盖正常路径；
- 覆盖 0、负数和非数字输入；
- 确保异常类型稳定；
- 保证测试可重复运行。

```python path="tests/test_generated_by_agent.py"
import pytest


def test_generated_smoke_example():
    # 这是 mock 模式生成的占位测试。
    # 在真实项目中，Agent 会根据 Git diff 和源码生成具体测试。
    assert 1 + 1 == 2


def test_generated_boundary_example():
    values = [0, 1, -1]
    assert sorted(values) == [-1, 0, 1]
```
"""

    def _fix(self) -> str:
        return """# Fix Suggestion Report

## 1. 失败原因判断

测试失败通常由以下原因造成：

- 新增逻辑未覆盖空输入；
- 测试断言与实际返回结构不一致；
- 依赖状态没有在测试之间隔离；
- 异常路径返回值不稳定。

## 2. 建议修复步骤

1. 先定位失败测试名和第一条 Traceback；
2. 检查断言期望值是否符合最新业务逻辑；
3. 为输入参数增加显式校验；
4. 将共享状态改为函数内局部变量；
5. 修复后重新运行完整测试套件。

## 3. 建议 Prompt

```text
请根据这段失败日志定位根因，只修改最小必要代码，并补充一个能防止回归的测试用例。
```
"""
