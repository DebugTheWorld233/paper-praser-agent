# Paper Praser Agent

一个面向 Codex、OpenClaw 和 ARIS 风格工作流的论文解析与复现方案 agent。给它一篇论文 PDF、arXiv 链接、DOI 或项目页，它会生成一组中文 Markdown 文档，用来判断论文能否复现、需要哪些数据/环境/实验、哪里需要人工帮助。

> 仓库名沿用 `paper-praser-agent`。功能上更准确地说，它是 paper parser + reproduction planner agent。

## 能做什么

`paper-solution-agent` 会在目标项目的 `paper-analysis/` 目录下生成：

1. `01_PAPER_INFO.md`：论文信息、任务定义、核心贡献、主要结论、目标指标、要复现的图表/表格。
2. `02_DATA.md`：数据集名称和版本、下载地址、数据处理、许可证和使用限制、是否需要人工帮助。
3. `03_ENVIRONMENT.md`：OS、Python/框架、CUDA/cuDNN、关键库、硬件需求、随机种子、资源预估。
4. `04_EXPERIMENT_PLAN.md`：主实验、消融实验、对照实验、每一步产出和成功标准。
5. `05_ISSUES_AND_ASSUMPTIONS.md`：论文不清楚处、代码论文不一致处、补充假设、改动原因。
6. `06_EXECUTION_AND_REVIEW.md`：分阶段执行步骤，每阶段效果和可验证中间结果。
7. `07_HUMAN_HELP.md`：闭源数据、付费 API、专有软件、GPU 预算、外网权限、代码/附录权限和需要人工拍板的问题。

默认输出为中文 Markdown。论文标题、数据集名、方法名、命令和路径会保留原文以避免歧义。

## OpenClaw 使用方式

OpenClaw 不一定有 Codex/Claude 的 slash skill 机制，所以这里采用 ARIS 的 OpenClaw 适配思路：**阶段化任务 + 文件化产出**。

第一步，准备论文源材料：

```bash
python scripts/paper_source.py prepare "https://arxiv.org/abs/1602.05629" --out paper-analysis
```

如果要抽取 PDF 文本，建议先装可选依赖：

```bash
python -m pip install -r requirements.txt
```

第二步，把下面这个 prompt 复制到 OpenClaw：

```text
openclaw/PAPER_SOLUTION_AGENT_PROMPT_CN.md
```

详细步骤见：

```text
openclaw/RUNBOOK_CN.md
```

## 安装到 Codex

Windows PowerShell：

```powershell
.\scripts\install.ps1
```

macOS/Linux：

```bash
bash scripts/install.sh
```

安装后重启 Codex，让新 skill 被加载。

## 使用方式

只有论文链接：

```text
/paper-solution-agent "https://arxiv.org/abs/1602.05629"
```

论文加代码仓库：

```text
/paper-solution-agent "论文链接 — base repo: https://github.com/org/repo"
```

本地 PDF：

```text
/paper-solution-agent "C:\path\to\paper.pdf"
```

## 本地 PDF/arXiv 准备脚本

`scripts/paper_source.py` 复用了 ARIS `arxiv_fetch.py` 的标准库 arXiv 搜索/下载思路，并按本项目需求扩展为“论文源材料准备”脚本。

```bash
# arXiv 元数据 + PDF 下载 + 尝试抽取文本
python scripts/paper_source.py prepare "https://arxiv.org/abs/1602.05629" --out paper-analysis

# 只查 arXiv 元数据
python scripts/paper_source.py metadata 1602.05629
```

输出示例：

```text
paper-analysis/sources/source_metadata.json
paper-analysis/sources/1602.05629.pdf
paper-analysis/sources/paper_text.md
```

## 输入模板

中文输入模板在：

```text
templates/PAPER_SOLUTION_AGENT_TEMPLATE_CN.md
```

你可以把它复制成项目内的 `paper-analysis/INPUT.md`，填好论文、代码、算力和网络限制后再运行 skill。

## 示例

`examples/fedavg-1602.05629/` 是对 FedAvg 经典论文 `Communication-Efficient Learning of Deep Networks from Decentralized Data` 的一次中文输出示例。

该示例没有使用代码仓库，因此 agent 将成功标准判断为“结果接近”，并把闭源的大规模社交网络数据标记为 `BLOCKED`。

## 仓库结构

```text
skills/paper-solution-agent/SKILL.md      # Codex/ARIS skill 主体
openclaw/PAPER_SOLUTION_AGENT_PROMPT_CN.md
openclaw/RUNBOOK_CN.md
scripts/paper_source.py                   # arXiv/PDF 准备脚本
templates/PAPER_SOLUTION_AGENT_TEMPLATE_CN.md
docs/PLAN.md                              # 设计与实现规划
examples/fedavg-1602.05629/               # 示例输出
scripts/install.ps1                       # Windows 安装脚本
scripts/install.sh                        # macOS/Linux 安装脚本
requirements.txt                          # PDF 文本抽取的可选依赖
```

## License

MIT
