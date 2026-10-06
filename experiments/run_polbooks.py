"""
Polbooks 数据集实验入口
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import load_polbooks
from src.fg_method import fg_based_detect
from src.baseline import m_based_detect
from src.evaluate import evaluate_method


def main():
    print("=" * 60)
    print("Polbooks 数据集实验")
    print("=" * 60)

    G, true_communities = load_polbooks()
    print(f"节点数: {G.number_of_nodes()}, 边数: {G.number_of_edges()}")

    gamma = 0.6
    h = 0.6
    beta = 0.5

    print("\n运行 FG-based 方法...")
    fg_results = evaluate_method(
        G, true_communities,
        detect_function=fg_based_detect,
        gamma=gamma, h=h, beta=beta
    )

    print("运行 M-based 基线...")
    m_results = evaluate_method(
        G, true_communities,
        detect_function=m_based_detect
    )

    print("\n" + "=" * 60)
    print(f"{'方法':<15} {'Recall':<12} {'Precision':<12} {'F-score':<12}")
    print("-" * 60)
    print(f"{'M-based':<15} {m_results['recall']:<12.4f} {m_results['precision']:<12.4f} {m_results['fscore']:<12.4f}")
    print(f"{'FG-based':<15} {fg_results['recall']:<12.4f} {fg_results['precision']:<12.4f} {fg_results['fscore']:<12.4f}")
    print("=" * 60)

    print("\n论文 Table III 参考值:")
    print(f"  M-based:  Recall=0.4837, Precision=0.7664, F=0.5257")
    print(f"  FG-based: Recall=0.8848, Precision=0.7359, F=0.7923")

    results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
    os.makedirs(results_dir, exist_ok=True)
    with open(os.path.join(results_dir, "polbooks_results.csv"), 'w', encoding='utf-8') as f:
        f.write("dataset,method,recall,precision,fscore,gamma,h\n")
        f.write(f"polbooks,M-based,{m_results['recall']:.6f},{m_results['precision']:.6f},{m_results['fscore']:.6f},,\n")
        f.write(f"polbooks,FG-based,{fg_results['recall']:.6f},{fg_results['precision']:.6f},{fg_results['fscore']:.6f},{gamma},{h}\n")
    print(f"\n结果已保存到 results/polbooks_results.csv")


if __name__ == "__main__":
    main()
