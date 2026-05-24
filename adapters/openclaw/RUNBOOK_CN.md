# OpenClaw 使用手册

## 目标

OpenClaw 不一定支持 Codex/Claude 风格的 slash skill。因此本项目在 OpenClaw 中采用 ARIS 的适配思路：**阶段化任务 + 文件化产出**。

也就是说，不要求 OpenClaw 识别 `/paper-solution-agent`，而是让 OpenClaw 读取 `SKILL.md` 和本目录里的 prompt，然后按文件契约在 `paper-analysis/` 下生成本次任务目录。

## 推荐流程

### 1. 准备论文源材料

如果是 arXiv 链接：

```bash
python scripts/paper_source.py prepare "https://arxiv.org/abs/1602.05629" --out paper-analysis
```

如果是本地 PDF：

```bash
python scripts/paper_source.py prepare "C:\path\to\paper.pdf" --out paper-analysis
```

脚本会创建一个新的任务目录，并尽量生成：

```text
paper-analysis/<run-dir>/sources/source_metadata.json
paper-analysis/<run-dir>/sources/<paper>.pdf
paper-analysis/<run-dir>/sources/paper_text.md
```

脚本执行后会打印 JSON，其中 `analysis_dir` 就是本次运行应继续写入的目录。

如果缺少 `pypdf`/`PyPDF2`/`pdftotext`，PDF 可能只能下载，不能抽取文本。此时可以：

```bash
python -m pip install pypdf
```

然后重新运行 `prepare`。

### 2. 在 OpenClaw 中运行 prompt

复制：

```text
adapters/openclaw/PAPER_SOLUTION_AGENT_PROMPT_CN.md
```

把 `<PAPER_SOURCE>` 和 `<BASE_REPO_OR_NONE>` 替换成你的论文和代码仓库信息。

### 3. 检查输出

OpenClaw 应在 `analysis_dir` 下生成：

```text
paper-analysis/<run-dir>/00_MANIFEST.md
paper-analysis/<run-dir>/01_PAPER_INFO.md
paper-analysis/<run-dir>/02_DATA.md
paper-analysis/<run-dir>/03_ENVIRONMENT.md
paper-analysis/<run-dir>/04_EXPERIMENT_PLAN.md
paper-analysis/<run-dir>/05_ISSUES_AND_ASSUMPTIONS.md
paper-analysis/<run-dir>/06_EXECUTION_AND_REVIEW.md
paper-analysis/<run-dir>/07_HUMAN_HELP.md
```

### 4. 进入实现阶段

如果你只使用 OpenClaw，不依赖 ARIS，可以让 OpenClaw 继续执行 `06_EXECUTION_AND_REVIEW.md` 中的阶段计划。

如果你同时安装了 ARIS，可以把 `04_EXPERIMENT_PLAN.md` 和 `06_EXECUTION_AND_REVIEW.md` 交给 ARIS 的 `/experiment-bridge`、`/run-experiment` 或 `/experiment-audit` 继续执行。

## 与 ARIS 的关系

本项目复用了 ARIS 的两个核心思想：

1. **Markdown skill 即 workflow contract**：`SKILL.md` 是 agent 的能力说明书。
2. **工具轻量可替换**：arXiv 下载逻辑来自 ARIS `arxiv_fetch.py` 的标准库实现思路，并改造成 `scripts/paper_source.py`。

本项目不要求完整安装 ARIS。只有当你想继续使用 ARIS 的实验执行、远程 GPU、审计和论文写作链路时，才需要安装完整 ARIS。
