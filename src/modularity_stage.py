"""
Algorithm 3：基于模块度的扩展阶段（Modularity-Based Expansion Stage）
处理"强连接"节点：选择使局部模块度 M = e_in/e_out 增益最大的折叠子图加入
"""
from .folded_subgraph import construct_folded_subgraph
from .graph_utils import (
    get_neighbors, get_degree, build_candidate_set,
    count_internal_edges, count_external_edges
)


def modularity_stage(G, C, A, gamma, e_in, e_out):
    """
    模块度扩展阶段

    参数:
        G: 局部网络
        C: 当前社区 (set)
        A: 候选集 (set)
        gamma: 折叠子图链接密度阈值
        e_in: 当前社区内部边数
        e_out: 当前社区与外部之间的边数

    返回:
        (C, A, e_in, e_out): 更新后的社区、候选集、内部边数、外部边数
    """
    # 第1行：while A != 空集
    while A:
        # 第2-5行：计算每个候选节点的模块度增益
        delta_M_dict = {}
        F_dict = {}

        for v in A:
            # 第3行：构造折叠子图
            F_v = construct_folded_subgraph(G, v, gamma)
            F_dict[v] = F_v

            # 第4行：计算 ΔM（公式5）
            # x: F(v)-C 中节点与 C 的连接数（公式2）
            F_minus_C = F_v - C
            x = 0
            for i in F_minus_C:
                x += len(get_neighbors(G, i) & C)

            # y: F(v)∩A 中节点与 C 的连接数（公式3）
            F_intersect_A = F_v & A
            y = 0
            for i in F_intersect_A:
                y += len(get_neighbors(G, i) & C)

            # z: F(v)-C 中节点与社区外部的边数（公式4）
            total_degree = sum(get_degree(G, i) for i in F_minus_C)
            internal_count = 0
            for i in F_minus_C:
                internal_count += len(get_neighbors(G, i) & F_minus_C)
            z = total_degree - x - 0.5 * internal_count

            # 计算 ΔM（公式5）
            denom = e_out + z - y
            if denom <= 0:
                delta_M = float('-inf')
            else:
                delta_M = (e_in + x) / denom - e_in / e_out if e_out > 0 else float('-inf')

            delta_M_dict[v] = delta_M

        # 第6行：找最大增益
        v_best = max(delta_M_dict, key=delta_M_dict.get)
        delta_M_best = delta_M_dict[v_best]
        F_best = F_dict[v_best]

        # 第7-9行：如果最大增益为负，退出
        if delta_M_best < 0:
            break

        # 第10行：将最佳折叠子图加入社区
        C = C | F_best

        # 第11行：更新 e_in, e_out, A
        e_in = count_internal_edges(G, C)
        e_out = count_external_edges(G, C)
        A = build_candidate_set(G, C)

    return C, A, e_in, e_out
