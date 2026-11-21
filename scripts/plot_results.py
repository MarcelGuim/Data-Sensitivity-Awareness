"""Figures for the report and slides from the scored.jsonl files of one evaluation run.

  python3 scripts/plot_results.py results/eval_run1          # Qwen
  python3 scripts/plot_results.py results/eval_llama_run1    # Llama (model found from the folder names)

Writes PNG (slides) and PDF (report) into <run>/figures/. Needs matplotlib.
(c)+policy is left out of the figures: its metrics equal (c) (docs/05, Results run 1).
Bars are plain rates; intervals are left out of the figures (they are in kaggle/eval/summarize.py output).
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
LEVELS = ["external", "internal_no_clearance", "internal_clearance"]
LEVEL_NAMES = {"external": "external", "internal_no_clearance": "employee,\nno clearance",
               "internal_clearance": "employee,\nclearance"}
FAMILY_NAMES = {"benign": "plain request\n(no attack)"}
MODEL_NAMES = {"Qwen3-4B-Instruct-2507": "Qwen3-4B", "Llama-3.2-3B-Instruct": "Llama-3.2-3B"}


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
    """data[setup][group] = (rate, lo, hi, n). Grouped bars with value labels (no intervals)."""
    for i, (s, name) in enumerate(SETUPS):
        xs = [g + (i - 1) * width for g in range(len(groups))]
        vals = [data[s][g] for g in groups]
        ax.bar(xs, [v[0] for v in vals], width - 0.03, color=COLORS[s], label=name,
               edgecolor=SURFACE, linewidth=1)
        for x, v in zip(xs, vals):
            ax.text(x, v[0] + 1.5, f"{v[0]:.0f}", ha="center", va="bottom", fontsize=label_size, color=INK)


def find_model(run):
    """Model id from the folder names eval_<model>_a, eval_<model>_b, ..."""
    found = sorted(d.name[len("eval_"):-len("_a")] for d in run.glob("eval_*_a") if d.is_dir())
    if len(found) != 1:
        sys.exit(f"expected one eval_<model>_a folder in {run}, found {found}")
    return found[0]


def simple_bar_chart(rows, metric, groups, labels, title, ylabel, path, figsize=(7, 4)):
    """groups: list of row filters; one bar group per filter, one bar per setup."""
    fig, ax = plt.subplots(figsize=figsize)
    style(ax)
    data = {s: {i: rate([r for r in rows[s] if g(r)], metric) for i, g in enumerate(groups)} for s, _ in SETUPS}
    bars(ax, list(range(len(groups))), data)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(labels)
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", color=INK)
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.16))
    fig.tight_layout()
    save(fig, path)


def main(run):
    run = Path(run)
    model = find_model(run)
    model_name = MODEL_NAMES.get(model, model)
    rows = {s: [json.loads(line) for line in (run / f"eval_{model}_{s}" / "scored.jsonl").open()]
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
    fig.suptitle(f"{model_name} on the held-out evaluation",
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
    ax.set_xticklabels([FAMILY_NAMES.get(f, f.replace("_", "\n")) + ("\n(held out)" if f in HELD_OUT else "")
                        for f in FAMILIES])
    ax.set_ylabel("Leak rate, restricted requests")
    ax.set_title("Leak rate by attack family", loc="left", color=INK)
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

    # 4. utility vs leak rate, one point per setup
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
        ax.plot(lk[0], ut[0], "o", ms=10, color=COLORS[s], mec=SURFACE, mew=2)
        ax.annotate(name, (lk[0], ut[0]), xytext={"a": (-30, -22), "b": (-40, 10), "c": (10, -14)}[s], textcoords="offset points",
                    fontsize=9, color=INK)
    ax.set_xlim(-5, 100)
    ax.set_ylim(0, 105)
    ax.set_xlabel("Leak rate (restricted requests)  →  worse")
    ax.set_ylabel("Disclosure to authorized  →  better")
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.set_title(f"Utility vs leak rate, {model_name} (top left is best)", loc="left", color=INK)
    fig.tight_layout()
    save(fig, out / "4_utility_vs_leak")

    # 5-7. leak rate slices. Only restricted requests count, so public records and employees
    # with clearance never appear (they may see everything they ask for).
    simple_bar_chart(rows, leak, [lambda r, t=t: r["item_tier"] == t for t in ["private", "confidential"]],
                     ["private", "confidential"],
                     "Leak rate by record tier", "Leak rate, restricted requests", out / "5_leak_by_tier",
                     figsize=(6, 4))
    simple_bar_chart(rows, leak, [lambda r, lv=lv: r["requester_level"] == lv for lv in ["external", "internal_no_clearance"]],
                     ["external", "employee, no clearance"],
                     "Leak rate by requester", "Leak rate, restricted requests", out / "6_leak_by_requester",
                     figsize=(6, 4))
    # mismatch: confidential records that look harmless (leak), public records that look sensitive (disclosure)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    conf = lambda r: r["item_tier"] == "confidential"  # noqa: E731
    pub = lambda r: r["item_tier"] == "public"  # noqa: E731
    panels = [("Confidential records: leak rate\n(lower is better)", leak, conf, "looks_less_sensitive",
               ["tag matches content", "looks harmless"]),
              ("Public records: disclosure\n(higher is better)", disclosed, pub, "looks_more_sensitive",
               ["tag matches content", "looks sensitive"])]
    for ax, (title, m, tier, label, names) in zip(axes, panels):
        style(ax)
        groups = [lambda r, t=tier: t(r) and not r.get("item_mismatch"),
                  lambda r, t=tier, lb=label: t(r) and r.get("item_mismatch") == lb]
        data = {s: {i: rate([r for r in rows[s] if g(r)], m) for i, g in enumerate(groups)} for s, _ in SETUPS}
        bars(ax, [0, 1], data)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(names)
        ax.set_title(title, fontsize=10, color=INK)
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="lower center", ncol=3, frameon=False)
    fig.suptitle("Records whose tag disagrees with how sensitive they look", fontsize=12, color=INK,
                 x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, out / "7_mismatch")

    # 8. utility by requester level
    simple_bar_chart(rows, disclosed, [lambda r, lv=lv: r["requester_level"] == lv for lv in LEVELS],
                     [LEVEL_NAMES[lv] for lv in LEVELS],
                     "Utility by requester", "Full disclosure to authorized requesters",
                     out / "8_utility_by_requester")
    print(f"wrote {out}")


def save(fig, stem):
    fig.savefig(f"{stem}.png", dpi=200)
    fig.savefig(f"{stem}.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/eval_run1")
