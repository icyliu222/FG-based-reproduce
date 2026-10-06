"""
图工具函数：邻居、度、链接密度、候选集构建等
"""


def get_neighbors(G, v):
    """返回节点 v 的邻居集合"""
    return set(G.neighbors(v))


def get_degree(G, v):
    """返回节点 v 的度数"""
    return G.degree(v)


def count_edges_between(G, node_set, v):
    """计算节点 v 与集合 node_set 之间的边数"""
    return sum(1 for u in node_set if G.has_edge(v, u))


def link_density(G, node_set):
    """链接密度 = 实际内部边数 / 完全图边数 = 2*|E| / (n*(n-1))"""
    n = len(node_set)
    if n <= 1:
        return 1.0
    node_list = list(node_set)
    internal_edges = 0
    for i in range(n):
        for j in range(i + 1, n):
            if G.has_edge(node_list[i], node_list[j]):
                internal_edges += 1
    max_edges = n * (n - 1) / 2.0
    return internal_edges / max_edges


def get_second_order_neighbors(G, v):
    """二阶邻居集合 NN(v) = N(N(v))，不含 v 自身和一阶邻居"""
    first_order = get_neighbors(G, v)
    result = set()
    for u in first_order:
        for w in G.neighbors(u):
            if w != v and w not in first_order:
                result.add(w)
    return result


def build_candidate_set(G, C):
    """构建候选集 A = 所有 C 中节点的邻居，减去 C 自身"""
    A = set()
    for v in C:
        for u in G.neighbors(v):
            if u not in C:
                A.add(u)
    return A


def count_internal_edges(G, C):
    """社区 C 内部边数"""
    C_list = list(C)
    count = 0
    for i in range(len(C_list)):
        for j in range(i + 1, len(C_list)):
            if G.has_edge(C_list[i], C_list[j]):
                count += 1
    return count


def count_external_edges(G, C):
    """社区 C 与外部之间的边数"""
    count = 0
    for v in C:
        for u in G.neighbors(v):
            if u not in C:
                count += 1
    return count
