# 06 实验执行与审查

## 阶段计划

| 阶段               | 目标                  | 具体步骤                                                   | 预期产物                                                      | 验证方式                                | 退出标准                    | 审查风险                  |
| ---------------- | ------------------- | ------------------------------------------------------ | --------------------------------------------------------- | ----------------------------------- | ----------------------- | --------------------- |
| S0 来源获取          | 固定来源和复现范围           | 保存 arXiv URL、ar5iv URL、复现范围                            | `paper-analysis/source_notes.md`                          | URL 可访问；范围说明 public-only 或 full     | 人工接受范围                  | 忘记闭源数据限制              |
| S1 数据下载和清洗       | 构造公开客户端数据集          | 下载 MNIST/CIFAR/Shakespeare；生成客户端划分                     | `data/processed/*`, `paper-analysis/data_checks.md`       | 数量、checksum、标签直方图、Shakespeare 客户端统计 | 数量匹配或偏差已记录              | Shakespeare parser 偏差 |
| S2 环境设置          | 创建可复现实验环境           | 安装依赖、记录版本、测试 CUDA                                      | `paper-analysis/env_freeze.txt`                           | import/version/CUDA 检查通过            | smoke script 可运行        | CUDA/包版本不匹配           |
| S3 算法实现          | 实现 FedSGD/FedAvg    | 添加 server loop、client update、sampling、aggregation      | `src/fedavg/*`, 单元测试                                      | 聚合权重和为 1；tiny run loss 下降           | E0 完成                   | 公式或权重 bug             |
| S4 基线 smoke test | sweep 前验证 pipeline  | 运行 MNIST 2NN tiny FedSGD 和 FedAvg                      | `results/e0_smoke.json`, logs                             | loss 下降；指标已保存                       | 两个 run 都完成              | tiny data 造成虚假信心      |
| S5 公开主实验         | 复现核心表格/图            | 运行 MNIST CNN 和 Shakespeare grid                        | `results/mnist_*`, `results/shakespeare_*`, figures       | 目标轮数插值可用                            | Table 2 / Figure 2 已重建  | 超参数预算太小               |
| S6 CIFAR 实验      | 复现 Table 3/Figure 4 | 运行 CIFAR central SGD、FedSGD、FedAvg                     | `results/cifar10_*`, `figures/fig4_cifar.png`             | 曲线和目标轮数已生成                          | 趋势匹配论文                  | 预处理差异                 |
| S7 消融/对照         | 支撑机制 claim          | 运行 client fraction、本地 epoch、IID/non-IID、shared-init 实验 | `results/ablation_*`, `figures/fig1_*`, `tables/table1_*` | 每个消融都有指标和结论                         | 必跑消融完成                  | 算力爆炸                  |
| S8 审计和对比         | 申报结论前检查证据           | 将重建结果与论文表格对比；检查日志                                      | `paper-analysis/reproduction_report.md`                   | 没有缺失结果文件；偏差已解释                      | 可交给 `/experiment-audit` | 夸大近似复现程度              |

## 可验证中间结果

- 数据阶段结束后，应有准确的客户端数量、split size、标签直方图和样本预览。
- 环境阶段结束后，应有 `env_freeze.txt` 和 CUDA 可用性记录。
- 算法阶段结束后，应有客户端采样和加权聚合的单元测试。
- Smoke 阶段结束后，应有一个完整 FedSGD 和一个完整 FedAvg 的 result JSON。
- 训练阶段结束后，应有 checkpoint、日志和 best metric summary。
- 评估阶段结束后，应有重建表格/图和原始 CSV/JSON 输入。

## 审查清单

报告成功前必须检查：

- 每个图中的数字都来自保存的 result 文件。
- 每个表格项都能追踪到 command/config/seed。
- 每个目标轮数插值都说明是否使用 monotonic best-so-far 曲线。
- 每个缺失论文结果都标为 BLOCKED 或 NOT_ATTEMPTED。
- 关于通信轮数减少的 claim 必须说明 baseline 和 target accuracy。

## 交接给实现阶段

人工确认以下三点后，就可以进入实现：

1. 接受只复现公开数据。
2. 接受 PyTorch，而不是强制历史 TensorFlow。
3. 至少批准 MNIST 和 Shakespeare sweep 的 GPU 预算。
