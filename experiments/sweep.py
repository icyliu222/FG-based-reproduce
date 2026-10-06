"""
二维超参数扫描：γ × h
测试 γ ∈ {0.6, 0.8, 1.0} 和 h ∈ {0.6, 0.8, 1.0, 1.2, 1.4}
在所有6个数据集上的 FG-based 表现
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import load_dataset
from src.fg_method import fg_based_detect
from src.evaluate import evaluate_method


def main():
    datasets = ['dolphins']
    gamma_values = [0.6, 0.8, 1.0]
    h_values = [0.6, 0.8, 1.0, 1.2, 1.4]
    beta = 0.5

    # results[dataset][gamma][h] = {recall, precision, fscore}
    results = {}

    for ds in datasets:
        print(f"\n{'='*60}")
        print(f"  {ds.upper()}")
        print(f"{'='*60}")
        G, true_communities = load_dataset(ds)
        print(f"节点={G.number_of_nodes()}, 边={G.number_of_edges()}")

        results[ds] = {}
        for gamma in gamma_values:
            results[ds][gamma] = {}
            print(f"\n  --- γ={gamma} ---")
            for h in h_values:
                res = evaluate_method(
                    G, true_communities,
                    detect_function=fg_based_detect,
                    gamma=gamma, h=h, beta=beta
                )
                results[ds][gamma][h] = res
                print(f"    h={h:<5} R={res['recall']:.4f}  P={res['precision']:.4f}  F={res['fscore']:.4f}")

    # 按 γ 分组的汇总表（F-score）
    for gamma in gamma_values:
        print(f"\n\n{'='*80}")
        print(f"  F-score 汇总 — γ={gamma}（β={beta}）")
        print(f"{'='*80}")
        print(f"  {'数据集':<10}", end="")
        for h in h_values:
            print(f" {'h='+str(h):<14}", end="")
        print(f" {'最优h':<8} {'最优F':<8}")
        print(f"  {'-'*85}")
        for ds in datasets:
            print(f"  {ds:<10}", end="")
            for h in h_values:
                r = results[ds][gamma][h]
                print(f" {r['fscore']:<14.4f}", end="")
            best_h = max(h_values, key=lambda h: results[ds][gamma][h]['fscore'])
            best_f = results[ds][gamma][best_h]['fscore']
            print(f" {best_h:<8} {best_f:<8.4f}")
        print(f"{'='*80}")

    # 全局最优：每个数据集的最优 (γ, h)
    print(f"\n\n{'='*80}")
    print("  各数据集全局最优参数（按 F-score）")
    print(f"{'='*80}")
    print(f"  {'数据集':<10} {'γ':<6} {'h':<6} {'Recall':<10} {'Precision':<10} {'F-score':<10}")
    print(f"  {'-'*55}")
    for ds in datasets:
        best_gamma = None
        best_h = None
        best_f = -1
        for gamma in gamma_values:
            for h in h_values:
                f = results[ds][gamma][h]['fscore']
                if f > best_f:
                    best_f = f
                    best_gamma = gamma
                    best_h = h
        best = results[ds][best_gamma][best_h]
        print(f"  {ds:<10} {best_gamma:<6} {best_h:<6} {best['recall']:<10.4f} {best['precision']:<10.4f} {best['fscore']:<10.4f}")
    print(f"{'='*80}")

    # 保存完整结果
    results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
    os.makedirs(results_dir, exist_ok=True)
    out_path = os.path.join(results_dir, "gamma_h_sweep1.csv")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("dataset,gamma,h,recall,precision,fscore,beta\n")
        for ds in datasets:
            for gamma in gamma_values:
                for h in h_values:
                    r = results[ds][gamma][h]
                    f.write(f"{ds},{gamma},{h},{r['recall']:.6f},{r['precision']:.6f},{r['fscore']:.6f},{beta}\n")
    print(f"\n完整结果已保存到 results/gamma_h_sweep1.csv")


if __name__ == "__main__":
    main()
