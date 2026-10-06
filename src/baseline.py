"""
M-based 基线方法：基于局部模块度 M = e_in/e_out 的贪心扩展
不使用折叠子图，每次只加入单个节点
作为 FG-based 方法的对比基线
"""
from .graph_utils import (
    get_neighbors, get_degree, build_candidate_set,
    count_internal_edges, count_external_edges
)


def m_based_detect(G, start_node):
    """
    M-based 局部社区检测

    参数:
        G: 全图
        start_node: 起始节点

    返回:
        C: 检测到的局部社区 (set)
    """
    C = {start_node}
    A = build_candidate_set(G, C)
    e_in = 0
    e_out = count_external_edges(G, C)

    while A:
        best_delta = float('-inf')
        best_v = None

        for v in A:
            # 计算加入单个节点v后的模块度增益
            # x = v与C的连接数
            x = len(get_neighbors(G, v) & C)
            # z = v与外部的连接数 = degree(v) - x
            z = get_degree(G, v) - x

            denom = e_out + z
            if denom <= 0 or e_out <= 0:
                delta = float('-inf')
            else:
                delta = (e_in + x) / denom - e_in / e_out

            if delta > best_delta:
                best_delta = delta
                best_v = v

        if best_delta < 0:
            break

        C.add(best_v)
        e_in = count_internal_edges(G, C)
        e_out = count_external_edges(G, C)
        A = build_candidate_set(G, C)

    return C
