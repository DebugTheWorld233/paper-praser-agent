# Paper Parser Agent

一个面向 Codex、Claude Code、OpenClaw 和 ARIS 风格工作流的论文解析与复现规划 agent。给它一篇论文 PDF、arXiv 链接、DOI 或项目页，它会生成一组中文 Markdown 文档，用来判断论文能否复现、需要哪些数据/环境/实验、哪里需要人工帮助。

> 仓库目录和 GitHub 仓库名沿用历史名称 `paper-praser-agent`。功能描述上统一使用更准确的名称 `Paper Parser Agent`。

## 能做什么

`paper-solution-agent` 默认会在 `paper-analysis/` 根目录下，为每次任务创建一个独立子目录：

```text
paper-analysis/<YYYYMMDD-HHMMSS>_<paper-key>/
```

例如：

```text
paper-analysis/20260524-141530_brendan-mcmahan-1602.05629/
```

对于 arXiv 论文，`paper-key` 默认使用 `第一作者-arxiv_id`。对于本地 PDF 或普通 URL，则退回到文件名或 URL 的简化 slug。

每个任务目录内会生成：

1. `00_MANIFEST.md`：本次分析索引、状态和下一步动作。
2. `01_PAPER_INFO.md`：论文信息、任务定义、核心贡献、主要结论、目标指标、要复现的图表/表格。
3. `02_DATA.md`：数据集名称和版本、下载地址、数据处理、许可证和使用限制、是否需要人工帮助。
4. `03_ENVIRONMENT.md`：OS、Python/框架、CUDA/cuDNN、关键库、硬件需求、随机种子、资源预估。
5. `04_EXPERIMENT_PLAN.md`：主实验、消融实验、对照实验、每一步产出和成功标准。
6. `05_ISSUES_AND_ASSUMPTIONS.md`：论文不清楚处、代码论文不一致处、补充假设、改动原因。
7. `06_EXECUTION_AND_REVIEW.md`：分阶段执行步骤、每阶段效果和可验证中间结果。
8. `07_HUMAN_HELP.md`：闭源数据、付费 API、专有软件、GPU 预算、外网权限、代码/附录权限和需要人工拍板的问题。
9. `sources/`：论文 PDF、元数据和可选的抽取文本。

默认输出为中文 Markdown。论文标题、数据集名、方法名、命令和路径保留原文以避免歧义。

## 在 Codex 中使用

默认安装到用户目录 `~/.codex/skills/`。这个仓库提供了对应的安装脚本：

Windows PowerShell：

```powershell
.\scripts\install_codex.ps1
```

macOS/Linux：

```bash
bash scripts/install_codex.sh
```

安装后重启 Codex，或打开一个新的会话，让 `/paper-solution-agent` skill 被加载。

重新运行安装脚本会覆盖 `~/.codex/skills/paper-solution-agent/` 下已有内容。

使用示例：

- 只有论文链接时，agent 会先读取论文，再输出复现规划文档：

```text
/paper-solution-agent "https://arxiv.org/abs/1602.05629"
```

- 如果你已经知道官方代码或参考仓库，可以把仓库地址一并传入，agent 会同时对照论文和代码：

```text
/paper-solution-agent "https://arxiv.org/abs/1602.05629 -- base repo: https://github.com/org/repo"
```

- 如果论文已经在本地，直接传 PDF 路径即可：

```text
/paper-solution-agent "C:\path\to\paper.pdf"
```

这三种写法的核心输入都一样：`<论文来源> [-- base repo: <代码仓库>]`。运行后会在 `paper-analysis/` 下创建一个新的任务目录，并写入 `00_MANIFEST.md`、7 份分析文档和 `sources/` 源材料目录。

## 在 Claude Code 中使用

默认安装到用户目录 `~/.claude/commands/`。这个仓库提供了对应的安装脚本：

Windows PowerShell：

```powershell
.\scripts\install_claude_code.ps1
```

macOS/Linux：

```bash
bash scripts/install_claude_code.sh
```

安装后重启 Claude Code，或打开一个新的会话，让 `/paper-solution-agent` 命令被加载。

重新运行安装脚本会覆盖 `~/.claude/commands/paper-solution-agent.md`。

这个命令会读取当前工作区里的 `skills/paper-solution-agent/SKILL.md` 和 `scripts/paper_source.py`，所以请在本仓库根目录打开 Claude Code 后再使用它。

使用示例：

- 只有论文链接：

```text
/paper-solution-agent https://arxiv.org/abs/1602.05629
```

- 论文加代码仓库：

```text
/paper-solution-agent https://arxiv.org/abs/1602.05629 -- base repo: https://github.com/org/repo
```

