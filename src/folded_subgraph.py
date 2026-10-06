"""
Algorithm 1：折叠子图构造（Folded Subgraph）
核心基石：贪心构造高链接密度的节点集合
"""
from .graph_utils import get_neighbors, get_degree, count_edges_between, link_density


def construct_folded_subgraph(G, v, gamma):
    """
    构造以 v 为起始节点的折叠子图

    参数:
        G: 网络图 (networkx.Graph)
        v: 起始节点
        gamma: 链接密度阈值 (0 < gamma <= 1，建议 >= 0.5)

    返回:
        F: 折叠子图节点集合 (set)
    """
    # 第1行：初始化 F = {v}, R = N(v)
    F = {v}
    R = get_neighbors(G, v)

    # 第2行：while R != 空集
    while R:
        # 第3-5行：计算 R 中每个节点与 F 的连接边数
        edge_counts = {}
        for node in R:
            edge_counts[node] = count_edges_between(G, F, node)

        # 第6行：选择与F连接最多的节点；并列选度最小的
        max_edges = max(edge_counts.values())
        candidates = [node for node in R if edge_counts[node] == max_edges]
        w = min(candidates, key=lambda node: get_degree(G, node))

        # 第7-9行：检查加入w后链接密度是否仍 >= gamma
        F_tentative = F | {w}
        if link_density(G, F_tentative) < gamma:
            break  # 第8行：不满足，退出

        # 第10行：将w加入F
        F.add(w)

        # 第11行：更新R = (F的所有邻居) - F
        R = set()
        for node in F:
            for neighbor in G.neighbors(node):
                if neighbor not in F:
                    R.add(neighbor)

    # 第12行：返回折叠子图
    return F
