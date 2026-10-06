"""
批量运行所有数据集实验（Karate + Dolphins + Polbooks + LFR1/LFR2/LFR5）
每个数据集使用各自调优后的最优 (γ, h) 参数
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import load_dataset
from src.fg_method import fg_based_detect
from src.baseline import m_based_detect
from src.evaluate import evaluate_method


# 每个数据集的最优超参数（来自 γ×h 二维扫描）
DATASET_PARAMS = {
    'karate':   {'gamma': 0.6, 'h': 1.0},
    'dolphins': {'gamma': 1.0, 'h': 0.6},
    'polbooks': {'gamma': 0.6, 'h': 0.6},
    'lfr1':     {'gamma': 0.8, 'h': 0.8},
    'lfr2':     {'gamma': 0.6, 'h': 1.0},
    'lfr5':     {'gamma': 0.8, 'h': 0.6},
}

BETA = 0.5


def run_one(dataset_name):
    """运行单个数据集的实验，使用该数据集对应的最优 (γ, h)"""
    params = DATASET_PARAMS[dataset_name]
    gamma = params['gamma']
    h = params['h']

    print(f"\n{'='*60}")
    print(f"  {dataset_name.upper()} 数据集  (γ={gamma}, h={h})")
    print(f"{'='*60}")

    G, true_communities = load_dataset(dataset_name)
    n_comm = len(set(true_communities.values()))
    print(f"节点数: {G.number_of_nodes()}, 边数: {G.number_of_edges()}, 社区数: {n_comm}")

    print("  运行 FG-based...")
    fg_results = evaluate_method(
        G, true_communities,
        detect_function=fg_based_detect,
        gamma=gamma, h=h, beta=BETA
    )

    print("  运行 M-based...")
    m_results = evaluate_method(
        G, true_communities,
        detect_function=m_based_detect
    )

    print(f"\n  {'方法':<12} {'Recall':<10} {'Precision':<10} {'F-score':<10}")
    print(f"  {'-'*45}")
    print(f"  {'M-based':<12} {m_results['recall']:<10.4f} {m_results['precision']:<10.4f} {m_results['fscore']:<10.4f}")
    print(f"  {'FG-based':<12} {fg_results['recall']:<10.4f} {fg_results['precision']:<10.4f} {fg_results['fscore']:<10.4f}")

    return gamma, h, m_results, fg_results


def main():
    datasets = ['karate', 'dolphins', 'polbooks', 'lfr1', 'lfr2', 'lfr5']
    all_results = {}

    for ds in datasets:
        gamma, h, m_res, fg_res = run_one(ds)
        all_results[ds] = (gamma, h, m_res, fg_res)

    # 汇总表
    print(f"\n\n{'='*80}")
    print("  全部数据集汇总结果（各数据集使用最优 γ, h）")
    print(f"{'='*80}")
    print(f"  {'数据集':<10} {'γ':<5} {'h':<5} {'方法':<10} {'Recall':<10} {'Precision':<10} {'F-score':<10}")
    print(f"  {'-'*65}")
    for ds in datasets:
        gamma, h, m_res, fg_res = all_results[ds]
        print(f"  {ds:<10} {gamma:<5} {h:<5} {'M-based':<10} {m_res['recall']:<10.4f} {m_res['precision']:<10.4f} {m_res['fscore']:<10.4f}")
        print(f"  {'':<10} {'':<5} {'':<5} {'FG-based':<10} {fg_res['recall']:<10.4f} {fg_res['precision']:<10.4f} {fg_res['fscore']:<10.4f}")
    print(f"{'='*80}")

    # 保存汇总结果
    results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
    os.makedirs(results_dir, exist_ok=True)
    with open(os.path.join(results_dir, "all_results.csv"), 'w', encoding='utf-8') as f:
        f.write("dataset,gamma,h,method,recall,precision,fscore,beta\n")
        for ds in datasets:
            gamma, h, m_res, fg_res = all_results[ds]
            f.write(f"{ds},{gamma},{h},M-based,{m_res['recall']:.6f},{m_res['precision']:.6f},{m_res['fscore']:.6f},{BETA}\n")
            f.write(f"{ds},{gamma},{h},FG-based,{fg_res['recall']:.6f},{fg_res['precision']:.6f},{fg_res['fscore']:.6f},{BETA}\n")
    print(f"\n汇总结果已保存到 results/all_results.csv")


if __name__ == "__main__":
    main()
