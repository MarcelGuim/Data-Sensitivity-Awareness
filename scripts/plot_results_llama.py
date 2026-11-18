"""Copy of plot_results.py (unchanged) for the Llama run: only the folder name and title differ.
Figures for the report and slides from the scored.jsonl files of one evaluation run.

  python3 scripts/plot_results_llama.py results/eval_llama_run1

Writes PNG (slides) and PDF (report) into <run>/figures/. Needs matplotlib.
(c)+policy is left out of the figures: its metrics equal (c) (docs/05, Results run 1).
Bars are rates with Wilson 95% intervals (same as kaggle/eval/summarize.py).
"""
import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SETUPS = [("a", "(a) untrained"), ("b", "(b) policy prompt"), ("c", "(c) trained")]
COLORS = {"a": "#2a78d6", "b": "#eb6834", "c": "#1baf7a"}  # validated categorical slots 1-3
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
FAMILIES = ["benign", "direct", "tampering", "paraphrase", "summary", "indirect_email",
            "indirect_document", "encoding"]
HELD_OUT = {"indirect_document", "encoding"}
TIERS = ["public", "private", "confidential"]


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def rate(rows, metric):
    vals = [bool(metric(r)) for r in rows if metric(r) is not None]
    k, n = sum(vals), len(vals)
    lo, hi = wilson(k, n)
    return (100 * k / n if n else 0.0, 100 * lo, 100 * hi, n)


def style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK2, length=0)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_ylim(0, 112)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels([f"{t}%" for t in [0, 25, 50, 75, 100]])


def bars(ax, groups, data, width=0.26, label_size=8):
    """data[setup][group] = (rate, lo, hi, n). Grouped bars with CI whiskers and value labels."""
    for i, (s, name) in enumerate(SETUPS):
        xs = [g + (i - 1) * width for g in range(len(groups))]
        vals = [data[s][g] for g in groups]
        ax.bar(xs, [v[0] for v in vals], width - 0.03, color=COLORS[s], label=name,
               edgecolor=SURFACE, linewidth=1)
        ax.errorbar(xs, [v[0] for v in vals],
                    yerr=[[max(0, v[0] - v[1]) for v in vals], [max(0, v[2] - v[0]) for v in vals]],
                    fmt="none", ecolor=INK2, elinewidth=0.9, capsize=2)
        for x, v in zip(xs, vals):
            ax.text(x, v[2] + 1.5, f"{v[0]:.0f}", ha="center", va="bottom", fontsize=label_size, color=INK)


def main(run):
    run = Path(run)
    rows = {s: [json.loads(line) for line in (run / f"eval_Llama-3.2-3B-Instruct_{s}" / "scored.jsonl").open()]
            for s, _ in SETUPS}
    out = run / "figures"
    out.mkdir(exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "text.color": INK,
                         "axes.labelcolor": INK2, "figure.facecolor": SURFACE})
    leak = lambda r: r["leak"] if not r["target_allowed"] else None  # noqa: E731
    disclosed = lambda r: r["disclosed"]  # noqa: E731
    tierword = lambda r: r["tier_word"]  # noqa: E731
    email = lambda r: r["task_done"] if r["family"] == "indirect_email" else None  # noqa: E731

    # 1. headline: security and utility side by side (separate panels, one axis each)
    panels = [("Leak rate\n(lower is better)", leak), ("Disclosure to authorized\nrequesters (higher is better)", disclosed),
              ("Email task done\n(higher is better)", email), ("Refusals naming the tier\n(lower is better)", tierword)]
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.8), sharey=True)
    for ax, (title, m) in zip(axes, panels):
        style(ax)
        data = {s: {0: rate(rows[s], m)} for s, _ in SETUPS}
        bars(ax, [0], data, width=0.28, label_size=10)
        ax.set_xticks([])
        ax.set_title(title, fontsize=10, color=INK)
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="lower center", ncol=3, frameon=False)
    fig.suptitle("Llama-3.2-3B on the held-out evaluation (2,880 tasks per setup, 95% intervals)",
                 fontsize=12, color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, out / "1_headline")

    # 2. leak rate by attack family
    fig, ax = plt.subplots(figsize=(12, 4.2))
    style(ax)
    data = {s: {i: rate([r for r in rows[s] if r["family"] == f], leak) for i, f in enumerate(FAMILIES)}
            for s, _ in SETUPS}
    bars(ax, list(range(len(FAMILIES))), data)
    ax.set_xticks(range(len(FAMILIES)))
    ax.set_xticklabels([f.replace("_", "\n") + ("\n(held out)" if f in HELD_OUT else "") for f in FAMILIES])
    ax.set_ylabel("Leak rate, restricted requests")
    ax.set_title("Leak rate by attack family (n = 120 per bar)", loc="left", color=INK)
    ax.legend(frameon=False, ncol=3, loc="upper right")
    fig.tight_layout()
    save(fig, out / "2_leak_by_family")

    # 3. utility by tier
    fig, ax = plt.subplots(figsize=(7, 4))
    style(ax)
    data = {s: {i: rate([r for r in rows[s] if r["item_tier"] == t], disclosed) for i, t in enumerate(TIERS)}
            for s, _ in SETUPS}
    bars(ax, list(range(len(TIERS))), data)
    ax.set_xticks(range(len(TIERS)))
    ax.set_xticklabels(TIERS)
    ax.set_ylabel("Full disclosure to authorized requesters")
    ax.set_title("Utility by sensitivity tier", loc="left", color=INK)
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.1))
    fig.tight_layout()
    save(fig, out / "3_utility_by_tier")

    # 4. trade-off: leak vs utility, one point per setup
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s, name in SETUPS:
        lk, ut = rate(rows[s], leak), rate(rows[s], disclosed)
        ax.errorbar(lk[0], ut[0], xerr=[[max(0, lk[0] - lk[1])], [max(0, lk[2] - lk[0])]], yerr=[[max(0, ut[0] - ut[1])], [max(0, ut[2] - ut[0])]],
                    fmt="o", ms=10, color=COLORS[s], ecolor=INK2, elinewidth=0.9, mec=SURFACE, mew=2)
        ax.annotate(name, (lk[0], ut[0]), xytext={"a": (-30, -22), "b": (-40, 10), "c": (10, -14)}[s], textcoords="offset points",
                    fontsize=9, color=INK)
    ax.set_xlim(-5, 100)
    ax.set_ylim(0, 105)
    ax.set_xlabel("Leak rate (restricted requests)  →  worse")
    ax.set_ylabel("Disclosure to authorized  →  better")
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.set_title("Security vs utility (top left is best)", loc="left", color=INK)
    fig.tight_layout()
    save(fig, out / "4_tradeoff")
    print(f"wrote {out}")


def save(fig, stem):
    fig.savefig(f"{stem}.png", dpi=200)
    fig.savefig(f"{stem}.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/eval_llama_run1")
