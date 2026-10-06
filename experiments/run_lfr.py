"""
LFR 合成网络实验入口
运行 LFR1(μ=0.1)、LFR2(μ=0.2)、LFR5(μ=0.5) 三组实验
论文 Table I 参数（LFR1-5）：N=200, k=7, maxk=15, t1=2, t2=1, minc=10, maxc=80

每个数据集使用各自调优后的最优 (γ, h)：
  LFR1: γ=0.8, h=0.8
  LFR2: γ=0.6, h=1.0
  LFR5: γ=0.8, h=0.6
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import load_lfr
from src.fg_method import fg_based_detect
from src.baseline import m_based_detect
from src.evaluate import evaluate_method


# 每个 LFR 数据集的最优超参数（来自 γ×h 二维扫描）
LFR_PARAMS = {
    0.1: {'name': 'LFR1', 'gamma': 0.8, 'h': 0.8},
    0.2: {'name': 'LFR2', 'gamma': 0.6, 'h': 1.0},
    0.5: {'name': 'LFR5', 'gamma': 0.8, 'h': 0.6},
}


def run_lfr_experiment(mu, beta=0.5):
    """运行单组 LFR 实验，使用该数据集对应的最优 (γ, h)"""
    params = LFR_PARAMS[mu]
    name = params['name']
    gamma = params['gamma']
    h = params['h']

    print(f"\n{'='*60}")
    print(f"  {name} (μ={mu})  γ={gamma}, h={h}")
    print(f"  (N=200, k=7, maxk=15, t1=2, t2≈1, minc=10, maxc=80)")
    print(f"{'='*60}")

    # 生成 LFR 网络
    G, true_communities = load_lfr(mu=mu)
    n_communities = len(set(true_communities.values()))
    print(f"节点数: {G.number_of_nodes()}, 边数: {G.number_of_edges()}, 社区数: {n_communities}")

    # 运行 FG-based
    print("  运行 FG-based 方法...")
    fg_results = evaluate_method(
        G, true_communities,
        detect_function=fg_based_detect,
        gamma=gamma, h=h, beta=beta
    )

    # 运行 M-based 基线
    print("  运行 M-based 基线...")
    m_results = evaluate_method(
        G, true_communities,
        detect_function=m_based_detect
    )

    # 打印结果
    print(f"\n  {'方法':<12} {'Recall':<10} {'Precision':<10} {'F-score':<10}")
    print(f"  {'-'*45}")
    print(f"  {'M-based':<12} {m_results['recall']:<10.4f} {m_results['precision']:<10.4f} {m_results['fscore']:<10.4f}")
    print(f"  {'FG-based':<12} {fg_results['recall']:<10.4f} {fg_results['precision']:<10.4f} {fg_results['fscore']:<10.4f}")

    return mu, gamma, h, m_results, fg_results


def main():
    mu_list = [0.1, 0.2, 0.5]
    all_results = []

    for mu in mu_list:
        mu, gamma, h, m_res, fg_res = run_lfr_experiment(mu)
        all_results.append((mu, gamma, h, m_res, fg_res))

    # 汇总表
    print(f"\n\n{'='*75}")
    print("  LFR 汇总结果（各数据集使用最优 γ, h）")
    print(f"{'='*75}")
    print(f"  {'数据集':<8} {'γ':<5} {'h':<5} {'方法':<10} {'Recall':<10} {'Precision':<10} {'F-score':<10}")
    print(f"  {'-'*65}")
    for mu, gamma, h, m_res, fg_res in all_results:
        name = LFR_PARAMS[mu]['name']
        print(f"  {name:<8} {gamma:<5} {h:<5} {'M-based':<10} {m_res['recall']:<10.4f} {m_res['precision']:<10.4f} {m_res['fscore']:<10.4f}")
        print(f"  {'':<8} {'':<5} {'':<5} {'FG-based':<10} {fg_res['recall']:<10.4f} {fg_res['precision']:<10.4f} {fg_res['fscore']:<10.4f}")
    print(f"{'='*75}")

    # 保存结果
    results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
    os.makedirs(results_dir, exist_ok=True)
    with open(os.path.join(results_dir, "lfr_results.csv"), 'w', encoding='utf-8') as f:
        f.write("dataset,mu,gamma,h,method,recall,precision,fscore\n")
        for mu, gamma, h, m_res, fg_res in all_results:
            name = LFR_PARAMS[mu]['name']
            f.write(f"{name},{mu},{gamma},{h},M-based,{m_res['recall']:.6f},{m_res['precision']:.6f},{m_res['fscore']:.6f}\n")
            f.write(f"{name},{mu},{gamma},{h},FG-based,{fg_res['recall']:.6f},{fg_res['precision']:.6f},{fg_res['fscore']:.6f}\n")
    print(f"\n结果已保存到 results/lfr_results.csv")


if __name__ == "__main__":
    main()
