"""Qwen vs Llama on the same held-out evaluation: leak rate and disclosure to authorized requesters
for setups (a), (b), (c), side by side. Reuses the helpers of plot_results.py (not modified).

  python3 scripts/plot_compare_models.py results/eval_run1 results/eval_llama_run1 results/figures_compare

Writes 5_models_compare.png (slides) and .pdf (report). Needs matplotlib.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plot_results as pr  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

MODELS = [("Qwen3-4B", "eval_Qwen3-4B-Instruct-2507_{s}"), ("Llama-3.2-3B", "eval_Llama-3.2-3B-Instruct_{s}")]


def main(qwen_run, llama_run, out):
    runs = [Path(qwen_run), Path(llama_run)]
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rows = {}
    for (name, pattern), run in zip(MODELS, runs):
        for s, _ in pr.SETUPS:
            path = run / pattern.format(s=s) / "scored.jsonl"
            rows[(name, s)] = [json.loads(line) for line in path.open()]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "text.color": pr.INK,
                         "axes.labelcolor": pr.INK2, "figure.facecolor": pr.SURFACE})
    leak = lambda r: r["leak"] if not r["target_allowed"] else None  # noqa: E731
    disclosed = lambda r: r["disclosed"]  # noqa: E731
    panels = [("Leak rate (lower is better)", leak),
              ("Disclosure to authorized requesters (higher is better)", disclosed)]
    xs = list(range(len(MODELS)))
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for ax, (title, m) in zip(axes, panels):
        pr.style(ax)
        data = {s: {x: pr.rate(rows[(name, s)], m) for x, (name, _) in zip(xs, MODELS)} for s, _ in pr.SETUPS}
        pr.bars(ax, xs, data, width=0.26, label_size=9)
        ax.set_xticks(xs)
        ax.set_xticklabels([name for name, _ in MODELS])
        ax.set_title(title, fontsize=10, color=pr.INK)
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="lower center", ncol=3, frameon=False)
    fig.suptitle("Both models on the held-out evaluation (2,880 tasks per setup, 95% intervals)",
                 fontsize=12, color=pr.INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    pr.save(fig, out / "5_models_compare")
    print(f"wrote {out}")


if __name__ == "__main__":
    a = sys.argv[1:] + [None] * 3
    main(a[0] or "results/eval_run1", a[1] or "results/eval_llama_run1", a[2] or "results/figures_compare")
