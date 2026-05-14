# CodeReview-Test Agent

一个面向个人开发者和小团队的 **AI 代码审查与单元测试生成 Agent**。

它可以读取 Git diff 和相关源码文件，自动完成：

- 代码变更总结
- 风险点和边界条件分析
- 单元测试计划生成
- 测试代码生成
- 本地测试命令执行
- 根据测试失败日志给出修复建议
- 输出可提交到申请表/GitHub PR 的 Markdown 报告

> 这个仓库适合用来作为申请表里的「AI Agent 项目」证明材料：有完整代码、README、可运行 demo、运行日志和可截图的命令行输出。

---

## 1. 快速开始

### 安装

```bash
cd codereview-test-agent
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

### 无 API Key 试运行 mock demo

```bash
codereview-agent review --mock
codereview-agent generate-tests --mock --target tests/test_generated_by_agent.py --write
codereview-agent run-tests --cmd "python -m pytest -q"
codereview-agent all --mock --test-cmd "python -m pytest -q" --write-tests
```

mock 模式会返回内置示例，方便你截图、录屏和验证流程。

### 使用真实模型

复制环境变量示例：

```bash
cp .env.example .env
```

修改 `.env`：

```env
LLM_API_KEY=你的 API Key
LLM_BASE_URL=https://api.openai.com/v1/chat/completions
LLM_MODEL=gpt-4.1-mini
```

DeepSeek 示例：

```env
LLM_API_KEY=你的 DeepSeek API Key
LLM_BASE_URL=https://api.deepseek.com/chat/completions
LLM_MODEL=deepseek-chat
```

然后执行：

```bash
codereview-agent review
codereview-agent generate-tests --target tests/test_agent_generated.py --write
codereview-agent run-tests --cmd "python -m pytest -q"
```

---

## 2. 常用命令

### 代码审查

```bash
codereview-agent review
```

输出内容包括：

- 本次变更总结
- 主要风险
- 边界条件
- 建议补充测试
- 是否建议合并

### 生成单元测试

```bash
codereview-agent generate-tests --framework pytest --target tests/test_agent_generated.py --write
```

如果不加 `--write`，只会把 AI 生成结果保存为 Markdown，不会改动项目文件。

### 运行测试

```bash
codereview-agent run-tests --cmd "python -m pytest -q"
```

测试日志会保存到 `.agent-runs/<时间>/test.log`。

### 根据失败日志生成修复建议

```bash
codereview-agent fix-from-log --log .agent-runs/20250101-120000/test.log
```

### 一键流程

```bash
codereview-agent all --test-cmd "python -m pytest -q" --write-tests --target tests/test_agent_generated.py
```

---

## 3. 推荐录屏流程

1. 打开一个有 Git diff 的项目；
2. 运行 `codereview-agent review --mock` 或真实模型命令；
3. 展示生成的 Review 报告；
4. 运行 `codereview-agent generate-tests --mock --write`；
5. 展示自动生成的测试文件；
6. 运行 `codereview-agent run-tests --cmd "python -m pytest -q"`；
7. 展示测试日志和 `.agent-runs` 目录；
8. 如果测试失败，运行 `fix-from-log` 展示 AI 修复建议。

---

## 4. 项目结构

```text
codereview-test-agent/
├── src/codereview_test_agent/
│   ├── cli.py              # 命令行入口
│   ├── agent.py            # Agent 编排逻辑
│   ├── config.py           # 环境变量和配置
│   ├── llm.py              # OpenAI-compatible LLM 客户端
│   ├── mock_llm.py         # 无 API Key 的 mock 输出
│   ├── prompts.py          # Review/Test/Fix Prompt
│   ├── repository.py       # Git diff 和源码上下文读取
│   ├── report.py           # Markdown 报告和代码块解析
│   ├── test_runner.py      # 本地测试运行器
│   └── utils.py            # 工具函数
├── examples/sample_python_project/ # 示例项目
├── tests/                  # Agent 自身测试
├── docs/                   # 架构和申请表文案
└── scripts/demo.sh         # 一键 demo 脚本
```

---

## 5. 申请表可写成果

你可以把 `docs/application_form_text.md` 里的内容复制到网页第 04 项，再替换成自己的真实数据。

---

## 6. 安全说明

- 不要提交 `.env`；
- 不要把 API Key、Cookie、Access Token 粘贴给模型；
- 上传截图前请打码邮箱、Key、账单地址、支付信息；
- 默认不会自动修改代码，只有加 `--write` 才会写入测试文件。
