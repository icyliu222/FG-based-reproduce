"""
Algorithm 4：松弛阶段（Relaxation Stage）
处理"弱连接"节点：用一阶+二阶邻居相似度 f(v) = f1(v) + β*f2(v)
每轮只加入一个折叠子图，然后回到整体循环
"""
from .folded_subgraph import construct_folded_subgraph
from .graph_utils import (
    get_neighbors, get_second_order_neighbors,
    build_candidate_set, count_internal_edges, count_external_edges
)


def relaxation_stage(G, C, A, gamma, h, beta=0.5):
    """
    松弛阶段扩展（每轮最多加入一个折叠子图）

    参数:
        G: 局部网络
        C: 当前社区 (set)
        A: 候选集 (set)
        gamma: 折叠子图链接密度阈值
        h: 松弛阶段加入阈值 (0 <= h <= 1)
        beta: f1/f2 权重比，固定 0.5

    返回:
        (C, A): 更新后的社区和候选集
    """
    if not A:
        return C, A

    # 第1-4行：计算每个候选节点的相似度
    f_dict = {}
    F_dict = {}

    for v in A:
        # 第2行：构造折叠子图
        F_v = construct_folded_subgraph(G, v, gamma)
        F_dict[v] = F_v

        # 第3行：计算 f1(v)（公式6）
        # 折叠子图所有节点的一阶邻居并集，与C的交集大小，归一化到|C|
        first_order_union = set()
        for i in F_v:
            first_order_union |= get_neighbors(G, i)
        f1 = len(first_order_union & C) / len(C) if len(C) > 0 else 0.0

        # 计算 f2(v)（公式7）
        # 折叠子图所有节点的二阶邻居并集，与C的交集大小，归一化到|C|
        second_order_union = set()
        for i in F_v:
            second_order_union |= get_second_order_neighbors(G, i)
        f2 = len(second_order_union & C) / len(C) if len(C) > 0 else 0.0

        # 综合相似度
        f_v = f1 + beta * f2
        f_dict[v] = f_v

    # 第5行：找最大相似度
    v_best = max(f_dict, key=f_dict.get)
    f_best = f_dict[v_best]
    F_best = F_dict[v_best]

    # 第6-9行：如果 f_best >= h，加入社区
    if f_best >= h:
        C = C | F_best
        # 更新 e_in, e_out, A（e_in/e_out 由调用方维护，这里只更新A）
        A = build_candidate_set(G, C)

    return C, A
