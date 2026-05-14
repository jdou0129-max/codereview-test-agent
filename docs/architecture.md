# CodeReview-Test Agent 架构说明

## 核心目标

CodeReview-Test Agent 不是简单的代码补全工具，而是一个面向工程流程的 Agent。它围绕一次代码变更，完成审查、测试、运行、调试建议和报告生成。

## 模块划分

```text
Repository -> Prompt Builder -> LLM Client -> Report Writer
                 ↓
             Test Runner
                 ↓
          Failure Log Analyzer
```

### Repository

读取 Git diff、变更文件列表和源码上下文。

### Prompt Builder

把代码上下文组织成三个核心任务：

- Review Prompt
- Test Generation Prompt
- Fix From Log Prompt

### LLM Client

通过 OpenAI-compatible 接口连接模型。也支持 mock 模式，方便无 API Key 演示。

### Test Runner

执行本地测试命令，保存 stdout/stderr 到 `.agent-runs`。

### Report Writer

将 AI 输出保存为 Markdown 报告，并可解析带 path 属性的代码块写入测试文件。

## 为什么适合作为申请项目

- 有明确痛点：Review 不充分、测试覆盖不足、Bug 定位耗时；
- 有完整 Agent 流程：理解、分析、生成、执行、反馈；
- 有可量化指标：处理任务数、生成测试数、测试通过率、节省时间、Token 用量；
- 有易准备证明：命令行截图、GitHub diff、测试日志、用量账单、演示录屏。
