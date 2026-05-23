# 01 论文信息

## 元信息

- **标题**：Communication-Efficient Learning of Deep Networks from Decentralized Data
- **作者**：H. Brendan McMahan, Eider Moore, Daniel Ramage, Seth Hampson, Blaise Aguera y Arcas
- **会议/期刊**：AISTATS 2017，JMLR W&CP volume 54
- **arXiv**：1602.05629，2016-02-17 首次提交，2023-01-26 更新到 v4
- **DOI**：https://doi.org/10.48550/arXiv.1602.05629
- **主要来源**：https://arxiv.org/abs/1602.05629
- **可读 HTML**：https://ar5iv.labs.arxiv.org/html/1602.05629

## 任务定义

论文研究在训练样本分散在大量客户端设备上、原始数据不能集中上传的情况下，如何训练神经网络。中心服务器协调训练：服务器把当前模型发送给被选中的客户端，客户端在本地数据上计算更新，只上传模型更新。核心优化目标是在非 IID、不均衡、海量客户端且通信受限的场景下减少通信轮数。

## 核心贡献

1. 将移动设备上的去中心化数据训练问题定义为 **Federated Learning** 的实际研究方向。
2. 提出 **FederatedAveraging（FedAvg）**：客户端执行本地 SGD，服务器对客户端模型做加权平均。
3. 在图像分类和语言建模任务上评估 FedAvg，覆盖 IID、病理非 IID、自然不均衡等数据划分。
4. 论文报告 FedAvg 相比同步 FedSGD/SGD 类基线可减少约 10-100 倍通信轮数。

## 主要结论

- 在客户端增加本地计算量可以显著减少通信轮数。
- FedAvg 在论文构造的 MNIST 病理非 IID 划分和 Shakespeare 自然不均衡划分上仍然比较稳健。
- 客户端比例 `C` 有帮助，但达到一定并行度后，主要收益来自每轮客户端本地训练更多步。
- 本地 epoch 过大时可能出现平台期或发散，因此本地计算量需要调参。

## 目标指标

| 基准 | 目标指标 | 论文中的目标/参考 |
|---|---|---|
| MNIST 2NN | 达到 97% 测试准确率所需通信轮数 | Table 1、Appendix Table 4 |
| MNIST CNN | 达到 99% 测试准确率所需通信轮数 | Table 1、Table 2、Figure 2 |
| Shakespeare char LSTM | 达到 54% 字符预测准确率所需通信轮数 | Table 2、Figure 2、Figure 3 |
| CIFAR-10 CNN | 达到 80%、82%、85% 测试准确率所需通信轮数 | Table 3、Figure 4 |
| 大规模社交网络 word LSTM | 达到 10.5% next-word accuracy 所需通信轮数 | Figure 5，闭源数据 |

## 要复现的图表/表格

| ID | 内容 | 复现状态 |
|---|---|---|
| Figure 1 | MNIST 2NN 上不同初始化/共享初始化的模型参数平均损失 | 公开数据，成本低，适合 smoke test |
| Table 1 | 客户端比例对 MNIST 2NN/CNN 通信轮数的影响 | 公开数据，核心 |
| Table 2 | FedAvg 与 FedSGD 在 MNIST CNN 和 Shakespeare LSTM 上的通信轮数对比 | 公开数据，最高优先级 |
| Figure 2 | MNIST CNN 和 Shakespeare LSTM 的准确率-通信轮数曲线 | 公开数据，最高优先级 |
| Figure 3 | Shakespeare LSTM 中较大本地 epoch 的影响 | 公开数据，有价值的消融 |
| Figure 4 | CIFAR-10 上 FedSGD 与 FedAvg 的通信曲线 | 公开数据，中等优先级 |
| Table 3 | CIFAR-10 达到 80/82/85% 准确率所需轮数和加速比 | 公开数据，中等优先级 |
| Figure 5 | 大规模 word LSTM 学习曲线 | 因闭源社交网络数据而 BLOCKED |
| Figures 6-10 / Table 4 | 附录中的收敛曲线和消融 | 主结果完成后可选 |

## 复现范围

推荐范围是 **公开数据复现**：

1. 必须复现 MNIST 和 Shakespeare 的核心结论。
2. 算力允许时复现 CIFAR-10。
3. 大规模社交网络 word LSTM 标记为无法无数据复现；如果使用公开替代数据，只能作为扩展实验，不能声称等价复现 Figure 5。
