# 04 实验计划

## 成功标准

采用 **结果接近**：

- 公开数据结果应复现 FedAvg 相比 FedSGD 的定性排序和大致通信轮数加速趋势。
- 对精确表格数值允许一定偏差，因为没有官方代码，且论文依赖学习率 sweep、初始化、预处理和客户端采样细节。
- 除非之后拿到官方实现，否则不要求代码级完全对齐。

## 实验矩阵

| ID | 类型 | 目的 | 输入 | 输出 | 指标 | 成功标准 | 优先级 |
|---|---|---|---|---|---|---|---|
| E0 | Smoke | 验证 FedSGD/FedAvg 模拟器和加权聚合 | MNIST 小子集 | `results/e0_smoke.json` | loss 下降、客户端数量正确 | 一轮 FedSGD 和一轮 FedAvg 完成 | 必须 |
| E1 | 主实验 | 复现 MNIST 2NN IID/non-IID 行为 | MNIST 划分、2NN | `results/mnist_2nn_rounds.csv` | 达到 97% 准确率所需轮数 | FedAvg 少于 FedSGD，方向匹配 Table 1/Table 4 | 必须 |
| E2 | 主实验 | 复现 MNIST CNN Table 2 / Figure 2 | MNIST 划分、CNN | `results/mnist_cnn_curves.csv`, `figures/fig2_mnist_cnn.png` | 达到 99% 准确率所需轮数 | FedAvg 显著减少通信轮数 | 必须 |
| E3 | 主实验 | 复现 Shakespeare char LSTM Table 2 / Figure 2 | Shakespeare role clients | `results/shakespeare_lstm_curves.csv`, `figures/fig2_shakespeare.png` | 达到 54% 准确率所需轮数 | FedAvg 改善通信轮数，non-IID role partition 尤其明显 | 必须 |
| E4 | 主实验 | 复现 CIFAR-10 Table 3 / Figure 4 | CIFAR-10 IID 100-client split | `results/cifar10_rounds.csv`, `figures/fig4_cifar.png` | 达到 80/82/85% 准确率所需轮数 | FedAvg 比 baseline SGD/FedSGD 少很多轮 | 应做 |
| E5 | 阻塞 | 复现大规模 word LSTM Figure 5 | 闭源社交网络帖子 | 无 | next-word accuracy 10.5% | 没有数据时 BLOCKED | 阻塞 |
| A1 | 消融 | 改变客户端比例 `C` | MNIST 2NN/CNN | `results/client_fraction.csv` | 达到目标所需轮数 | 达到足够客户端后收益递减 | 必须 |
| A2 | 消融 | 改变本地 epoch `E` 和 minibatch `B` | MNIST CNN、Shakespeare LSTM | `results/local_work_grid.csv` | 轮数、是否发散 | 本地计算增加先有益，过大可能平台期/发散 | 必须 |
| A3 | 消融 | 共享初始化 vs 独立初始化的模型平均 | MNIST 2NN | `figures/fig1_model_average.png` | 插值后的全训练集 loss | 共享初始化使参数平均可行 | 应做 |
| A4 | 对照 | IID vs non-IID 划分 | MNIST、Shakespeare | `results/iid_vs_noniid.csv` | 轮数和最终准确率 | FedAvg 稳健，但 MNIST non-IID 更难 | 必须 |
| C1 | 对照 | 中心化 SGD baseline | CIFAR-10 | `results/cifar_central_sgd.csv` | 达到目标的更新数/轮数 | 趋势匹配 Table 3 | 应做 |
| C2 | 对照 | 每轮一个客户端 | CIFAR-10 / MNIST | `results/one_client.csv` | 曲线方差、目标轮数 | 振荡更大，进展更慢 | 可选 |

## 运行顺序

1. E0 smoke test。
2. E1 MNIST 2NN，小学习率 grid。
3. E2 MNIST CNN，先 IID 后 non-IID。
4. A1/A2 MNIST 消融。
5. E3 Shakespeare LSTM。
6. A4 IID vs non-IID 汇总。
7. 如果 GPU 预算允许，运行 E4/C1 CIFAR-10。
8. 可选 A3 和附录图。

## 学习率搜索

论文说明学习率使用乘法 grid，并按每个 x 轴设置选择最佳曲线。复现应：

- 先定义如 `[0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0]` 的 grid，如果最优值落在边界则扩展。
- 记录所有候选，而不是只保存最佳结果。
- 为目标轮数插值生成 monotonic best-so-far 曲线。

## 预期输出

- 每个 run 生成 `results/*.json` 或 `results/*.csv`。
- 曲线生成 `figures/*.png`。
- 重建 Table 1/Table 2/Table 3/Table 4 到 `tables/*.md`。
- `logs/*.txt` 保存完整命令、seed、partition seed、超参数和 git commit。

## Stop / Go 关卡

- 如果 E0 loss 不下降或聚合权重校验失败，停止。
- 如果 E1 的 MNIST non-IID 标签划分错误，停止。
- 如果 MNIST/Shakespeare 没有显示 FedAvg 通信收益，先不要跑 CIFAR。
- 除非人工批准，否则不要用大规模替代数据声称复现 Figure 5。