- 本地 PDF：

```text
/paper-solution-agent C:\path\to\paper.pdf
```

参数含义和 Codex 版保持一致。区别只在于安装方式不同，输出结果和目录结构相同。

对应的命令模板在：

```text
adapters/claude-code/paper-solution-agent.md
```

## 更新与卸载

更新方式很简单：重新运行对应安装脚本即可，现有安装会被覆盖。

卸载方式也不需要单独脚本：

- Codex：删除 `~/.codex/skills/paper-solution-agent/`
- Claude Code：删除 `~/.claude/commands/paper-solution-agent.md`

## 在 OpenClaw 中使用

OpenClaw 不一定支持 Codex/Claude Code 的 slash command 或 skill 机制，所以这里采用 ARIS 的适配思路：**阶段化任务 + 文件化产出**。

可以把 OpenClaw 的用法理解成两步：

1. 先用本地脚本把论文 PDF、元数据和可选文本准备到 `paper-analysis/`。
2. 再把 prompt 交给 OpenClaw，让它基于这些材料生成分析文档。

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
adapters/openclaw/PAPER_SOLUTION_AGENT_PROMPT_CN.md
```

详细步骤见：

```text
adapters/openclaw/RUNBOOK_CN.md
```

## 本地 PDF/arXiv 准备脚本

`scripts/paper_source.py` 复用了 ARIS `arxiv_fetch.py` 的标准库 arXiv 搜索/下载思路，并按本项目需求扩展为“论文源材料准备”脚本。

运行这个脚本需要 Python 3.10 或更高版本。

这个脚本适合在两种场景下单独运行：

1. 你想先把论文 PDF 和元数据缓存到本地，再交给 Codex、Claude Code 或 OpenClaw 继续分析。
2. 你想显式控制输出目录，或者保留每次准备的历史记录。

```bash
# arXiv 元数据 + PDF 下载 + 尝试抽取文本
python scripts/paper_source.py prepare "https://arxiv.org/abs/1602.05629" --out paper-analysis

# 保持旧版平铺目录结构
python scripts/paper_source.py prepare "https://arxiv.org/abs/1602.05629" --out paper-analysis --flat

# 只查 arXiv 元数据
python scripts/paper_source.py metadata 1602.05629
```

默认输出示例：

```text
paper-analysis/20260524-141530_brendan-mcmahan-1602.05629/
  00_MANIFEST.md
  01_PAPER_INFO.md
  ...
  07_HUMAN_HELP.md
  sources/
    source_metadata.json
    1602.05629.pdf
    paper_text.md
```

脚本执行后会打印 JSON，其中 `analysis_dir` 就是本次运行应继续写入的目录。

## 输入模板

中文输入模板在：

```text
templates/PAPER_SOLUTION_AGENT_TEMPLATE_CN.md
```

如果你先运行了 `prepare`，建议把补充输入写到本次任务目录下的 `INPUT.md`，例如：

```text
paper-analysis/<run-dir>/INPUT.md
```

## 示例

`examples/fedavg-1602.05629/` 是对 FedAvg 经典论文 `Communication-Efficient Learning of Deep Networks from Decentralized Data` 的一次中文输出示例。

该示例没有使用代码仓库，因此 agent 将成功标准判断为“结果接近”，并把闭源的大规模社交网络数据标记为 `BLOCKED`。

## 仓库结构

```text
.
├── README.md
├── requirements.txt                         # PDF 文本抽取的可选依赖
├── skills/
│   └── paper-solution-agent/
│       └── SKILL.md                         # Codex/ARIS 核心 skill
├── scripts/
│   ├── paper_source.py                      # arXiv/PDF 准备脚本
│   ├── install_codex.ps1                    # Codex Windows 安装脚本
│   ├── install_codex.sh                     # Codex macOS/Linux 安装脚本
│   ├── install_claude_code.ps1              # Claude Code Windows 安装脚本
│   └── install_claude_code.sh               # Claude Code macOS/Linux 安装脚本
├── adapters/
│   ├── claude-code/
│   │   └── paper-solution-agent.md          # Claude Code 命令模板
│   └── openclaw/
│       ├── PAPER_SOLUTION_AGENT_PROMPT_CN.md
│       └── RUNBOOK_CN.md                    # OpenClaw prompt 和运行手册
├── templates/
│   └── PAPER_SOLUTION_AGENT_TEMPLATE_CN.md  # 中文输入模板
├── examples/
│   └── fedavg-1602.05629/                   # 示例输出
└── docs/
    └── PLAN.md                              # 设计与实现规划
```

## License

MIT
