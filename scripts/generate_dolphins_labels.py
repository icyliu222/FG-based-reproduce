"""
生成 Dolphins 数据集的社区标签

背景：
  Dolphins 原始数据集（Lusseau 2003, 62只宽吻海豚）只有拓扑结构，
  不含社区标签。论文复现实验需要 ground truth 社区划分。

方法依据：
  Lusseau & Newman (2004) "Identifying the role that individual animals
  play in their social network", Proc. R. Soc. B, 271(Suppl 6): S477-S481.
  该论文使用 Girvan-Newman（边介数）方法在 Dolphins 网络上检测出
  2个社区和4个子社区。后续社区检测文献普遍将此二社区划分作为
  Dolphins 的 ground truth。

  本脚本使用 networkx 的 girvan_newman 函数，取层次聚类树中
  首次分裂为2个社区时的划分。

输出：
  data/dolphins/dolphins_labels.json  — 标签字典 {节点名: 社区ID}
  data/dolphins/dolphins_labeled.gml  — 带 community 属性的 GML（备用）
"""
import json
import os
import networkx as nx
from networkx.algorithms.community.centrality import girvan_newman

# 路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GML_PATH = os.path.join(PROJECT_ROOT, "data", "dolphins", "dolphins.gml")
JSON_OUT = os.path.join(PROJECT_ROOT, "data", "dolphins", "dolphins_labels.json")
GML_OUT = os.path.join(PROJECT_ROOT, "data", "dolphins", "dolphins_labeled.gml")


def main():
    # 1. 读取原始 GML（只有拓扑，无社区标签）
    G = nx.read_gml(GML_PATH)
    print(f"读取 Dolphins: {G.number_of_nodes()} 节点, {G.number_of_edges()} 边")

    # 2. Girvan-Newman 边介数社区检测（取二社区划分）
    #    girvan_newman 返回一个生成器，每次迭代给出更细的社区划分
    #    第一次迭代就是二社区划分
    print("\n运行 Girvan-Newman 边介数社区检测...")
    gn_iterator = girvan_newman(G)
    two_communities = next(gn_iterator)  # 首次分裂 = 二社区

    comm0 = set(two_communities[0])
    comm1 = set(two_communities[1])
    print(f"二社区划分: 社区0={len(comm0)}, 社区1={len(comm1)}")

    # 3. 计算模块度
    modularity = nx.community.modularity(G, [comm0, comm1])
    print(f"模块度: {modularity:.4f}")

    # 4. 构建标签字典（社区ID按大小排序：大的为0，小的为1）
    if len(comm0) < len(comm1):
        comm0, comm1 = comm1, comm0
    labels = {}
    for node in comm0:
        labels[node] = 0
    for node in comm1:
        labels[node] = 1

    # 5. 保存 JSON
    result = {
        "source": "girvan_newman_2way",
        "reference": "Lusseau & Newman (2004), Proc. R. Soc. B, 271(Suppl 6): S477-S481",
        "method": "Girvan-Newman edge betweenness, first split (2 communities)",
        "modularity": round(modularity, 4),
        "num_communities": 2,
        "community_sizes": [len(comm0), len(comm1)],
        "note": "Dolphins原始数据集(Lusseau 2003)不含社区标签；此二社区划分由Girvan-Newman边介数方法生成，与Lusseau & Newman (2004)论文中的检测结果一致，被后续社区检测文献广泛用作ground truth",
        "labels": labels
    }
    with open(JSON_OUT, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n标签已保存到: {JSON_OUT}")

    # 6. 同时生成带 community 属性的 GML（备用）
    for node in G.nodes():
        G.nodes[node]['community'] = labels[node]
    nx.write_gml(G, GML_OUT)
    print(f"带标签 GML 已保存到: {GML_OUT}")

    # 7. 验证
    print(f"\n验证: 标签数={len(labels)}, 社区0={sum(1 for v in labels.values() if v==0)}, 社区1={sum(1 for v in labels.values() if v==1)}")
    print("完成!")


if __name__ == "__main__":
    main()
