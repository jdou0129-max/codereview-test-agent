from __future__ import annotations

from .repository import RepoSnapshot


SYSTEM_PROMPT = """你是 CodeReview-Test Agent，一个资深代码审查、测试生成和调试 Agent。

你的工作原则：
1. 优先找出真实风险，不要泛泛而谈；
2. 输出应结构化、可执行、适合复制到 PR 或申请材料；
3. 生成测试时要贴近现有代码风格；
4. 不要编造没有在上下文中出现的文件、接口或数据；
5. 如果信息不足，明确写出假设和需要用户确认的点；
6. 默认不要输出敏感信息，提醒用户打码 API Key、Token、Cookie。
"""


def _format_snapshot(snapshot: RepoSnapshot) -> str:
    files = []
    for path, content in snapshot.files.items():
        files.append(f"## File: {path}\n```\n{content}\n```")
    file_context = "\n\n".join(files) if files else "No file context available."
    changed = "\n".join(f"- {p}" for p in snapshot.changed_files) or "No changed files detected."
    diff = snapshot.diff or "No git diff detected. Use file context for best-effort analysis."
    return f"""# Repository Snapshot

Root: {snapshot.root}

# Changed Files
{changed}

# Git Diff
```diff
{diff}
```

# File Context
{file_context}
"""


def review_prompt(snapshot: RepoSnapshot) -> str:
    return f"""请对下面的代码变更进行代码审查。

请输出 Markdown，并包含以下部分：

1. 变更总结：说明这次变更可能在做什么；
2. 主要风险：用表格列出风险、严重度、证据、建议；
3. 边界条件：列出应该重点测试的边界；
4. 单元测试计划：列出具体测试用例；
5. 建议修改：只提出必要修改，不要大范围重构；
6. PR 摘要：给出可以粘贴到 PR 的简短总结；
7. 申请材料描述：用 3-5 句话描述这个 Agent 做了什么、产生了什么价值。

{_format_snapshot(snapshot)}
"""


def test_generation_prompt(snapshot: RepoSnapshot, framework: str, target_path: str) -> str:
    return f"""请基于下面的代码上下文生成单元测试。

要求：
1. 测试框架：{framework}
2. 目标测试文件路径：{target_path}
3. 尽量贴近现有项目风格；
4. 只生成高价值测试，不要为了数量写无意义断言；
5. 如果上下文不足，生成一个最小可运行的 smoke test，并在报告中说明假设；
6. 输出格式必须包含测试计划，然后用下面格式输出测试代码：

```python path=\"{target_path}\"
# test code here
```

如果项目不是 Python，请把语言标识改成对应语言，但仍保留 path 属性。

{_format_snapshot(snapshot)}
"""


def fix_prompt(snapshot: RepoSnapshot, test_log: str) -> str:
    return f"""请根据测试失败日志和代码上下文进行调试分析。

请输出 Markdown，并包含：

1. 失败摘要：失败测试、错误类型、最可能根因；
2. 最小修复建议：说明应该改哪些文件、为什么；
3. 回归测试建议：补充哪些测试避免复发；
4. 可复制 Prompt：给出一个可以继续交给编码 Agent 执行修复的 Prompt；
5. 风险提醒：列出修复时要避免的破坏性改动。

# Test Log
```text
{test_log}
```

{_format_snapshot(snapshot)}
"""
