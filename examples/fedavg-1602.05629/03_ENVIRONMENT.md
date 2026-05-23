# 03 环境与依赖

## 成功标准

**结果接近**。没有提供官方代码仓库，且原实验来自 2016/2017 年，论文正文无法完整恢复具体框架版本、初始化细节和底层预处理默认值。

## 推荐环境

| 组件 | 推荐版本 | 原因 |
|---|---|---|
| OS | Ubuntu 22.04 LTS 或 WSL2 Ubuntu 22.04 | CUDA/PyTorch 支持稳定 |
| Python | 3.10 或 3.11 | ML 包兼容性好 |
| 框架 | PyTorch 2.3+ | 便于重建实现；不追求原代码对齐 |
| CUDA | 12.1+，如使用 GPU | 匹配常见 PyTorch wheel |
| cuDNN | PyTorch CUDA wheel 内置 | 避免手工配置 cuDNN |
| 关键库 | torch, torchvision, numpy, pandas, matplotlib, tqdm, pyyaml | 数据、训练、绘图和配置 |

NEEDS_HUMAN_CONFIRMATION：是否接受 PyTorch 实用复现，还是要求更贴近论文年代的 TensorFlow 风格实现。

## 硬件需求

| 范围 | 硬件 | 显存 | 运行时间预估 |
|---|---|---|---|
| MNIST smoke test | CPU 或任意 CUDA GPU | 小于 2 GB | 数分钟到数小时 |
| MNIST 完整 grid | 1 张消费级 GPU | 4-8 GB | 数小时 |
| Shakespeare char LSTM | 推荐 1 张 GPU | 4-12 GB | 数小时到 1 天，取决于 grid |
| CIFAR-10 | 推荐 1 张 GPU | 8-12 GB | 0.5-2 天，取决于 grid |
| 论文级 2000+ runs | 推荐多 GPU | 每卡 8-24 GB | 多天 |
| 大规模社交网络 LSTM | 没有数据无法估计 | 未知 | BLOCKED |

## 随机种子

第一轮使用 seeds `0, 1, 2`。如果算力允许并要生成论文级表格，扩展到 `0, 1, 2, 3, 4`。

需要记录：

- Python hash seed。
- NumPy seed。
- PyTorch seed。
- CUDA deterministic flags。
- 客户端划分 seed。
- 每轮客户端采样 seed。
- 模型初始化 seed。

## 资源预估

- 磁盘：公开数据和核心日志 20 GB 足够；完整 sweep 建议 100 GB。
- GPU 显存：公开实验 8 GB 基本够用；CIFAR 和 LSTM sweep 建议 12 GB 更稳。
- 网络：需要下载公开数据、arXiv/Gutenberg 内容。
- Checkpoint：只保存 best 和 final checkpoint，避免每轮通信都存模型。

## 环境验证命令

```bash
python -c "import torch, torchvision, numpy; print(torch.__version__, torchvision.__version__, torch.cuda.is_available())"
python -c "import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu')"
python -m pip freeze > paper-analysis/env_freeze.txt
```

## 安装计划

1. 创建干净的 venv 或 conda 环境。
2. 安装与本机 CUDA 匹配的 PyTorch。
3. 安装项目依赖。
4. 跑数据下载 smoke test。
5. 跑一轮 MNIST 2NN FedSGD 和一轮 FedAvg。
6. 将环境版本冻结到 `paper-analysis/env_freeze.txt`。
