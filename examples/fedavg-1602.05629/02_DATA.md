# 02 数据

## 数据集清单

| 数据集 | 版本/来源 | 论文中的作用 | 获取方式 | 是否需要人工帮助 |
|---|---|---|---|---|
| MNIST | LeCun 等人的手写数字数据集 | 2NN 和 CNN 的 IID / non-IID 实验 | 公开 | 否 |
| Shakespeare complete works | Project Gutenberg ebook 100 | 字符级 LSTM，按剧本角色构造客户端 | 公开 | 需要确认许可证/引用偏好 |
| CIFAR-10 | Krizhevsky CIFAR-10 | CNN 通信轮数基准 | 公开 | 否 |
| 大规模社交网络公开帖子 | 作者内部数据，超过 500k 客户端 | word-level LSTM 大规模实验 | 闭源/不可用 | 是，BLOCKED |

## 下载来源

- MNIST：使用 `torchvision.datasets.MNIST` 或 TensorFlow/Keras MNIST 镜像。
- CIFAR-10：使用 `torchvision.datasets.CIFAR10` 或 TensorFlow 数据加载器。
- Shakespeare：Project Gutenberg ebook 100，论文引用地址：https://www.gutenberg.org/ebooks/100
- 大规模社交网络帖子：论文没有公开下载地址，需要作者/机构授权或明确改用替代数据。

## 处理流程

### MNIST

- 使用标准 60,000 train / 10,000 test 划分。
- IID 划分：打乱训练集，分给 100 个客户端，每个客户端 600 个样本。
- non-IID 划分：按 digit label 排序，切成 200 个 shard，每个 shard 300 个样本，每个客户端分配 2 个 shard。
- 评估：中心化测试集准确率。
- 数据检查：客户端数量、每客户端样本数、每客户端标签直方图、全局 train/test 数量。

### Shakespeare 字符级 LSTM

- 下载完整 Shakespeare 文本。
- 解析 play 和 speaking role。
- 保留至少有两行文本的角色。
- 一个角色对应一个客户端，论文目标约 1146 个客户端。
- 每个角色/客户端前 80% 行作为训练，后 20% 行作为测试，至少保留一行测试。
- 论文报告训练集 3,564,579 个字符、测试集 870,014 个字符；复现时用作近似校验目标。
- 额外构造 balanced IID 版本作为对照。

### CIFAR-10

- 使用标准 50,000 train / 10,000 test。
- 分成 100 个客户端，每个客户端 500 个训练样本和 100 个测试样本，balanced IID。
- 论文预处理：裁剪到 24x24、随机左右翻转、随机调整 contrast/brightness、whitening/standardization。
- 评估：标准测试集或客户端测试集并集；必须记录采用哪一种。

### 大规模社交网络 word LSTM

- BLOCKED：数据集不公开。
- 论文已知信息：公开帖子按作者聚合，超过 500,000 个客户端，每个客户端最多 5000 词，测试作者与训练作者不同，词表大小 10,000。
- 公共替代数据不等价，必须标注为 extension，而不是原论文 Figure 5 复现。

## 许可证与使用限制

| 数据集 | 许可证/限制 | 说明 |
|---|---|---|
| MNIST | 公开研究数据集，引用原始来源 | 确认所用镜像的再分发规则 |
| CIFAR-10 | 公开研究数据集，引用技术报告 | 不要在未确认许可前再分发原始压缩包 |
| Shakespeare / Project Gutenberg | 美国公有领域文本，但受 Gutenberg 使用条款约束 | 检查本地司法辖区和署名要求 |
| 社交网络帖子 | 专有/闭源 | 没有授权不能复现 |

## 预估磁盘占用

- 公开原始数据：小于 500 MB。
- 处理后的客户端划分和缓存 tensor：约 1-5 GB，取决于序列化方式。
- sweep 日志和 checkpoint：约 10-100 GB，取决于学习率、seed 和实验数量。
- 闭源大规模 word LSTM：未知，可能是几十到数百 GB。

## 阻塞项

- BLOCKED：大规模社交网络数据不可用。
- NEEDS_HUMAN_CONFIRMATION：是否用公开替代数据作为扩展实验，或完全跳过 Figure 5。
