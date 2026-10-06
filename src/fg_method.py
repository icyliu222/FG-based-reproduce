"""
Algorithm 5：FG-based 整体流程
三阶段循环：折叠阶段 → 模块度扩展阶段 → 松弛阶段 → 折叠阶段 → ...
"""
from .folding_stage import folding_stage
from .modularity_stage import modularity_stage
from .relaxation_stage import relaxation_stage
from .graph_utils import build_candidate_set, count_internal_edges, count_external_edges


def fg_based_detect(G, start_node, gamma=0.8, h=1.0, beta=0.5):
    """
    FG-based 局部社区检测主流程

    参数:
        G: 全图 (networkx.Graph)
        start_node: 起始节点
        gamma: 折叠子图链接密度阈值 (建议 >= 0.5)
        h: 松弛阶段加入阈值 (0 <= h <= 1)
        beta: f1/f2 权重比，固定 0.5

    返回:
        C: 检测到的局部社区 (set)
    """
    # 初始化：社区从起始节点开始
    C = {start_node}
    A = build_candidate_set(G, C)

    # 计算初始 e_in, e_out
    e_in = 0  # 单个节点没有内部边
    e_out = count_external_edges(G, C)

    # 第1行：nums1 = nums2 = |C|
    nums1 = len(C)
    nums2 = len(C)

    # 第2行：while A != 空集
    while A:
        # 第3行：折叠阶段
        C, A = folding_stage(G, C, A, gamma)

        # 第4行：模块度扩展阶段
        C, A, e_in, e_out = modularity_stage(G, C, A, gamma, e_in, e_out)

        # 第5行：nums1 = |C|
        nums1 = len(C)

        # 第6-8行：如果前两阶段后社区大小不变，退出
        if nums1 == nums2:
            break

        # 第9行：松弛阶段
        C, A = relaxation_stage(G, C, A, gamma, h, beta)

        # 松弛后更新 e_in, e_out
        e_in = count_internal_edges(G, C)
        e_out = count_external_edges(G, C)

        # 第10行：nums2 = |C|
        nums2 = len(C)

    return C
