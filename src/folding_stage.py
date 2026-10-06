"""
Algorithm 2：折叠阶段（Folding Stage）
处理"半归属"节点：折叠子图中 >=50% 节点已在社区内 → 整体加入
"""
from .folded_subgraph import construct_folded_subgraph
from .graph_utils import build_candidate_set


def folding_stage(G, C, A, gamma):
    """
    折叠阶段扩展

    参数:
        G: 局部网络
        C: 当前社区 (set)
        A: 候选集 (set)
        gamma: 折叠子图链接密度阈值

    返回:
        (C, A): 更新后的社区和候选集
    """
    while True:
        added_any = False

        # 第2-8行：遍历候选集中每个节点
        # 注意：遍历 A 的副本，因为循环中可能更新 A
        for v in list(A):
            if v not in A:
                continue
            # 第3行：构造v的折叠子图
            F_v = construct_folded_subgraph(G, v, gamma)

            # 第4行：判断折叠子图中是否 >= 50% 已在社区内
            intersection = F_v & C
            if len(intersection) >= 0.5 * len(F_v):
                # 第5行：将整个折叠子图加入社区
                C = C | F_v
                # 第6行：更新候选集A
                A = build_candidate_set(G, C)
                added_any = True

        # 第9-11行：如果一轮中没有新节点加入，退出
        if not added_any:
            break

    return C, A
