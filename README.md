# FG-based Local Community Detection — Reproduction

基于折叠子图（Folded Subgraph）的局部社区检测方法复现。

原论文：*A Local Community Detection Method Based on Folded Subgraph*

## 方法概述

FG-based 方法以**折叠子图**为核心构建单元，通过三阶段循环迭代扩展局部社区：

1. **折叠阶段（Folding Stage）**：以候选集中每个节点为起点构造折叠子图，将满足链接密度阈值 γ 的折叠子图整体并入社区。
2. **模块度扩展阶段（Modularity Stage）**：在折叠子图基础上，以局部模块度 M = e_in / e_out 为准则逐个加入候选节点。
3. **松弛阶段（Relaxation Stage）**：综合 f1（链接密度）与 f2（模块度增益）两个指标，以权重 β=0.5 和阈值 h 放宽加入条件，召回前两阶段遗漏的节点。

三阶段循环直至社区大小不再变化。

**基线方法**：M-based —— 仅基于局部模块度的单节点贪心扩展，不使用折叠子图。

## 项目结构

```
├── src/
│   ├── fg_method.py         # Algorithm 5: FG-based 主流程
│   ├── folded_subgraph.py   # Algorithm 1: 折叠子图构造
│   ├── folding_stage.py     # 折叠阶段
│   ├── modularity_stage.py  # 模块度扩展阶段
│   ├── relaxation_stage.py  # 松弛阶段
│   ├── baseline.py          # M-based 基线方法
│   ├── data_loader.py       # 数据集加载（Karate/Dolphins/Polbooks/LFR）
│   ├── evaluate.py          # 评估：Recall / Precision / F-score
│   └── graph_utils.py       # 图工具函数
├── experiments/
│   ├── run_all.py           # 批量运行全部数据集（各数据集最优参数）
│   ├── run_karate.py        # 单数据集：Karate
│   ├── run_dolphins.py      # 单数据集：Dolphins
│   ├── run_polbooks.py      # 单数据集：Polbooks
│   ├── run_lfr.py           # 单数据集：LFR 合成网络
│   └── sweep.py             # γ × h 二维参数扫描
├── data/
│   ├── dolphins/            # 海豚社交网络（62节点/159边/2社区）
│   └── polbooks/            # 美国政治书籍网络（105节点/441边/3社区）
├── results/                 # 实验结果（CSV）
└── scripts/                 # 辅助脚本
```

> Karate 数据集由 NetworkX 内置生成；LFR 合成网络通过 `LFR_benchmark_graph` 在线生成。

## 环境依赖

- Python ≥ 3.10
- NetworkX
- NumPy

```bash
pip install networkx numpy
```

## 快速开始

### 运行全部数据集实验

各数据集使用经 γ×h 扫描调优后的最优参数：

```bash
python experiments/run_all.py
```

结果将打印到终端并保存至 `results/all_results.csv`。

### 运行单个数据集

```bash
python experiments/run_karate.py
python experiments/run_dolphins.py
python experiments/run_polbooks.py
python experiments/run_lfr.py
```

### 参数扫描

```bash
python experiments/sweep.py
```

对 γ ∈ {0.5, 0.6, 0.7, 0.8, 0.9, 1.0} 和 h ∈ {0.5, 0.6, 0.7, 0.8, 0.9, 1.0} 进行二维网格搜索，结果保存至 `results/gamma_h_sweep.csv`。

## 各数据集最优参数

| 数据集 | γ | h | β |
|--------|---|---|---|
| karate   | 0.6 | 1.0 | 0.5 |
| dolphins | 1.0 | 0.6 | 0.5 |
| polbooks | 0.6 | 0.6 | 0.5 |
| lfr1 (μ=0.1) | 0.8 | 0.8 | 0.5 |
| lfr2 (μ=0.2) | 0.6 | 1.0 | 0.5 |
| lfr5 (μ=0.5) | 0.8 | 0.6 | 0.5 |

## 实验结果

全节点平均的 Recall / Precision / F-score：

| 数据集 | 方法 | Recall | Precision | F-score |
|--------|------|--------|-----------|---------|
| karate | M-based  | 0.4377 | 0.9314 | 0.5722 |
| karate | **FG-based** | **0.9464** | 0.9211 | **0.9318** |
| dolphins | M-based  | 0.1917 | 0.9570 | 0.3041 |
| dolphins | **FG-based** | **0.9685** | 0.9519 | **0.9600** |
| polbooks | M-based  | 0.1741 | 0.7955 | 0.2711 |
| polbooks | **FG-based** | **0.7914** | 0.7547 | **0.7580** |
| lfr1 (μ=0.1) | M-based  | 0.2147 | 0.8449 | 0.3232 |
| lfr1 (μ=0.1) | **FG-based** | **0.9293** | 0.8186 | **0.8663** |
| lfr2 (μ=0.2) | M-based  | 0.1615 | 0.5942 | 0.2323 |
| lfr2 (μ=0.2) | **FG-based** | **0.6671** | 0.4342 | **0.4252** |
| lfr5 (μ=0.5) | M-based  | 0.0725 | 0.3641 | 0.1142 |
| lfr5 (μ=0.5) | **FG-based** | **0.9766** | 0.1768 | **0.2852** |

FG-based 在所有数据集上 F-score 均显著优于 M-based 基线，尤其在 Recall 上提升明显。

## 评估方式

对网络中**每个节点**作为起始节点运行检测算法，计算检测社区与该节点真实社区的 Recall / Precision / F-score，最后取全节点平均值。

```
Recall    = |C_found ∩ C_true| / |C_true|
Precision = |C_found ∩ C_true| / |C_found|
F-score   = 2 · Precision · Recall / (Precision + Recall)
```

## 注意事项

- `src/data_loader.py` 中 `DATA_DIR` 默认为绝对路径 `D:\FG-based\data`，如克隆到其他位置请修改该变量。
- LFR 生成参数与论文原文略有差异（详见 `load_lfr`  docstring），核心变量 μ 和 N=200 保持一致。
