# 论文分析清单

**论文**：Communication-Efficient Learning of Deep Networks from Decentralized Data  
**arXiv**：https://arxiv.org/abs/1602.05629  
**目标**：复现  
**成功标准**：结果接近  
**输出语言**：中文 Markdown  
**生成日期**：2026-05-23  

## 判断

用户没有提供代码仓库，因此本次计划面向“根据论文重建实现并尽量复现实验趋势”，不追求与原作者代码逐行或逐配置完全一致。

## 产物

| 文件 | 状态 | 用途 | 下一步 |
|---|---|---|---|
| `01_PAPER_INFO.md` | 草稿 | 论文事实、贡献、目标指标、图表清单 | 人工确认优先复现哪些图表 |
| `02_DATA.md` | 草稿 | 数据集、访问方式、处理流程、许可证、限制 | 确认是否跳过闭源社交网络数据 |
| `03_ENVIRONMENT.md` | 草稿 | 操作系统、框架、CUDA、硬件、随机种子、资源预估 | 确认 GPU 预算和框架偏好 |
| `04_EXPERIMENT_PLAN.md` | 草稿 | 主实验、消融、对照、输出文件和成功标准 | 批准公共数据复现范围 |
| `05_ISSUES_AND_ASSUMPTIONS.md` | 草稿 | 不清楚之处、缺失代码细节、补充假设和风险 | 人工审阅需要确认的假设 |
| `06_EXECUTION_AND_REVIEW.md` | 草稿 | 分阶段实现和审查计划，包含可验证中间结果 | 作为实现 agent 的交接文档 |
| `07_HUMAN_HELP.md` | 草稿 | 需要人工帮助的阻塞项、权限、算力和决策 | 先解决阻塞项再做完整实验 |

## 来源锚点

- arXiv 摘要和元信息：https://arxiv.org/abs/1602.05629
- ar5iv 全文 HTML：https://ar5iv.labs.arxiv.org/html/1602.05629

## 前三步

1. 确认复现范围：只复现公开数据，还是尝试申请闭源大规模 LSTM 数据。
2. 实现最小 FedAvg/FedSGD 模拟器，并在 MNIST 2NN 上做 smoke test。
3. 优先复现 Table 2 / Figure 2 的公开数据结果，再扩展到 CIFAR-10 和附录图表。
