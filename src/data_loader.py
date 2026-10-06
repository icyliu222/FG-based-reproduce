"""
数据加载模块：统一加载 Karate、Dolphins、Polbooks 三个数据集
返回 (G, true_communities)，其中 true_communities 是 {node: community_label} 字典
"""
import json
import os
import networkx as nx

DATA_DIR = r"D:\FG-based\data"


def load_karate():
    """Karate 空手道俱乐部网络：34节点/78边/2社区，networkx 内置"""
    G = nx.karate_club_graph()
    # 节点为整数 0-33，社区标签在 'club' 属性中（'Mr. Hi' / 'Officer'）
    true_communities = {node: G.nodes[node]['club'] for node in G.nodes()}
    return G, true_communities


def load_dolphins():
    """Dolphins 海豚社交网络：62节点/159边/2社区
    拓扑从 GML 读取，社区标签从 JSON 读取（greedy modularity 生成的 40/22 划分）
    """
    gml_path = os.path.join(DATA_DIR, "dolphins", "dolphins.gml")
    json_path = os.path.join(DATA_DIR, "dolphins", "dolphins_labels.json")

    G = nx.read_gml(gml_path)
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # labels 字段: {海豚名字: 0或1}
    true_communities = data['labels']

    # 验证所有节点都有标签
    missing = [n for n in G.nodes() if n not in true_communities]
    if missing:
        raise ValueError(f"Dolphins 缺失标签的节点: {missing}")
    return G, true_communities


def load_polbooks():
    """Polbooks 美国政治书籍网络：105节点/441边/3社区
    拓扑和标签都在 GML 中，社区标签在 'value' 属性中（'c'保守/'l'自由/'n'中立）
    """
    gml_path = os.path.join(DATA_DIR, "polbooks", "polbooks.gml")
    G = nx.read_gml(gml_path)
    true_communities = {node: G.nodes[node]['value'] for node in G.nodes()}
    return G, true_communities


def load_dataset(name):
    """统一加载入口"""
    name = name.lower().strip()
    if name == 'karate':
        return load_karate()
    elif name == 'dolphins':
        return load_dolphins()
    elif name == 'polbooks':
        return load_polbooks()
    elif name.startswith('lfr'):
        # lfr1 / lfr2 / lfr5 等，mu 由名称映射
        mu_map = {'lfr1': 0.1, 'lfr2': 0.2, 'lfr3': 0.3, 'lfr4': 0.4, 'lfr5': 0.5}
        if name not in mu_map:
            raise ValueError(f"未知 LFR 数据集: {name}，可选: lfr1/lfr2/lfr3/lfr4/lfr5")
        return load_lfr(mu=mu_map[name])
    else:
        raise ValueError(f"未知数据集: {name}，可选: karate / dolphins / polbooks / lfr1~lfr5")


def load_lfr(n=200, tau1=2.5, tau2=1.5, mu=0.1, average_degree=7,
             max_degree=None, min_community=10, max_community=80, seed=3):
    """
    生成 LFR 合成网络（论文 Table I，LFR1-LFR5）

    论文原始参数: N=200, k=7, maxk=15, μ=0.1~0.5, t1=2, t2=1, minc=10, maxc=80

    实际生成参数调整说明:
    - networkx 的 LFR_benchmark_graph 要求 tau2 > 1（论文 t2=1 无法直接使用），
      故采用 tau2=1.5
    - tau1=2 配合 max_degree=15 在 N=200 下生成器难以收敛，
      故采用 tau1=2.5 且不设 max_degree（度分布自然收敛）
    - 核心实验变量 μ（混合系数）和网络规模 N=200、平均度 k=7、
      社区大小范围 minc=10~maxc=80 均保持论文设定
    - seed=3 对 μ=0.1~0.5 均能稳定生成

    返回:
        (G, true_communities): 图和 {node: community_id} 字典
    """
    from networkx.generators.community import LFR_benchmark_graph

    G = None
    for s in range(seed, seed + 20):
        try:
            kwargs = dict(
                n=n, tau1=tau1, tau2=tau2, mu=mu,
                average_degree=average_degree,
                min_community=min_community, max_community=max_community,
                seed=s
            )
            if max_degree is not None:
                kwargs['max_degree'] = max_degree
            G = LFR_benchmark_graph(**kwargs)
            break
        except Exception:
            continue

    if G is None:
        raise RuntimeError(f"LFR 生成失败（mu={mu}），请尝试调整 seed")

    # 提取真实社区：节点属性 'community' 是 frozenset（on=0 时每个节点只属一个社区）
    true_communities = {}
    for node in G.nodes():
        comm_set = G.nodes[node]['community']
        comm_id = min(comm_set)
        true_communities[node] = comm_id

    return G, true_communities
