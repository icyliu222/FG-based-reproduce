"""
评估模块：recall、precision、F-score
对网络中每个节点作为起始节点检测社区，取所有节点的平均值
"""


def evaluate_single(C_found, C_true):
    """
    计算单次检测的 recall、precision、F-score

    参数:
        C_found: 检测到的社区 (set)
        C_true: 真实社区 (set)

    返回:
        (recall, precision, fscore)
    """
    if len(C_true) == 0:
        return 0.0, 0.0, 0.0
    if len(C_found) == 0:
        return 0.0, 0.0, 0.0

    intersection = C_found & C_true
    recall = len(intersection) / len(C_true)
    precision = len(intersection) / len(C_found)
    if precision + recall == 0:
        fscore = 0.0
    else:
        fscore = 2 * precision * recall / (precision + recall)
    return recall, precision, fscore


def evaluate_method(G, true_communities, detect_function, **kwargs):
    """
    对全网络所有节点取平均的评估

    参数:
        G: 网络图
        true_communities: {node: community_label} 字典
        detect_function: 检测函数，接收 (G, start_node, **kwargs) 返回社区集合
        **kwargs: 传给 detect_function 的参数

    返回:
        dict: 包含 recall, precision, fscore 的平均值，以及各节点的详细列表
    """
    all_recall = []
    all_precision = []
    all_fscore = []

    nodes = list(G.nodes())
    for start_node in nodes:
        # 检测社区
        C_found = detect_function(G, start_node, **kwargs)

        # 找到起始节点的真实社区
        true_label = true_communities[start_node]
        C_true = {node for node in G.nodes() if true_communities[node] == true_label}

        # 计算指标
        recall, precision, fscore = evaluate_single(C_found, C_true)
        all_recall.append(recall)
        all_precision.append(precision)
        all_fscore.append(fscore)

    n = len(all_recall)
    return {
        'recall': sum(all_recall) / n,
        'precision': sum(all_precision) / n,
        'fscore': sum(all_fscore) / n,
        'recall_list': all_recall,
        'precision_list': all_precision,
        'fscore_list': all_fscore,
    }
